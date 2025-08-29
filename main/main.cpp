#include "esp_log.h"
extern "C" {
#include "waveshare_rgb_lcd_port.h"
}
#include "lvgl_port.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "CarCanController.h"
#include "CarCanGui.h"
#include "SerialCommandHandler.h"

#define TAG "APP_MAIN"

extern "C" void app_main()
{
    waveshare_esp32_s3_rgb_lcd_init(); // Initialize the Waveshare ESP32-S3 RGB LCD 
    
    ESP_LOGI(TAG, "Starting application...");

    // Create main components
    CarCanController controller;
    CarCanGui gui(controller);
    gui.createGui();
    
    // Initialize serial command interface
    SerialCommandHandler serialHandler(controller, gui);
    if (serialHandler.initialize()) {
        ESP_LOGI(TAG, "Serial command interface ready");
    } else {
        ESP_LOGE(TAG, "Failed to initialize serial command interface");
    }
    
    // Start CAN communication
    controller.startCan();

    ESP_LOGI(TAG, "ESP32 CAN Simulator ready!");
    ESP_LOGI(TAG, "Send JSON commands via serial to control the simulator");
    
    while(1){
        vTaskDelay(1);
    }
}
