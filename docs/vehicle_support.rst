Vehicle Support
===============

The ESP32 CAN Bus Vehicle Controller supports multiple vehicle manufacturers and models, each with specific CAN message protocols and configurations. This document details the supported vehicles and their implementation.

Supported Vehicles Overview
--------------------------

Currently Supported
~~~~~~~~~~~~~~~~~

The controller supports the following vehicle types:

**Volkswagen:**
* T5 (2003-2015)
* T6 (2015-2019) 
* T6.1 (2019-2023)
* T7 (2021+)

**Mercedes-Benz:**
* Sprinter (various years)
* Sprinter 2023+ (updated protocol)
* Viano (2003-2014)

**Jeep:**
* Renegade (2014+)
* Renegade MHEV (Mild Hybrid Electric Vehicle)

Vehicle Implementation Details
----------------------------

Volkswagen T-Series
~~~~~~~~~~~~~~~~~~

The Volkswagen T-series vans share similar CAN protocols with minor variations between generations.

**VW T7 (Primary Implementation)**

* **CAN Bus Speed**: 500 kbps
* **Speed Message ID**: ``0x0FD``
* **Gear Message ID**: ``0x3DC``
* **Message Format**: Standard 8-byte CAN frames

**Speed Message Protocol:**

.. code-block::

    Message ID: 0x0FD
    DLC: 8 bytes
    Data Format:
    Byte 0-3: Reserved/Other data
    Byte 4-5: Speed value (LSB first)
    Byte 6-7: Reserved/Other data
    
    Speed Calculation:
    speed_value = speed_kmh / 0.01
    data[4] = speed_value & 0xFF
    data[5] = (speed_value >> 8) & 0xFF

**Gear Message Protocol:**

.. code-block::

    Message ID: 0x3DC
    DLC: 8 bytes
    Data Format:
    Byte 0-4: Reserved/Other data
    Byte 5: Gear position
    Byte 6-7: Reserved/Other data
    
    Gear Values:
    0x05 = Park (P)
    0x04 = Reverse (R)
    0x03 = Neutral (N)
    0x02 = Drive (D)

**VW T6/T6.1 Differences:**

.. code-block:: cpp

    // VW T6 Configuration
    vehicle_configs[VW_T6] = {
        .speed_msg_id = 0x1FD,     // Different message ID
        .gear_msg_id = 0x3DD,      // Different message ID
        .baud_rate = 500000,
        // Same message generation functions
    };

**VW T5 Legacy Support:**

The T5 uses an older protocol that may require different message formatting. Current implementation uses T6/T7 format as baseline.

Mercedes-Benz Vehicles
~~~~~~~~~~~~~~~~~~~~

Mercedes vehicles use different CAN protocols compared to Volkswagen.

**Mercedes Sprinter**

* **CAN Bus Speed**: 500 kbps
* **Protocol**: Mercedes-specific message format
* **Implementation Status**: Partial (message IDs defined, protocol needs refinement)

.. code-block:: cpp

    // Mercedes Sprinter placeholder configuration
    vehicle_configs[MB_SPRINTER] = {
        .speed_msg_id = 0x200,     // Example ID - needs verification
        .gear_msg_id = 0x300,      // Example ID - needs verification
        .baud_rate = 500000,
        // Custom message generators needed
    };

**Mercedes Sprinter 2023+**

The 2023+ Sprinter models have updated CAN protocols that may differ from earlier versions.

**Mercedes Viano**

* **Years**: 2003-2014
* **Protocol**: Earlier Mercedes CAN implementation
* **Implementation Status**: Framework defined, needs protocol development

Jeep Vehicles
~~~~~~~~~~~

Jeep vehicles use FCA (Fiat Chrysler Automobiles) CAN protocols.

**Jeep Renegade**

* **CAN Bus Speed**: 500 kbps
* **Protocol**: FCA-specific message format
* **Implementation Status**: Framework defined, needs protocol implementation

**Jeep Renegade MHEV**

The Mild Hybrid Electric Vehicle variant may have additional CAN messages for hybrid system status.

Adding New Vehicle Support
-------------------------

Vehicle Configuration Structure
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Each vehicle is defined by a ``VehicleCanConfig`` structure:

.. code-block:: cpp

    struct VehicleCanConfig {
        uint32_t speed_msg_id;           // CAN ID for speed messages
        uint32_t gear_msg_id;            // CAN ID for gear messages
        uint32_t baud_rate;              // CAN bus speed (typically 500000)
        SpeedMessageGenerator speed_generator;  // Function to generate speed messages
        GearMessageGenerator gear_generator;    // Function to generate gear messages
    };

Step-by-Step Implementation
~~~~~~~~~~~~~~~~~~~~~~~~~

**1. Define Vehicle Enum**

Add new vehicle to ``main/common.h``:

.. code-block:: cpp

    enum button_id_t {
        // ... existing vehicles ...
        NEW_VEHICLE = 10,
    };

**2. Add Button Mapping**

Update button map in ``CarCanController.cpp``:

.. code-block:: cpp

    CarCanController::CarCanController() {
        button_map = {
            // ... existing mappings ...
            { NEW_VEHICLE, {"New Vehicle Name"} },
        };
    }

**3. Implement Message Generators**

Create vehicle-specific message generation functions:

.. code-block:: cpp

    // Speed message generator for new vehicle
    void generateNewVehicleSpeedMessage(uint8_t speed_kmh, uint8_t* data, uint8_t& dlc) {
        dlc = 8;
        std::memset(data, 0, dlc);
        
        // Implement vehicle-specific speed message format
        // Example: Place speed in bytes 2-3
        uint16_t speed_value = speed_kmh * 10;  // Vehicle-specific scaling
        data[2] = speed_value & 0xFF;
        data[3] = (speed_value >> 8) & 0xFF;
    }
    
    // Gear message generator for new vehicle
    void generateNewVehicleGearMessage(Gear gear, uint8_t* data, uint8_t& dlc) {
        dlc = 8;
        std::memset(data, 0, dlc);
        
        // Implement vehicle-specific gear message format
        uint8_t gear_value;
        switch (gear) {
            case Gear::PARK:     gear_value = 0x01; break;  // Vehicle-specific values
            case Gear::REVERSE:  gear_value = 0x02; break;
            case Gear::NEUTRAL:  gear_value = 0x03; break;
            case Gear::DRIVE:    gear_value = 0x04; break;
            default:            gear_value = 0x01; break;
        }
        data[0] = gear_value;  // Vehicle-specific byte position
    }

**4. Add Vehicle Configuration**

Add configuration to ``initializeVehicleConfigs()`` in ``CarCanMessageGenerator.cpp``:

.. code-block:: cpp

    void CarCanMessageGenerator::initializeVehicleConfigs() {
        // ... existing configurations ...
        
        // New Vehicle Configuration
        vehicle_configs[NEW_VEHICLE] = {
            .speed_msg_id = 0x123,     // Vehicle-specific CAN ID
            .gear_msg_id = 0x456,      // Vehicle-specific CAN ID
            .baud_rate = 500000,       // or vehicle-specific baud rate
            .speed_generator = [this](uint8_t speed, uint8_t* data, uint8_t& dlc) {
                generateNewVehicleSpeedMessage(speed, data, dlc);
            },
            .gear_generator = [this](Gear gear, uint8_t* data, uint8_t& dlc) {
                generateNewVehicleGearMessage(gear, data, dlc);
            }
        };
    }

Protocol Development Guidelines
-----------------------------

CAN Message Analysis
~~~~~~~~~~~~~~~~~~

When adding support for a new vehicle, follow these steps:

**1. CAN Bus Monitoring**

Use CAN analysis tools to capture vehicle messages:

.. code-block:: bash

    # Linux with SocketCAN
    candump can0
    
    # With PCAN-USB
    pcanview
    
    # With CANtact
    cantact-dump

**2. Message Identification**

Identify relevant messages by:

* Monitoring during speed changes
* Observing gear position changes
* Looking for periodic transmission patterns
* Correlating with vehicle behavior

**3. Message Format Analysis**

For each identified message:

* Document message ID (11-bit or 29-bit)
* Record data length code (DLC)
* Analyze byte-by-byte data changes
* Determine scaling factors and offsets
* Identify bit fields and flags

**4. Protocol Documentation**

Create protocol documentation:

.. code-block::

    Vehicle: [Vehicle Name]
    Year Range: [Years]
    CAN Bus Speed: [Speed in bps]
    
    Speed Message:
    - ID: 0x[HEX]
    - DLC: [Length]
    - Format: [Byte breakdown]
    - Scaling: [Formula]
    - Range: [Min-Max values]
    
    Gear Message:
    - ID: 0x[HEX] 
    - DLC: [Length]
    - Format: [Byte breakdown]
    - Values: [Gear mappings]

Message Generation Best Practices
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Reuse Common Functions**

For vehicles with similar protocols, reuse existing generation functions:

.. code-block:: cpp

    // Reuse VW protocol for similar vehicles
    vehicle_configs[SIMILAR_VEHICLE] = {
        .speed_msg_id = 0x2FD,     // Different ID
        .gear_msg_id = 0x4DC,      // Different ID
        .baud_rate = 500000,
        .speed_generator = [this](uint8_t speed, uint8_t* data, uint8_t& dlc) {
            generateVWSpeedMessage(0.01f, speed, data, dlc);  // Reuse VW function
        },
        .gear_generator = [this](Gear gear, uint8_t* data, uint8_t& dlc) {
            generateVWGearMessage(data, dlc, gear);  // Reuse VW function
        }
    };

**Parameter Customization**

Use parameters to customize shared functions:

.. code-block:: cpp

    // Generic function with parameters
    static void generateGenericSpeedMessage(float scale_factor, uint8_t byte_offset, 
                                          uint8_t speed_kmh, uint8_t* data, uint8_t& dlc) {
        dlc = 8;
        std::memset(data, 0, dlc);
        uint16_t speed_value = static_cast<uint16_t>(speed_kmh / scale_factor);
        data[byte_offset] = speed_value & 0xFF;
        data[byte_offset + 1] = (speed_value >> 8) & 0xFF;
    }
    
    // Use with different parameters
    .speed_generator = [this](uint8_t speed, uint8_t* data, uint8_t& dlc) {
        generateGenericSpeedMessage(0.01f, 4, speed, data, dlc);  // VW-style
    },

Testing Vehicle Support
----------------------

Simulation Testing
~~~~~~~~~~~~~~~~

Test new vehicle support without actual hardware:

.. code-block:: cpp

    // Test message generation in main.cpp
    void test_vehicle_messages() {
        CarCanMessageGenerator generator;
        uint8_t data[8];
        uint8_t dlc;
        
        // Test speed message
        generator.generateSpeedMessage(NEW_VEHICLE, 100, data, dlc);
        ESP_LOGI("TEST", "Speed message: %02X %02X %02X %02X %02X %02X %02X %02X",
                 data[0], data[1], data[2], data[3], data[4], data[5], data[6], data[7]);
        
        // Test gear message
        generator.generateGearMessage(NEW_VEHICLE, Gear::DRIVE, data, dlc);
        ESP_LOGI("TEST", "Gear message: %02X %02X %02X %02X %02X %02X %02X %02X",
                 data[0], data[1], data[2], data[3], data[4], data[5], data[6], data[7]);
    }

Hardware Testing
~~~~~~~~~~~~~~

Test with CAN transceiver and monitoring equipment:

.. code-block:: cpp

    // Enable debug logging for CAN messages
    esp_log_level_set("CarCan", ESP_LOG_DEBUG);
    
    // Monitor outgoing messages
    void log_can_message(uint32_t id, uint8_t* data, uint8_t dlc) {
        ESP_LOGI("CAN", "TX: ID=0x%03X DLC=%d Data=%02X %02X %02X %02X %02X %02X %02X %02X",
                 id, dlc, data[0], data[1], data[2], data[3], data[4], data[5], data[6], data[7]);
    }

Vehicle Integration Testing
~~~~~~~~~~~~~~~~~~~~~~~~~

When testing with actual vehicles:

1. **Start with read-only monitoring** to verify protocol understanding
2. **Test with isolated systems** before connecting to main vehicle bus
3. **Use CAN filters** to avoid interfering with vehicle operation
4. **Monitor for error frames** and bus-off conditions
5. **Validate message timing** and periodicity requirements

Protocol Validation
~~~~~~~~~~~~~~~~~~

Verify protocol implementation:

.. code-block:: python

    # Python script for protocol validation
    import can
    
    def validate_protocol(vehicle_type, test_cases):
        bus = can.interface.Bus(channel='can0', bustype='socketcan')
        
        for speed, expected_data in test_cases:
            # Send test message
            msg = can.Message(arbitration_id=0x0FD, data=expected_data, is_extended_id=False)
            bus.send(msg)
            
            # Verify against implementation
            print(f"Speed {speed}: Expected {expected_data.hex()}")

Known Protocol Variations
------------------------

Common Differences Between Vehicles
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Message ID Variations:**
* Same protocol, different CAN IDs
* Extended vs standard frame formats
* Multi-frame messages for complex data

**Data Format Differences:**
* Byte order (little-endian vs big-endian)
* Scaling factors and units
* Bit field positions and sizes
* Reserved/padding bytes

**Timing Requirements:**
* Message transmission intervals
* Response timeouts
* Bus arbitration priorities

**Bus Configuration:**
* CAN bus speed variations (125k, 250k, 500k, 1M bps)
* Termination requirements
* Multiple CAN buses (powertrain, body, infotainment)

Manufacturer-Specific Notes
~~~~~~~~~~~~~~~~~~~~~~~~~

**Volkswagen Group:**
* Generally consistent protocols across VW, Audi, Seat, Skoda
* Gateway modules may filter messages
* Some models require authentication for certain messages

**Mercedes-Benz:**
* Different protocols for different vehicle classes
* May use proprietary diagnostic protocols
* CAN-FD support in newer models

**Stellantis (FCA):**
* Jeep, Chrysler, Dodge, Fiat protocols
* May require security access for message injection
* Multiple CAN network architecture

Future Enhancements
-----------------

Planned Features
~~~~~~~~~~~~~~

**Enhanced Vehicle Support:**
* More granular model year support
* Additional message types (engine data, diagnostics)
* Support for CAN-FD (Controller Area Network Flexible Data-Rate)

**Protocol Features:**
* Automatic protocol detection
* Message validation and error checking
* Bidirectional communication support

**Development Tools:**
* Protocol reverse engineering utilities
* Message capture and analysis tools
* Automated testing framework

**Security Features:**
* Message authentication
* Encryption support for sensitive data
* Access control and authorization

Contributing Vehicle Support
--------------------------

Community Contributions
~~~~~~~~~~~~~~~~~~~~~~

To contribute support for new vehicles:

1. **Document the protocol** thoroughly with CAN traces
2. **Test implementation** with actual hardware
3. **Follow coding standards** and existing patterns
4. **Provide test cases** for validation
5. **Update documentation** with new vehicle information

**Submission Requirements:**
* CAN message traces showing protocol behavior
* Implementation code following project structure
* Test results from actual vehicle testing
* Documentation updates for new vehicle support

**Review Process:**
* Code review for implementation quality
* Protocol validation against provided traces
* Testing with multiple vehicle instances (if possible)
* Integration testing with existing functionality

This collaborative approach ensures high-quality vehicle support and maintains compatibility across the growing list of supported vehicles.