#ifndef SERIAL_COMMAND_HANDLER_H
#define SERIAL_COMMAND_HANDLER_H

#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "freertos/queue.h"
#include "cJSON.h"
#include "esp_log.h"
#include "esp_timer.h"
#include "common.h"
#include "BaseMessageGenerator.h"
#include <string>
#include <functional>

class CarCanController;
class CarCanGui;

/**
 * Serial Command Handler for ESP32 CAN Simulator
 * 
 * Provides JSON-based serial communication interface for:
 * - Setting vehicle type, gear, speed
 * - Getting current status
 * - Controlling CAN transmission
 * 
 * Commands are JSON objects sent over UART:
 * {"command": "set_vehicle", "vehicle": "VWT7"}
 * {"command": "set_gear", "gear": "PARK"}
 * {"command": "set_speed", "speed": 120}
 * {"command": "get_status"}
 * 
 * Responses are JSON objects:
 * {"type": "response", "status": "ok", "command": "set_vehicle", "vehicle": "VWT7"}
 * {"type": "status_update", "vehicle": "VWT7", "gear": "PARK", "speed": 120, "can_active": true}
 */
class SerialCommandHandler {
public:
    SerialCommandHandler(CarCanController& controller, CarCanGui& gui);
    ~SerialCommandHandler();
    
    /**
     * Initialize serial command handler
     * Creates background task for reading serial commands
     */
    bool initialize();
    
    /**
     * Stop serial command handler
     */
    void stop();
    
    /**
     * Send status update notification (called when controller state changes)
     */
    void notifyStatusUpdate();
    
private:
    CarCanController& controller;
    CarCanGui& gui;
    
    // FreeRTOS task handling
    TaskHandle_t serial_task_handle;
    QueueHandle_t command_queue;
    bool running;
    
    // Serial buffer
    std::string input_buffer;
    
    /**
     * Background task that reads serial input
     */
    static void serialTaskWrapper(void* params);
    void serialTask();
    
    /**
     * Process a complete JSON command
     */
    void processCommand(const std::string& command_str);
    
    /**
     * Handle individual commands
     */
    void handlePing(cJSON* json);
    void handleGetStatus(cJSON* json);
    void handleSetVehicle(cJSON* json);
    void handleSetGear(cJSON* json);
    void handleSetSpeed(cJSON* json);
    void handleSetCanActive(cJSON* json);
    void handleGetSupportedVehicles(cJSON* json);
    void handleResetSettings(cJSON* json);
    
    /**
     * Send JSON response
     */
    void sendResponse(const char* type, const char* status, const char* command = nullptr, cJSON* data = nullptr);
    void sendError(const char* message, const char* command = nullptr);
    void sendStatusUpdate();
    
    /**
     * Helper functions
     */
    const char* vehicleIdToString(button_id_t vehicle);
    button_id_t stringToVehicleId(const char* vehicle_str);
    const char* gearToString(Gear gear);
    Gear stringToGear(const char* gear_str);
    
    /**
     * Update GUI elements to reflect controller state
     */
    void updateGuiFromController();
};

#endif // SERIAL_COMMAND_HANDLER_H
