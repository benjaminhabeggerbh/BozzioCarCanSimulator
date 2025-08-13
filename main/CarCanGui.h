#ifndef CAR_CAN_GUI_H
#define CAR_CAN_GUI_H

#include "lvgl.h"
#include "common.h"
#include "esp_log.h"
#include <map>

class CarCanController;
class CarCanGui {
public:
    CarCanGui(CarCanController& controller);
    void createGui();

private:
    lv_obj_t *container;
    lv_obj_t *dropdown;
    lv_obj_t *speed_slider;
    lv_obj_t *speed_label;
    lv_obj_t *gear_buttons[4];  // P, R, N, D buttons
    CarCanController& controller;
    ButtonMap button_map;
    
    void createVehicleSelector();
    void createSpeedControl();
    void createGearControl();
    
    static void dropdown_event_handler(lv_event_t * e);
    static void speed_event_handler(lv_event_t * e);
    static void gear_event_handler(lv_event_t * e);
};

void gui_main(const ButtonMap& buttons);

#endif // CAR_CAN_GUI_H 