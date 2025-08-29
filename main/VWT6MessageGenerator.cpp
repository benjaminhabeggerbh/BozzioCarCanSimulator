#include "VWT6MessageGenerator.h"
#include "esp_log.h"
#include <cstring>

#define TAG "VWT6Gen"

void VWT6MessageGenerator::generateSpeedMessage(uint8_t speed_kmh, uint8_t* data, uint8_t& dlc) {
    dlc = 8;  // VW T6 uses 8-byte messages
    clearDataBuffer(data, dlc);  // Initialize all bytes to 0
    
    // Convert speed using the real T6 factor (0.005)
    uint16_t speed_value = static_cast<uint16_t>(speed_kmh / SPEED_FACTOR);
    
    // Pack speed value into the message (VW T6 format - bytes 2-3, little endian)
    data[2] = speed_value & 0xFF;        // Low byte
    data[3] = (speed_value >> 8) & 0xFF; // High byte
    
    ESP_LOGI(TAG, "T6 Speed DEBUG: %d km/h -> raw_value: %d -> data[2]=0x%02X, data[3]=0x%02X", 
             speed_kmh, speed_value, data[2], data[3]);
    ESP_LOGI(TAG, "T6 Speed FULL: [%02X %02X %02X %02X %02X %02X %02X %02X]", 
             data[0], data[1], data[2], data[3], data[4], data[5], data[6], data[7]);
}

void VWT6MessageGenerator::generateGearMessage(Gear gear, uint8_t* data, uint8_t& dlc) {
    dlc = 8;  // VW T6 uses 8-byte messages
    clearDataBuffer(data, dlc);  // Initialize all bytes to 0
    
    // Map our gear enum to real VW T6 gear values (from parser implementation)
    uint8_t gear_value;
    switch (gear) {
        case Gear::PARK:     gear_value = 0x80; break; // Real T6 Park value
        case Gear::REVERSE:  gear_value = 0x77; break; // Real T6 Reverse value (engine on)
        case Gear::NEUTRAL:  gear_value = 0x60; break; // Real T6 Neutral value
        case Gear::DRIVE:    gear_value = 0x50; break; // Real T6 Drive value
        default:            gear_value = 0x80; break; // Default to PARK
    }
    
    // Set gear value in byte 1 (VW T6 format - from parser)
    data[1] = gear_value;
    
    ESP_LOGI(TAG, "T6 Gear DEBUG: %d -> gear_value: 0x%02X -> data[1]=0x%02X", 
             static_cast<int>(gear), gear_value, data[1]);
    ESP_LOGI(TAG, "T6 Gear FULL: [%02X %02X %02X %02X %02X %02X %02X %02X]", 
             data[0], data[1], data[2], data[3], data[4], data[5], data[6], data[7]);
}

std::vector<uint32_t> VWT6MessageGenerator::getRequiredMessageIds() const {
    return {GEAR_MSG_ID, SPEED_MSG_ID};
}

uint32_t VWT6MessageGenerator::getCANBaudRate() const {
    return CAN_BAUDRATE;
}

button_id_t VWT6MessageGenerator::getVehicleType() const {
    return VW_T6;
}

const char* VWT6MessageGenerator::getVehicleName() const {
    return "VW T6";
}
