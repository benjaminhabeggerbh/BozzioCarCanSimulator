#include "SerialCommandHandler.h"
#include "CarCanController.h"
#include "CarCanGui.h"
#include "common.h"
#include "esp_system.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include <cstring>
#include <iostream>

#define TAG "SerialCmd"
#define BUFFER_SIZE 1024
#define COMMAND_QUEUE_SIZE 10

SerialCommandHandler::SerialCommandHandler(CarCanController& controller, CarCanGui& gui)
    : controller(controller), gui(gui), serial_task_handle(nullptr), command_queue(nullptr), running(false) {
}

SerialCommandHandler::~SerialCommandHandler() {
    stop();
}

bool SerialCommandHandler::initialize() {
    ESP_LOGI(TAG, "Initializing serial command handler...");
    
    // Create command queue
    command_queue = xQueueCreate(COMMAND_QUEUE_SIZE, sizeof(char*));
    if (!command_queue) {
        ESP_LOGE(TAG, "Failed to create command queue");
        return false;
    }
    
    // Create background task
    running = true;
    BaseType_t result = xTaskCreate(
        serialTaskWrapper,
        "serial_cmd_task",
        8192,  // Increased stack size
        this,
        3,  // Lower priority to avoid conflicts
        &serial_task_handle
    );
    
    if (result != pdPASS) {
        ESP_LOGE(TAG, "Failed to create serial task");
        running = false;
        vQueueDelete(command_queue);
        command_queue = nullptr;
        return false;
    }
    
    ESP_LOGI(TAG, "Serial command handler initialized successfully");
    
    // Send initial status
    sendStatusUpdate();
    
    return true;
}

void SerialCommandHandler::stop() {
    if (running) {
        running = false;
        
        if (serial_task_handle) {
            vTaskDelete(serial_task_handle);
            serial_task_handle = nullptr;
        }
        
        if (command_queue) {
            vQueueDelete(command_queue);
            command_queue = nullptr;
        }
        
        ESP_LOGI(TAG, "Serial command handler stopped");
    }
}

void SerialCommandHandler::serialTaskWrapper(void* params) {
    SerialCommandHandler* handler = static_cast<SerialCommandHandler*>(params);
    handler->serialTask();
    vTaskDelete(nullptr);
}

void SerialCommandHandler::serialTask() {
    ESP_LOGI(TAG, "Serial command task started");
    
    while (running) {
        // Read character by character from stdin
        int c = getchar();
        
        if (c != EOF && c != -1) {
            char ch = (char)c;
            
            // Add character to buffer
            if (ch == '\n' || ch == '\r') {
                // Process complete command
                if (!input_buffer.empty()) {
                    processCommand(input_buffer);
                    input_buffer.clear();
                }
            } else if (ch >= 32 && ch <= 126) {  // Printable ASCII characters
                input_buffer += ch;
                
                // Prevent buffer overflow
                if (input_buffer.length() > BUFFER_SIZE - 1) {
                    ESP_LOGW(TAG, "Input buffer overflow, clearing");
                    input_buffer.clear();
                }
            }
        }
        
        // Small delay to prevent busy waiting
        vTaskDelay(pdMS_TO_TICKS(50));  // Increased delay to reduce CPU usage
    }
    
    ESP_LOGI(TAG, "Serial command task stopped");
}

void SerialCommandHandler::processCommand(const std::string& command_str) {
    ESP_LOGI(TAG, "Processing command: %s", command_str.c_str());
    
    // Parse JSON
    cJSON* json = cJSON_Parse(command_str.c_str());
    if (!json) {
        sendError("Invalid JSON format");
        return;
    }
    
    // Get command type
    cJSON* cmd_item = cJSON_GetObjectItem(json, "command");
    if (!cmd_item || !cJSON_IsString(cmd_item)) {
        sendError("Missing or invalid 'command' field");
        cJSON_Delete(json);
        return;
    }
    
    const char* command = cmd_item->valuestring;
    
    // Dispatch to appropriate handler
    if (strcmp(command, "ping") == 0) {
        handlePing(json);
    } else if (strcmp(command, "get_status") == 0) {
        handleGetStatus(json);
    } else if (strcmp(command, "set_vehicle") == 0) {
        handleSetVehicle(json);
    } else if (strcmp(command, "set_gear") == 0) {
        handleSetGear(json);
    } else if (strcmp(command, "set_speed") == 0) {
        handleSetSpeed(json);
    } else if (strcmp(command, "set_can_active") == 0) {
        handleSetCanActive(json);
    } else if (strcmp(command, "get_supported_vehicles") == 0) {
        handleGetSupportedVehicles(json);
    } else if (strcmp(command, "reset_settings") == 0) {
        handleResetSettings(json);
    } else {
        sendError("Unknown command", command);
    }
    
    cJSON_Delete(json);
}

void SerialCommandHandler::handlePing(cJSON* json) {
    sendResponse("response", "ok", "ping");
}

void SerialCommandHandler::handleGetStatus(cJSON* json) {
    cJSON* data = cJSON_CreateObject();
    
    // Add current status
    cJSON_AddStringToObject(data, "vehicle", vehicleIdToString(controller.getCurrentVehicle()));
    cJSON_AddStringToObject(data, "gear", gearToString(controller.getGear()));
    cJSON_AddNumberToObject(data, "speed", controller.getSpeed());
    cJSON_AddBoolToObject(data, "can_active", true);  // Assume CAN is always active for now
    cJSON_AddNumberToObject(data, "uptime", esp_timer_get_time() / 1000000);  // Uptime in seconds
    cJSON_AddStringToObject(data, "firmware_version", "1.0.0");
    
    sendResponse("response", "ok", "get_status", data);
}

void SerialCommandHandler::handleSetVehicle(cJSON* json) {
    cJSON* vehicle_item = cJSON_GetObjectItem(json, "vehicle");
    if (!vehicle_item || !cJSON_IsString(vehicle_item)) {
        sendError("Missing or invalid 'vehicle' field", "set_vehicle");
        return;
    }
    
    button_id_t vehicle_id = stringToVehicleId(vehicle_item->valuestring);
    if (vehicle_id == 0) {  // Invalid vehicle (using 0 as invalid marker)
        sendError("Unsupported vehicle type", "set_vehicle");
        return;
    }
    
    // Update controller
    controller.setCurrentVehicle(vehicle_id);
    
    // Update GUI
    updateGuiFromController();
    
    // Send response
    cJSON* data = cJSON_CreateObject();
    cJSON_AddStringToObject(data, "vehicle", vehicleIdToString(vehicle_id));
    sendResponse("response", "ok", "set_vehicle", data);
    
    // Send status update
    notifyStatusUpdate();
}

void SerialCommandHandler::handleSetGear(cJSON* json) {
    cJSON* gear_item = cJSON_GetObjectItem(json, "gear");
    if (!gear_item || !cJSON_IsString(gear_item)) {
        sendError("Missing or invalid 'gear' field", "set_gear");
        return;
    }
    
    Gear gear = stringToGear(gear_item->valuestring);
    if (gear == Gear::PARK && strcmp(gear_item->valuestring, "PARK") != 0) {  // Invalid gear
        sendError("Invalid gear value", "set_gear");
        return;
    }
    
    // Update controller
    controller.setGear(gear);
    
    // Update GUI
    updateGuiFromController();
    
    // Send response
    cJSON* data = cJSON_CreateObject();
    cJSON_AddStringToObject(data, "gear", gearToString(gear));
    sendResponse("response", "ok", "set_gear", data);
    
    // Send status update
    notifyStatusUpdate();
}

void SerialCommandHandler::handleSetSpeed(cJSON* json) {
    cJSON* speed_item = cJSON_GetObjectItem(json, "speed");
    if (!speed_item || !cJSON_IsNumber(speed_item)) {
        sendError("Missing or invalid 'speed' field", "set_speed");
        return;
    }
    
    int speed = speed_item->valueint;
    if (speed < 0 || speed > 250) {
        sendError("Speed must be between 0 and 250 km/h", "set_speed");
        return;
    }
    
    // Update controller
    controller.setSpeed(speed);
    
    // Update GUI
    updateGuiFromController();
    
    // Send response
    cJSON* data = cJSON_CreateObject();
    cJSON_AddNumberToObject(data, "speed", speed);
    sendResponse("response", "ok", "set_speed", data);
    
    // Send status update
    notifyStatusUpdate();
}

void SerialCommandHandler::handleSetCanActive(cJSON* json) {
    cJSON* active_item = cJSON_GetObjectItem(json, "active");
    if (!active_item || !cJSON_IsBool(active_item)) {
        sendError("Missing or invalid 'active' field", "set_can_active");
        return;
    }
    
    bool active = cJSON_IsTrue(active_item);
    
    // TODO: Implement CAN enable/disable functionality in controller
    // For now, just acknowledge the command
    
    // Send response
    cJSON* data = cJSON_CreateObject();
    cJSON_AddBoolToObject(data, "active", active);
    sendResponse("response", "ok", "set_can_active", data);
}

void SerialCommandHandler::handleGetSupportedVehicles(cJSON* json) {
    cJSON* vehicles = cJSON_CreateArray();
    
    // Get button map and add all supported vehicles
    ButtonMap button_map = controller.getButtonMap();
    for (const auto& item : button_map) {
        cJSON_AddItemToArray(vehicles, cJSON_CreateString(vehicleIdToString(item.first)));
    }
    
    cJSON* data = cJSON_CreateObject();
    cJSON_AddItemToObject(data, "vehicles", vehicles);
    
    sendResponse("response", "ok", "get_supported_vehicles", data);
}

void SerialCommandHandler::handleResetSettings(cJSON* json) {
    // Reset to default values
    controller.setCurrentVehicle(VW_T6);  // Default vehicle
    controller.setGear(Gear::PARK);       // Default gear
    controller.setSpeed(0);               // Default speed
    
    // Update GUI
    updateGuiFromController();
    
    sendResponse("response", "ok", "reset_settings");
    
    // Send status update
    notifyStatusUpdate();
}

void SerialCommandHandler::sendResponse(const char* type, const char* status, const char* command, cJSON* data) {
    cJSON* response = cJSON_CreateObject();
    
    cJSON_AddStringToObject(response, "type", type);
    cJSON_AddStringToObject(response, "status", status);
    
    if (command) {
        cJSON_AddStringToObject(response, "command", command);
    }
    
    cJSON_AddNumberToObject(response, "timestamp", esp_timer_get_time() / 1000);
    
    if (data) {
        // Add all items from data object to response
        cJSON* item = data->child;
        while (item) {
            cJSON* next = item->next;  // Store next before moving
            cJSON_DetachItemFromObject(data, item->string);
            cJSON_AddItemToObject(response, item->string, item);
            item = next;
        }
    }
    
    char* json_string = cJSON_Print(response);
    if (json_string) {
        printf("%s\n", json_string);
        fflush(stdout);  // Ensure immediate output
        free(json_string);
    }
    
    cJSON_Delete(response);
    if (data) {
        cJSON_Delete(data);
    }
}

void SerialCommandHandler::sendError(const char* message, const char* command) {
    cJSON* data = cJSON_CreateObject();
    cJSON_AddStringToObject(data, "message", message);
    sendResponse("error", "error", command, data);
}

void SerialCommandHandler::sendStatusUpdate() {
    cJSON* response = cJSON_CreateObject();
    
    cJSON_AddStringToObject(response, "type", "status_update");
    cJSON_AddStringToObject(response, "vehicle", vehicleIdToString(controller.getCurrentVehicle()));
    cJSON_AddStringToObject(response, "gear", gearToString(controller.getGear()));
    cJSON_AddNumberToObject(response, "speed", controller.getSpeed());
    cJSON_AddBoolToObject(response, "can_active", true);
    cJSON_AddNumberToObject(response, "uptime", esp_timer_get_time() / 1000000);
    cJSON_AddStringToObject(response, "firmware_version", "1.0.0");
    cJSON_AddNumberToObject(response, "timestamp", esp_timer_get_time() / 1000);
    
    char* json_string = cJSON_Print(response);
    if (json_string) {
        printf("%s\n", json_string);
        fflush(stdout);  // Ensure immediate output
        free(json_string);
    }
    
    cJSON_Delete(response);
}

void SerialCommandHandler::notifyStatusUpdate() {
    sendStatusUpdate();
}

// Helper functions
const char* SerialCommandHandler::vehicleIdToString(button_id_t vehicle) {
    switch (vehicle) {
        case VW_T7: return "VWT7";
        case VW_T6: return "VWT6";
        case VW_T61: return "VWT61";
        case VW_T5: return "VWT5";
        case MB_SPRINTER: return "MB_SPRINTER";
        case MB_SPRINTER_2023: return "MB_SPRINTER_2023";
        case JEEP_RENEGADE: return "JEEP_RENEGADE";
        case JEEP_RENEGADE_MHEV: return "JEEP_RENEGADE_MHEV";
        case MB_VIANO: return "MB_VIANO";
        default: return "UNKNOWN";
    }
}

button_id_t SerialCommandHandler::stringToVehicleId(const char* vehicle_str) {
    if (strcmp(vehicle_str, "VWT7") == 0) return VW_T7;
    if (strcmp(vehicle_str, "VWT6") == 0) return VW_T6;
    if (strcmp(vehicle_str, "VWT61") == 0) return VW_T61;
    if (strcmp(vehicle_str, "VWT5") == 0) return VW_T5;
    if (strcmp(vehicle_str, "MB_SPRINTER") == 0) return MB_SPRINTER;
    if (strcmp(vehicle_str, "MB_SPRINTER_2023") == 0) return MB_SPRINTER_2023;
    if (strcmp(vehicle_str, "JEEP_RENEGADE") == 0) return JEEP_RENEGADE;
    if (strcmp(vehicle_str, "JEEP_RENEGADE_MHEV") == 0) return JEEP_RENEGADE_MHEV;
    if (strcmp(vehicle_str, "MB_VIANO") == 0) return MB_VIANO;
    return static_cast<button_id_t>(0);  // Invalid (using 0 as invalid marker)
}

const char* SerialCommandHandler::gearToString(Gear gear) {
    switch (gear) {
        case Gear::PARK: return "PARK";
        case Gear::REVERSE: return "REVERSE";
        case Gear::NEUTRAL: return "NEUTRAL";
        case Gear::DRIVE: return "DRIVE";
        default: return "UNKNOWN";
    }
}

Gear SerialCommandHandler::stringToGear(const char* gear_str) {
    if (strcmp(gear_str, "PARK") == 0) return Gear::PARK;
    if (strcmp(gear_str, "REVERSE") == 0) return Gear::REVERSE;
    if (strcmp(gear_str, "NEUTRAL") == 0) return Gear::NEUTRAL;
    if (strcmp(gear_str, "DRIVE") == 0) return Gear::DRIVE;
    return Gear::PARK;  // Default to park for invalid input
}

void SerialCommandHandler::updateGuiFromController() {
    // Update all GUI elements to reflect current controller state
    gui.updateAllElements();
    ESP_LOGI(TAG, "GUI updated from controller state");
}
