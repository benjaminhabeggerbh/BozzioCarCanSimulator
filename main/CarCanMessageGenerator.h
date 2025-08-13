#ifndef CAR_CAN_MESSAGE_GENERATOR_H
#define CAR_CAN_MESSAGE_GENERATOR_H

#include <vector>
#include <cstdint>
#include <functional>
#include <map>
#include "common.h"

enum class Gear {
    PARK,
    REVERSE,
    NEUTRAL,
    DRIVE
};

// Function type definitions for message generators
using SpeedMessageGenerator = std::function<void(uint8_t speed_kmh, uint8_t* data, uint8_t& dlc)>;
using GearMessageGenerator = std::function<void(Gear gear, uint8_t* data, uint8_t& dlc)>;

// Vehicle CAN configuration structure
struct VehicleCanConfig {
    uint32_t speed_msg_id;
    uint32_t gear_msg_id;
    uint32_t baud_rate;
    SpeedMessageGenerator speed_generator;
    GearMessageGenerator gear_generator;
};

class CarCanMessageGenerator {
public:
    CarCanMessageGenerator();
    
    void generateSpeedMessage(button_id_t vehicle, uint8_t speed_kmh, uint8_t* data, uint8_t& dlc);
    void generateGearMessage(button_id_t vehicle, Gear gear, uint8_t* data, uint8_t& dlc);
    std::vector<uint32_t> getRequiredMessageIds(button_id_t vehicle) const;
    uint32_t getCANBaudRate(button_id_t vehicle) const;
    bool hasSupport(button_id_t vehicle) const;

private:
    std::map<button_id_t, VehicleCanConfig> vehicle_configs;
    void initializeVehicleConfigs();

    // Common message generation functions that can be shared between vehicles
    static void generateVWSpeedMessage(float speed_factor, uint8_t speed_kmh, uint8_t* data, uint8_t& dlc);
    static void generateVWGearMessage(uint8_t* data, uint8_t& dlc, Gear gear);
};

#endif // CAR_CAN_MESSAGE_GENERATOR_H 