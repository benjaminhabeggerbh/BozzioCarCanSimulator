#include "VWT6MessageGenerator.h"
#include "esp_log.h"
#include <cstring>

#define TAG "VWT6Gen"

void VWT6MessageGenerator::generateSpeedMessage(uint8_t speed_kmh, uint8_t* data, uint8_t& dlc) {
    dlc = 8;  // VW T6 uses 8-byte messages
    clearDataBuffer(data, dlc);  // Initialize all bytes to 0
    
    // Convert speed using the factor (0.01)
    uint16_t speed_value = static_cast<uint16_t>(speed_kmh / SPEED_FACTOR);
    
    // Pack speed value into the message (VW T6 format - same as T7)
    data[4] = speed_value & 0xFF;
    data[5] = (speed_value >> 8) & 0xFF;
    
    ESP_LOGI(TAG, "Generated VW T6 speed message (%d km/h): %02X %02X %02X %02X %02X %02X %02X %02X", 
             speed_kmh, data[0], data[1], data[2], data[3], data[4], data[5], data[6], data[7]);
}

void VWT6MessageGenerator::generateGearMessage(Gear gear, uint8_t* data, uint8_t& dlc) {
    dlc = 8;  // VW T6 uses 8-byte messages
    clearDataBuffer(data, dlc);  // Initialize all bytes to 0
    
    // Map our gear enum to VW T6's gear values (same as T7)
    uint8_t gear_value;
    switch (gear) {
        case Gear::PARK:     gear_value = 0x05; break;
        case Gear::REVERSE:  gear_value = 0x04; break;
        case Gear::NEUTRAL:  gear_value = 0x03; break;
        case Gear::DRIVE:    gear_value = 0x02; break;
        default:            gear_value = 0x05; break; // Default to PARK
    }
    
    // Set gear value in byte 5 (VW T6 format)
    data[5] = gear_value;
    
    ESP_LOGI(TAG, "Generated VW T6 gear message: %02X %02X %02X %02X %02X %02X %02X %02X", 
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
