#include "VWT7MessageGenerator.h"
#include "esp_log.h"
#include <cstring>

#define TAG "VWT7Gen"

void VWT7MessageGenerator::generateSpeedMessage(uint8_t speed_kmh, uint8_t* data, uint8_t& dlc) {
    dlc = 8;  // VW T7 uses 8-byte messages
    clearDataBuffer(data, dlc);  // Initialize all bytes to 0
    
    // Convert speed using the factor (0.01)
    uint16_t speed_value = static_cast<uint16_t>(speed_kmh / SPEED_FACTOR);
    
    // Pack speed value into the message (VW T7 format - bytes 4-5)
    data[4] = speed_value & 0xFF;
    data[5] = (speed_value >> 8) & 0xFF;
    
    // Debug output removed for cleaner interface
}

void VWT7MessageGenerator::generateGearMessage(Gear gear, uint8_t* data, uint8_t& dlc) {
    dlc = 8;  // VW T7 uses 8-byte messages
    clearDataBuffer(data, dlc);  // Initialize all bytes to 0
    
    // Map our gear enum to VW T7's gear values
    uint8_t gear_value;
    switch (gear) {
        case Gear::PARK:     gear_value = 0x05; break;
        case Gear::REVERSE:  gear_value = 0x04; break;
        case Gear::NEUTRAL:  gear_value = 0x03; break;
        case Gear::DRIVE:    gear_value = 0x02; break;
        default:            gear_value = 0x05; break; // Default to PARK
    }
    
    // Set gear value in byte 5 (VW T7 format)
    data[5] = gear_value;
    
        // Debug output removed for cleaner interface
}

std::vector<uint32_t> VWT7MessageGenerator::getRequiredMessageIds() const {
    return {GEAR_MSG_ID, SPEED_MSG_ID};
}

uint32_t VWT7MessageGenerator::getCANBaudRate() const {
    return CAN_BAUDRATE;
}

button_id_t VWT7MessageGenerator::getVehicleType() const {
    return VW_T7;
}

const char* VWT7MessageGenerator::getVehicleName() const {
    return "VW T7";
} 