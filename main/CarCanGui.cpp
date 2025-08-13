#include "CarCanGui.h"
#include "CarCanController.h"
#include "common.h"
#include "lvgl.h"
#include <string>

CarCanGui* self = nullptr;
    
CarCanGui::CarCanGui(CarCanController& controller) : controller(controller) {
    self = this;
    button_map = controller.getButtonMap();
}

void CarCanGui::createGui() {
    lv_obj_t *scr = lv_scr_act();  // Get the current active screen

    container = lv_obj_create(scr);
    lv_obj_set_size(container, 800, 400);
    lv_obj_center(container);

    createVehicleSelector();
    createSpeedControl();
    createGearControl();
}

void CarCanGui::createVehicleSelector() {
    // Create the dropdown
    dropdown = lv_dropdown_create(container);
    lv_obj_set_size(dropdown, 300, 50);
    lv_obj_align(dropdown, LV_ALIGN_TOP_MID, 0, 20);
    lv_obj_add_event_cb(dropdown, dropdown_event_handler, LV_EVENT_VALUE_CHANGED, NULL);

    // Build options string from button map
    std::string options;
    for (const auto& item : button_map) {
        if (!options.empty()) {
            options += "\n";
        }
        options += item.second.label;
    }
    lv_dropdown_set_options(dropdown, options.c_str());

    // Set initial selection to match controller's current vehicle
    button_id_t current = controller.getCurrentVehicle();
    int index = 0;
    for (const auto& item : button_map) {
        if (item.first == current) {
            lv_dropdown_set_selected(dropdown, index);
            break;
        }
        index++;
    }
}

void CarCanGui::createSpeedControl() {
    // Create speed slider
    speed_slider = lv_slider_create(container);
    lv_obj_set_size(speed_slider, 300, 20);
    lv_obj_align(speed_slider, LV_ALIGN_LEFT_MID, 50, 0);
    lv_slider_set_range(speed_slider, 0, 250);
    lv_obj_add_event_cb(speed_slider, speed_event_handler, LV_EVENT_VALUE_CHANGED, NULL);

    // Create speed label
    speed_label = lv_label_create(container);
    lv_label_set_text(speed_label, "0 km/h");
    lv_obj_align_to(speed_label, speed_slider, LV_ALIGN_OUT_BOTTOM_MID, 0, 10);
}

void CarCanGui::createGearControl() {
    static const char* gear_labels[] = {"P", "R", "N", "D"};
    static lv_style_t style_pr;
    lv_style_init(&style_pr);
    lv_style_set_bg_color(&style_pr, lv_palette_main(LV_PALETTE_GREEN));

    // Create gear selector buttons
    for (int i = 0; i < 4; i++) {
        gear_buttons[i] = lv_btn_create(container);
        lv_obj_add_style(gear_buttons[i], &style_pr, LV_STATE_CHECKED);
        lv_obj_add_flag(gear_buttons[i], LV_OBJ_FLAG_CHECKABLE);
        lv_obj_set_size(gear_buttons[i], 60, 40);
        lv_obj_align(gear_buttons[i], LV_ALIGN_RIGHT_MID, -50 - (i * 70), 0);
        lv_obj_add_event_cb(gear_buttons[i], gear_event_handler, LV_EVENT_CLICKED, (void*)(intptr_t)i);

        lv_obj_t *label = lv_label_create(gear_buttons[i]);
        lv_label_set_text(label, gear_labels[i]);
        lv_obj_center(label);
    }

    // Set initial gear state
    lv_obj_add_state(gear_buttons[0], LV_STATE_CHECKED); // P is default
}

void CarCanGui::dropdown_event_handler(lv_event_t * e) {
    lv_obj_t * dropdown = lv_event_get_target(e);
    uint16_t selected = lv_dropdown_get_selected(dropdown);
    
    if (self) {
        uint16_t index = 0;
        for (const auto& item : self->button_map) {
            if (index == selected) {
                self->controller.btnCallback(item.first);
                break;
            }
            index++;
        }
    }
}

void CarCanGui::speed_event_handler(lv_event_t * e) {
    lv_obj_t * slider = lv_event_get_target(e);
    int32_t value = lv_slider_get_value(slider);
    
    if (self) {
        self->controller.setSpeed(value);
        char buf[16];
        snprintf(buf, sizeof(buf), "%ld km/h", value);
        lv_label_set_text(self->speed_label, buf);
    }
}

void CarCanGui::gear_event_handler(lv_event_t * e) {
    lv_obj_t * btn = lv_event_get_target(e);
    intptr_t gear_index = (intptr_t)lv_event_get_user_data(e);
    
    if (self) {
        // Uncheck all other buttons
        for (int i = 0; i < 4; i++) {
            if (self->gear_buttons[i] != btn) {
                lv_obj_clear_state(self->gear_buttons[i], LV_STATE_CHECKED);
            }
        }
        
        // Ensure the clicked button stays checked
        lv_obj_add_state(btn, LV_STATE_CHECKED);
        
        // Update controller
        self->controller.setGear(static_cast<Gear>(gear_index));
    }
} 