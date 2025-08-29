#include "MessageGeneratorFactory.h"
#include "VWT7MessageGenerator.h"
#include "VWT6MessageGenerator.h"
// Add more vehicle generators here as needed
// #include "MercedesSprinterMessageGenerator.h"
// #include "JeepRenegadeMessageGenerator.h"

#include "esp_log.h"

#define TAG "MsgGenFactory"

MessageGeneratorFactory& MessageGeneratorFactory::getInstance() {
    static MessageGeneratorFactory instance;
    return instance;
}

std::shared_ptr<BaseMessageGenerator> MessageGeneratorFactory::getMessageGenerator(button_id_t vehicle) {
    // Check if we already have a cached generator for this vehicle
    auto it = generator_cache.find(vehicle);
    if (it != generator_cache.end()) {
        return it->second;
    }
    
    // Create new generator and cache it
    auto generator = createMessageGenerator(vehicle);
    if (generator) {
        auto shared_gen = std::shared_ptr<BaseMessageGenerator>(generator.release());
        generator_cache[vehicle] = shared_gen;
        ESP_LOGI(TAG, "Created message generator for vehicle %d (%s)", 
                 vehicle, shared_gen->getVehicleName());
        return shared_gen;
    }
    
    ESP_LOGW(TAG, "No message generator available for vehicle %d", vehicle);
    return nullptr;
}

bool MessageGeneratorFactory::isVehicleSupported(button_id_t vehicle) const {
    switch (vehicle) {
        case VW_T7:
        case VW_T6:
        case VW_T61:  // You can map T6.1 to T6 generator for now
        case VW_T5:   // You can map T5 to T6 generator for now
            return true;
        // Add more supported vehicles here
        // case MB_SPRINTER:
        // case JEEP_RENEGADE:
        //     return true;
        default:
            return false;
    }
}

std::vector<button_id_t> MessageGeneratorFactory::getSupportedVehicles() const {
    return {
        VW_T7,
        VW_T6,
        VW_T61,
        VW_T5
        // Add more supported vehicles here
        // MB_SPRINTER,
        // JEEP_RENEGADE
    };
}

std::unique_ptr<BaseMessageGenerator> MessageGeneratorFactory::createMessageGenerator(button_id_t vehicle) {
    switch (vehicle) {
        case VW_T7:
            return std::make_unique<VWT7MessageGenerator>();
            
        case VW_T6:
        case VW_T61:  // T6.1 uses same protocol as T6
        case VW_T5:   // T5 uses same protocol as T6 (you can adjust if needed)
            return std::make_unique<VWT6MessageGenerator>();
            
        // Add more vehicle types here:
        // case MB_SPRINTER:
        //     return std::make_unique<MercedesSprinterMessageGenerator>();
        //     
        // case JEEP_RENEGADE:
        //     return std::make_unique<JeepRenegadeMessageGenerator>();
        
        default:
            ESP_LOGW(TAG, "Unsupported vehicle type: %d", vehicle);
            return nullptr;
    }
}
