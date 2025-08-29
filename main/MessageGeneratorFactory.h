#ifndef MESSAGE_GENERATOR_FACTORY_H
#define MESSAGE_GENERATOR_FACTORY_H

#include <memory>
#include <map>
#include "BaseMessageGenerator.h"
#include "common.h"

/**
 * Factory class for creating and managing vehicle-specific message generators
 */
class MessageGeneratorFactory {
public:
    /**
     * Get singleton instance of the factory
     */
    static MessageGeneratorFactory& getInstance();
    
    /**
     * Create or get cached message generator for specified vehicle
     * @param vehicle Vehicle button ID
     * @return Shared pointer to message generator, or nullptr if vehicle not supported
     */
    std::shared_ptr<BaseMessageGenerator> getMessageGenerator(button_id_t vehicle);
    
    /**
     * Check if a vehicle is supported
     * @param vehicle Vehicle button ID
     * @return true if supported, false otherwise
     */
    bool isVehicleSupported(button_id_t vehicle) const;
    
    /**
     * Get list of all supported vehicles
     * @return Vector of supported vehicle button IDs
     */
    std::vector<button_id_t> getSupportedVehicles() const;

private:
    MessageGeneratorFactory() = default;
    ~MessageGeneratorFactory() = default;
    
    // Delete copy constructor and assignment operator
    MessageGeneratorFactory(const MessageGeneratorFactory&) = delete;
    MessageGeneratorFactory& operator=(const MessageGeneratorFactory&) = delete;
    
    /**
     * Create a new message generator instance for the specified vehicle
     * @param vehicle Vehicle button ID
     * @return Unique pointer to message generator, or nullptr if not supported
     */
    std::unique_ptr<BaseMessageGenerator> createMessageGenerator(button_id_t vehicle);
    
    // Cache of created message generators
    std::map<button_id_t, std::shared_ptr<BaseMessageGenerator>> generator_cache;
};

#endif // MESSAGE_GENERATOR_FACTORY_H
