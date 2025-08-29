#ifndef VWT6_MESSAGE_GENERATOR_H
#define VWT6_MESSAGE_GENERATOR_H

#include "BaseMessageGenerator.h"

/**
 * CAN message generator for Volkswagen T6 vehicles
 */
class VWT6MessageGenerator : public BaseMessageGenerator {
public:
    VWT6MessageGenerator() = default;
    ~VWT6MessageGenerator() override = default;
    
    void generateSpeedMessage(uint8_t speed_kmh, uint8_t* data, uint8_t& dlc) override;
    void generateGearMessage(Gear gear, uint8_t* data, uint8_t& dlc) override;
    std::vector<uint32_t> getRequiredMessageIds() const override;
    uint32_t getCANBaudRate() const override;
    button_id_t getVehicleType() const override;
    const char* getVehicleName() const override;

private:
    // VW T6 specific constants (from real parser implementation)
    static constexpr uint32_t SPEED_MSG_ID = 0x01A0;  // Real VW T6 speed CAN ID
    static constexpr uint32_t GEAR_MSG_ID = 0x0440;   // Real VW T6 gear CAN ID
    static constexpr uint32_t CAN_BAUDRATE = 500000;  // 500k baud rate
    static constexpr float SPEED_FACTOR = 0.005f;     // Real VW T6 speed factor
};

#endif // VWT6_MESSAGE_GENERATOR_H
