#ifndef CAR_CAN_CONTROLLER_H
#define CAR_CAN_CONTROLLER_H

#include <map>
#include <cstdint>
#include <memory>
#include "common.h"
#include "BaseMessageGenerator.h"
#include "MessageGeneratorFactory.h"



class CarCanController {
public:
    CarCanController();
    void btnCallback(button_id_t button);
    ButtonMap getButtonMap();
    void startCan();
    button_id_t getCurrentVehicle() const { return current_vehicle; }
    void setCurrentVehicle(button_id_t vehicle);
    
    // Speed control (0-250 km/h)
    void setSpeed(uint8_t speed_kmh);
    uint8_t getSpeed() const { return current_speed_kmh; }
    
    // Gear control
    void setGear(Gear gear);
    Gear getGear() const { return current_gear; }

    // Message generation
    bool hasMessageGenerator() const;
    void sendPeriodicMessages();
    std::shared_ptr<BaseMessageGenerator> getCurrentMessageGenerator() const;
    
private:
    ButtonMap button_map;
    button_id_t current_vehicle;
    uint8_t current_speed_kmh;
    Gear current_gear;
    
};

#endif // CAR_CAN_CONTROLLER_H 