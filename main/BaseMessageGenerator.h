#ifndef BASE_MESSAGE_GENERATOR_H
#define BASE_MESSAGE_GENERATOR_H

#include <vector>
#include <cstdint>
#include <cstring>
#include "common.h"

enum class Gear {
    PARK,
    REVERSE,
    NEUTRAL,
    DRIVE
};

/**
 * Abstract base class for all vehicle CAN message generators.
 * Each vehicle type should inherit from this class and implement
 * the pure virtual methods to generate vehicle-specific messages.
 */
class BaseMessageGenerator {
public:
    virtual ~BaseMessageGenerator() = default;
    
    /**
     * Generate a speed message for this vehicle type
     * @param speed_kmh Speed in km/h
     * @param data Output buffer for CAN message data (8 bytes)
     * @param dlc Output data length code
     */
    virtual void generateSpeedMessage(uint8_t speed_kmh, uint8_t* data, uint8_t& dlc) = 0;
    
    /**
     * Generate a gear message for this vehicle type
     * @param gear Current gear position
     * @param data Output buffer for CAN message data (8 bytes)
     * @param dlc Output data length code
     */
    virtual void generateGearMessage(Gear gear, uint8_t* data, uint8_t& dlc) = 0;
    
    /**
     * Get the required CAN message IDs for this vehicle
     * @return Vector of message IDs (typically [gear_id, speed_id])
     */
    virtual std::vector<uint32_t> getRequiredMessageIds() const = 0;
    
    /**
     * Get the CAN bus baud rate for this vehicle
     * @return Baud rate in bits per second
     */
    virtual uint32_t getCANBaudRate() const = 0;
    
    /**
     * Get the vehicle type this generator supports
     * @return Vehicle button ID
     */
    virtual button_id_t getVehicleType() const = 0;
    
    /**
     * Get a human-readable name for this vehicle
     * @return Vehicle name string
     */
    virtual const char* getVehicleName() const = 0;

protected:
    /**
     * Helper method to initialize all bytes in data buffer to zero
     */
    static void clearDataBuffer(uint8_t* data, uint8_t size = 8) {
        memset(data, 0, size);
    }
};

#endif // BASE_MESSAGE_GENERATOR_H
