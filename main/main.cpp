#include "esp_log.h"
extern "C" {
#include "waveshare_rgb_lcd_port.h"
}
#include "lvgl_port.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "CarCanController.h"
#include "CarCanGui.h"

#define TAG "APP_MAIN"

extern "C" void app_main()
{
    waveshare_esp32_s3_rgb_lcd_init(); // Initialize the Waveshare ESP32-S3 RGB LCD 
    
    ESP_LOGI(TAG, "Starting application...");

    CarCanController controller;
    CarCanGui gui(controller);
    gui.createGui();
    
    controller.startCan();

    while(1){
        vTaskDelay(1);
    }
}
