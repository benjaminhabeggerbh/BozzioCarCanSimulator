#include "VWT7MessageGenerator.h"
#include "esp_log.h"

#define TAG "VWT7Gen"

void VWT7MessageGenerator::generateSpeedMessage(uint8_t speed_kmh, uint8_t* data, uint8_t& dlc) {
    dlc = 8;  // VW T7 uses 8-byte messages
    std::memset(data, 0, dlc);  // Initialize all bytes to 0
    
    // Convert speed using the factor (0.01)
    uint16_t speed_value = static_cast<uint16_t>(speed_kmh / SPEED_FACTOR);
    
    // Pack speed value into the message
    data[0] = speed_value & 0xFF;
    data[1] = (speed_value >> 8) & 0xFF;
    
    ESP_LOGI(TAG, "Generated speed message: %02X %02X %02X %02X %02X %02X %02X %02X", 
             data[0], data[1], data[2], data[3], data[4], data[5], data[6], data[7]);
}

void VWT7MessageGenerator::generateGearMessage(Gear gear, uint8_t* data, uint8_t& dlc) {
    dlc = 8;  // VW T7 uses 8-byte messages
    std::memset(data, 0, dlc);  // Initialize all bytes to 0
    
    // Map our gear enum to VW T7's gear values
    uint8_t gear_value;
    switch (gear) {
        case Gear::PARK:     gear_value = 0x05; break;
        case Gear::REVERSE:  gear_value = 0x04; break;
        case Gear::NEUTRAL:  gear_value = 0x03; break;
        case Gear::DRIVE:    gear_value = 0x02; break;
        default:            gear_value = 0x05; break; // Default to PARK
    }
    
    // Set gear value in byte 5 (as seen in the original code)
    data[5] = gear_value;
    
    ESP_LOGI(TAG, "Generated gear message: %02X %02X %02X %02X %02X %02X %02X %02X", 
             data[0], data[1], data[2], data[3], data[4], data[5], data[6], data[7]);
}

std::vector<uint32_t> VWT7MessageGenerator::getRequiredMessageIds() const {
    return {GEAR_MSG_ID, SPEED_MSG_ID};
}

uint32_t VWT7MessageGenerator::getCANBaudRate() const {
    return CAN_BAUDRATE;
} 