#ifndef VWT7_MESSAGE_GENERATOR_H
#define VWT7_MESSAGE_GENERATOR_H

#include "BaseMessageGenerator.h"

/**
 * CAN message generator for Volkswagen T7 vehicles
 */
class VWT7MessageGenerator : public BaseMessageGenerator {
public:
    VWT7MessageGenerator() = default;
    ~VWT7MessageGenerator() override = default;
    
    void generateSpeedMessage(uint8_t speed_kmh, uint8_t* data, uint8_t& dlc) override;
    void generateGearMessage(Gear gear, uint8_t* data, uint8_t& dlc) override;
    std::vector<uint32_t> getRequiredMessageIds() const override;
    uint32_t getCANBaudRate() const override;
    button_id_t getVehicleType() const override;
    const char* getVehicleName() const override;

private:
    // VW T7 specific constants
    static constexpr uint32_t SPEED_MSG_ID = 0x0FD;
    static constexpr uint32_t GEAR_MSG_ID = 0x3DC;
    static constexpr uint32_t CAN_BAUDRATE = 500000;
    static constexpr float SPEED_FACTOR = 0.01f;
};

#endif // VWT7_MESSAGE_GENERATOR_H
