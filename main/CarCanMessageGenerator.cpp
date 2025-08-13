#include "CarCanMessageGenerator.h"
#include "esp_log.h"
#include <cstring>

#define TAG "CarCanGen"

// Common message generation functions
void CarCanMessageGenerator::generateVWSpeedMessage(float speed_factor, uint8_t speed_kmh, uint8_t* data, uint8_t& dlc) {
    dlc = 8;
    std::memset(data, 0, dlc);
    uint16_t speed_value = static_cast<uint16_t>(speed_kmh / speed_factor);
    data[4] = speed_value & 0xFF;
    data[5] = (speed_value >> 8) & 0xFF;
}

void CarCanMessageGenerator::generateVWGearMessage(uint8_t* data, uint8_t& dlc, Gear gear) {
    dlc = 8;
    std::memset(data, 0, dlc);
    uint8_t gear_value;
    switch (gear) {
        case Gear::PARK:     gear_value = 0x05; break;
        case Gear::REVERSE:  gear_value = 0x04; break;
        case Gear::NEUTRAL:  gear_value = 0x03; break;
        case Gear::DRIVE:    gear_value = 0x02; break;
        default:            gear_value = 0x05; break;
    }
    data[5] = gear_value;
}

CarCanMessageGenerator::CarCanMessageGenerator() {
    initializeVehicleConfigs();
}

void CarCanMessageGenerator::initializeVehicleConfigs() {
    // VW T7 Configuration
    vehicle_configs[VW_T7] = {
        .speed_msg_id = 0x0FD,
        .gear_msg_id = 0x3DC,
        .baud_rate = 500000,
        .speed_generator = [this](uint8_t speed, uint8_t* data, uint8_t& dlc) {
            generateVWSpeedMessage(0.01f, speed, data, dlc);
        },
        .gear_generator = [this](Gear gear, uint8_t* data, uint8_t& dlc) {
            generateVWGearMessage(data, dlc, gear);
        }
    };

    // VW T6 Configuration (similar to T7 but different message IDs)
    vehicle_configs[VW_T6] = {
        .speed_msg_id = 0x1FD,  // Example ID, replace with actual
        .gear_msg_id = 0x3DD,   // Example ID, replace with actual
        .baud_rate = 500000,
        .speed_generator = [this](uint8_t speed, uint8_t* data, uint8_t& dlc) {
            generateVWSpeedMessage(0.01f, speed, data, dlc);
        },
        .gear_generator = [this](Gear gear, uint8_t* data, uint8_t& dlc) {
            generateVWGearMessage(data, dlc, gear);
        }
    };

    // Add more vehicle configurations here...
}

void CarCanMessageGenerator::generateSpeedMessage(button_id_t vehicle, uint8_t speed_kmh, uint8_t* data, uint8_t& dlc) {
    auto it = vehicle_configs.find(vehicle);
    if (it != vehicle_configs.end()) {
        it->second.speed_generator(speed_kmh, data, dlc);
    } else {
        ESP_LOGW(TAG, "No speed message generator for vehicle %d", vehicle);
        dlc = 0;
    }
}

void CarCanMessageGenerator::generateGearMessage(button_id_t vehicle, Gear gear, uint8_t* data, uint8_t& dlc) {
    auto it = vehicle_configs.find(vehicle);
    if (it != vehicle_configs.end()) {
        it->second.gear_generator(gear, data, dlc);
    } else {
        ESP_LOGW(TAG, "No gear message generator for vehicle %d", vehicle);
        dlc = 0;
    }
}

std::vector<uint32_t> CarCanMessageGenerator::getRequiredMessageIds(button_id_t vehicle) const {
    auto it = vehicle_configs.find(vehicle);
    if (it != vehicle_configs.end()) {
        return {it->second.gear_msg_id, it->second.speed_msg_id};
    }
    return {};
}

uint32_t CarCanMessageGenerator::getCANBaudRate(button_id_t vehicle) const {
    auto it = vehicle_configs.find(vehicle);
    if (it != vehicle_configs.end()) {
        return it->second.baud_rate;
    }
    return 500000; // Default to 500kbps
}

bool CarCanMessageGenerator::hasSupport(button_id_t vehicle) const {
    return vehicle_configs.find(vehicle) != vehicle_configs.end();
} 