#include <map>
#include <cstdint>
#include <cstring>
#include "lvgl.h"
#include "driver/twai.h"
#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "CarCanController.h"
#include "MessageGeneratorFactory.h"
#include "common.h"

#define TAG "CarCan"

void twai_task(void *pvParameter);
void twai_receive_task(void *pvParameter);
void send_can_message(uint32_t message_id, uint8_t* data, uint8_t dlc);

CarCanController::CarCanController() : current_vehicle(VW_T6), current_speed_kmh(0), current_gear(Gear::PARK) {
    button_map = {
        { VW_T5,             {"VW T5"} },        
        { VW_T6,             {"VW T6"} },
        { VW_T61,            {"VW T6.1"} },
        { VW_T7,             {"VW T7"} },                
        { MB_SPRINTER,       {"M Sprinter"} },        
        { MB_SPRINTER_2023,  {"Mercedes Sprinter 2023"} },
        { JEEP_RENEGADE,     {"Jeep Renegade"} },                
        { JEEP_RENEGADE_MHEV,{"Jeep Renegade MHEV"} },
        { MB_VIANO,          {"Mercedes Viano"} }
    };
}

void CarCanController::startCan(){
    xTaskCreate(twai_task, "twai_task", 4096, this, 5, NULL);
    xTaskCreate(twai_receive_task, "TWAI_Receive", 4096, NULL, 5, NULL);    
}

void CarCanController::btnCallback(button_id_t button){
    ESP_LOGI(TAG, "Button callback %u ", button);
    setCurrentVehicle(button);
}

void CarCanController::setCurrentVehicle(button_id_t vehicle) {
    if (button_map.find(vehicle) != button_map.end()) {
        current_vehicle = vehicle;
        ESP_LOGI(TAG, "Selected vehicle: %s", button_map[vehicle].label);
        
        // Reconfigure CAN controller with new vehicle's baud rate
        reconfigureCANController();
    }
}

void CarCanController::setSpeed(uint8_t speed_kmh) {
    if (speed_kmh <= 250) {
        current_speed_kmh = speed_kmh;
        ESP_LOGI(TAG, "Speed set to: %d km/h", speed_kmh);
    }
}

void CarCanController::setGear(Gear gear) {
    current_gear = gear;
    const char* gear_names[] = {"PARK", "REVERSE", "NEUTRAL", "DRIVE"};
    ESP_LOGI(TAG, "Gear set to: %s", gear_names[static_cast<int>(gear)]);
}

ButtonMap CarCanController::getButtonMap(){
    return button_map;
}

bool CarCanController::hasMessageGenerator() const {
    return MessageGeneratorFactory::getInstance().isVehicleSupported(current_vehicle);
}

std::shared_ptr<BaseMessageGenerator> CarCanController::getCurrentMessageGenerator() const {
    return MessageGeneratorFactory::getInstance().getMessageGenerator(current_vehicle);
}

void CarCanController::reconfigureCANController() {
    ESP_LOGI(TAG, "Reconfiguring CAN controller for vehicle change...");
    
    // Stop current CAN driver
    esp_err_t stop_result = twai_stop();
    ESP_LOGI(TAG, "TWAI stop result: 0x%x", stop_result);
    
    esp_err_t uninstall_result = twai_driver_uninstall();
    ESP_LOGI(TAG, "TWAI uninstall result: 0x%x", uninstall_result);
    
    // Get new baud rate from current vehicle
    uint32_t baudrate = 500000; // Default baudrate
    if (hasMessageGenerator()) {
        auto generator = getCurrentMessageGenerator();
        if (generator) {
            baudrate = generator->getCANBaudRate();
        }
    }
    
    ESP_LOGI(TAG, "Configuring CAN for %lu baud", baudrate);
    ESP_LOGI(TAG, "*** RECONFIG MODE: NORMAL (production) ***");
    
    // Reconfigure with new baud rate
    twai_general_config_t g_config = TWAI_GENERAL_CONFIG_DEFAULT(GPIO_NUM_20, GPIO_NUM_19, TWAI_MODE_NORMAL);
    
    // Configure timing based on baudrate
    twai_timing_config_t t_config;
    if (baudrate == 500000) {
        t_config = TWAI_TIMING_CONFIG_500KBITS();
        ESP_LOGI(TAG, "Using TWAI_TIMING_CONFIG_500KBITS()");
    } else if (baudrate == 250000) {
        t_config = TWAI_TIMING_CONFIG_250KBITS();
        ESP_LOGI(TAG, "Using TWAI_TIMING_CONFIG_250KBITS()");
    } else if (baudrate == 125000) {
        t_config = TWAI_TIMING_CONFIG_125KBITS();
        ESP_LOGI(TAG, "Using TWAI_TIMING_CONFIG_125KBITS()");
    } else {
        ESP_LOGW(TAG, "Unsupported baudrate %lu, defaulting to 500kbps", baudrate);
        t_config = TWAI_TIMING_CONFIG_500KBITS();
        ESP_LOGI(TAG, "Using TWAI_TIMING_CONFIG_500KBITS() (default)");
    }
    
    twai_filter_config_t f_config = TWAI_FILTER_CONFIG_ACCEPT_ALL();

    if (twai_driver_install(&g_config, &t_config, &f_config) == ESP_OK) {
        ESP_LOGI(TAG, "TWAI driver reconfigured successfully");
        if (twai_start() == ESP_OK) {
            ESP_LOGI(TAG, "TWAI started successfully");
        } else {
            ESP_LOGE(TAG, "Failed to start TWAI");
        }
    } else {
        ESP_LOGE(TAG, "Failed to reinstall TWAI driver");
    }
}

void CarCanController::sendPeriodicMessages() {
    auto generator = getCurrentMessageGenerator();
    if (!generator) {
        ESP_LOGW(TAG, "No message generator available for vehicle %d", current_vehicle);
        return;
    }

    uint8_t data[8];
    uint8_t dlc;

    // Get message IDs for this vehicle
    auto ids = generator->getRequiredMessageIds();
    
    // Send gear message (first ID in the vector)
    if (!ids.empty()) {
        generator->generateGearMessage(current_gear, data, dlc);
        send_can_message(ids[0], data, dlc);
    }
    
    // Send speed message (second ID in the vector)
    if (ids.size() > 1) {
        generator->generateSpeedMessage(current_speed_kmh, data, dlc);
        send_can_message(ids[1], data, dlc);
    }
}

void send_can_message(uint32_t message_id, uint8_t* data, uint8_t dlc)
{
    twai_message_t message;
    message.flags = TWAI_MSG_FLAG_NONE;
    message.identifier = message_id;
    message.data_length_code = dlc;
    memcpy(message.data, data, dlc);

    esp_err_t result = twai_transmit(&message, pdMS_TO_TICKS(1000));
    if (result != ESP_OK) {
        ESP_LOGE(TAG, "Failed to send CAN message! ID=0x%03lX, Error=0x%x", message_id, result);
    } else {
        ESP_LOGD(TAG, "CAN message sent successfully: ID=0x%03lX", message_id);
    }
}

void twai_task(void *pvParameter) {
    CarCanController* controller = static_cast<CarCanController*>(pvParameter);
    
    // Configure TWAI with baudrate from current vehicle
    uint32_t baudrate = 500000; // Default baudrate
    if (controller->hasMessageGenerator()) {
        auto generator = controller->getCurrentMessageGenerator();
        if (generator) {
            baudrate = generator->getCANBaudRate();
        }
    }
    
    ESP_LOGI(TAG, "Initial CAN configuration: %lu baud", baudrate);
    ESP_LOGI(TAG, "*** INITIAL MODE: NORMAL (production) ***");
    
    twai_general_config_t g_config = TWAI_GENERAL_CONFIG_DEFAULT(GPIO_NUM_20, GPIO_NUM_19, TWAI_MODE_NORMAL);
    
    // Configure timing based on baudrate
    twai_timing_config_t t_config;
    if (baudrate == 500000) {
        t_config = TWAI_TIMING_CONFIG_500KBITS();
        ESP_LOGI(TAG, "Initial: Using TWAI_TIMING_CONFIG_500KBITS()");
    } else if (baudrate == 250000) {
        t_config = TWAI_TIMING_CONFIG_250KBITS();
        ESP_LOGI(TAG, "Initial: Using TWAI_TIMING_CONFIG_250KBITS()");
    } else if (baudrate == 125000) {
        t_config = TWAI_TIMING_CONFIG_125KBITS();
        ESP_LOGI(TAG, "Initial: Using TWAI_TIMING_CONFIG_125KBITS()");
    } else {
        ESP_LOGW(TAG, "Unsupported baudrate %lu, defaulting to 500kbps", baudrate);
        t_config = TWAI_TIMING_CONFIG_500KBITS();
        ESP_LOGI(TAG, "Initial: Using TWAI_TIMING_CONFIG_500KBITS() (default)");
    }
    
    twai_filter_config_t f_config = TWAI_FILTER_CONFIG_ACCEPT_ALL();

    if (twai_driver_install(&g_config, &t_config, &f_config) == ESP_OK) {
        ESP_LOGI(TAG, "TWAI driver installed");
    } else {
        ESP_LOGE(TAG, "Failed to install TWAI driver");
        vTaskDelete(NULL);
    }

    if (twai_start() == ESP_OK) {
        ESP_LOGI(TAG, "TWAI driver started");
    } else {
        ESP_LOGE(TAG, "Failed to start TWAI driver");
        twai_driver_uninstall();
        vTaskDelete(NULL);
    }

    while (1) {
        if (controller && controller->hasMessageGenerator()) {
            controller->sendPeriodicMessages();
        }
        vTaskDelay(pdMS_TO_TICKS(100));
    }

    twai_stop();
    twai_driver_uninstall();
    vTaskDelete(NULL);
}

void twai_receive_task(void *pvParameter) {
    twai_message_t message;
    while (1) {
        if (twai_receive(&message, pdMS_TO_TICKS(1000)) == ESP_OK) {
            // Message received, but we don't need to process it
        } else {
            // Timeout warnings removed for cleaner interface
        }
    }
} 