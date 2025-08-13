Configuration
=============

The ESP32 CAN Bus Vehicle Controller provides extensive configuration options through ESP-IDF's menuconfig system and code-level settings. This document describes all available configuration options and their usage.

Build-Time Configuration
-----------------------

The project uses ESP-IDF's Kconfig system for build-time configuration. Access the configuration menu with:

.. code-block:: bash

    idf.py menuconfig

Serial Flasher Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Flash Size**
  :Location: Serial flasher config → Flash size
  :Default: 4MB
  :Recommended: 8MB or 16MB
  :Description: Sets the flash memory size for the ESP32-S3

**Flash Mode**
  :Location: Serial flasher config → Flash SPI mode
  :Default: DIO
  :Options: QIO, QOUT, DIO, DOUT
  :Description: SPI flash interface mode

**Flash Frequency**
  :Location: Serial flasher config → Flash SPI speed
  :Default: 80 MHz
  :Options: 80 MHz, 40 MHz, 26.7 MHz, 20 MHz
  :Description: SPI flash clock frequency

**Monitor Baud Rate**
  :Location: Serial flasher config → Monitor baud rate
  :Default: 115200
  :Options: 9600, 57600, 115200, 230400, 460800, 921600
  :Description: Serial monitor communication speed

Example Configuration Display
~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Touch Controller Configuration**
  :Location: Example Configuration → Touch Controller
  :Setting: ``CONFIG_EXAMPLE_LCD_TOUCH_CONTROLLER_GT911``
  :Default: Disabled
  :Description: Enable GT911 touch controller support

.. code-block:: kconfig

    menu "Touch Controller"
        config EXAMPLE_LCD_TOUCH_CONTROLLER_GT911
            bool "Enable LCD GT911 Touch"
            default n
            help
                Enable this option if you wish to use display touch.
    endmenu

**Display Configuration**

*RGB Bounce Buffer Height*
  :Location: Example Configuration → Display → RGB Bounce buffer height
  :Setting: ``CONFIG_EXAMPLE_LCD_RGB_BOUNCE_BUFFER_HEIGHT``
  :Default: 10
  :Range: 1-50
  :Description: Height of RGB bounce buffer in lines

*LVGL Task Configuration*
  :Location: Example Configuration → Display → LVGL timer task settings
  
  - **Maximum Delay**: ``CONFIG_EXAMPLE_LVGL_PORT_TASK_MAX_DELAY_MS`` (default: 500ms)
  - **Minimum Delay**: ``CONFIG_EXAMPLE_LVGL_PORT_TASK_MIN_DELAY_MS`` (default: 10ms)
  - **Task Priority**: ``CONFIG_EXAMPLE_LVGL_PORT_TASK_PRIORITY`` (default: 2)
  - **Stack Size**: ``CONFIG_EXAMPLE_LVGL_PORT_TASK_STACK_SIZE_KB`` (default: 6KB)
  - **CPU Core**: ``CONFIG_EXAMPLE_LVGL_PORT_TASK_CORE`` (default: -1, any core)

ESP32S3 Specific Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**CPU Frequency**
  :Location: Component config → ESP32S3-Specific → CPU frequency
  :Default: 240 MHz
  :Options: 80 MHz, 160 MHz, 240 MHz
  :Recommendation: 240 MHz for optimal performance

**Flash and PSRAM**
  :Location: Component config → ESP32S3-Specific → Support for external PSRAM
  :Default: Disabled
  :Description: Enable if using external PSRAM

**Instruction Cache**
  :Location: Component config → ESP32S3-Specific → Instruction cache size
  :Default: 16KB
  :Options: 16KB, 32KB
  :Recommendation: 32KB for larger applications

**Data Cache**
  :Location: Component config → ESP32S3-Specific → Data cache size
  :Default: 32KB
  :Options: 32KB, 64KB
  :Recommendation: 64KB for better performance

Component Configuration
~~~~~~~~~~~~~~~~~~~~~~

**FreeRTOS Settings**
  :Location: Component config → FreeRTOS

  - **Tick rate**: Default 1000 Hz (1ms tick)
  - **Task stack size**: Default 3584 bytes
  - **Idle task stack size**: Default 1536 bytes
  - **Timer task priority**: Default 1
  - **Timer task stack size**: Default 3584 bytes

**Log Output**
  :Location: Component config → Log output
  
  - **Default log verbosity**: ERROR, WARN, INFO, DEBUG, VERBOSE
  - **Maximum log verbosity**: Sets compile-time limit
  - **Log timestamps**: Include timestamps in log output
  - **Log colors**: Enable colored log output

**TWAI (CAN) Configuration**
  :Location: Component config → Driver configurations → TWAI configuration

  - **ISR in IRAM**: Place TWAI ISR in IRAM for better performance
  - **ERRATA FIX**: Enable hardware errata fixes

Runtime Configuration
--------------------

Vehicle Selection
~~~~~~~~~~~~~~~

The controller maintains a mapping of vehicle types to display names:

.. code-block:: cpp

    ButtonMap button_map = {
        { VW_T5,             {"VW T5"} },
        { VW_T6,             {"VW T6"} },
        { VW_T61,            {"VW T6.1"} },
        { VW_T7,             {"VW T7"} },
        { MB_SPRINTER,       {"M Sprinter"} },
        { MB_SPRINTER_2023,  {"Mercedes Sprinter 2023"} },
        { JEEP_RENEGADE,     {"Jeep Renegade"} },
        { JEEP_RENEGADE_MHEV,{"Jeep Renegade MHEV"} },
        { MB_VIANO,          {"Mercedes Viano"} }
    };

**Default Vehicle**: VW_T7

**Runtime Changes**: Vehicle selection can be changed through the GUI dropdown or programmatically via ``setCurrentVehicle()``.

Speed and Gear Settings
~~~~~~~~~~~~~~~~~~~~~~

**Speed Range**
  :Minimum: 0 km/h
  :Maximum: 250 km/h
  :Default: 0 km/h
  :Resolution: 1 km/h

**Gear Positions**
  :Available: PARK, REVERSE, NEUTRAL, DRIVE
  :Default: PARK
  :Encoding: Vehicle-specific gear values

GPIO Pin Configuration
--------------------

Display Interface Pins
~~~~~~~~~~~~~~~~~~~~~

The RGB display interface requires multiple GPIO pins. Default configuration:

.. code-block:: c

    // RGB Data Lines
    #define EXAMPLE_PIN_NUM_RGB_R0    1
    #define EXAMPLE_PIN_NUM_RGB_R1    2
    #define EXAMPLE_PIN_NUM_RGB_R2    42
    #define EXAMPLE_PIN_NUM_RGB_R3    41
    #define EXAMPLE_PIN_NUM_RGB_R4    40
    
    #define EXAMPLE_PIN_NUM_RGB_G0    39
    #define EXAMPLE_PIN_NUM_RGB_G1    38
    #define EXAMPLE_PIN_NUM_RGB_G2    37
    #define EXAMPLE_PIN_NUM_RGB_G3    36
    #define EXAMPLE_PIN_NUM_RGB_G4    35
    #define EXAMPLE_PIN_NUM_RGB_G5    34
    
    #define EXAMPLE_PIN_NUM_RGB_B0    33
    #define EXAMPLE_PIN_NUM_RGB_B1    26
    #define EXAMPLE_PIN_NUM_RGB_B2    25
    #define EXAMPLE_PIN_NUM_RGB_B3    24
    #define EXAMPLE_PIN_NUM_RGB_B4    23
    
    // Control Lines
    #define EXAMPLE_PIN_NUM_HSYNC     46
    #define EXAMPLE_PIN_NUM_VSYNC     3
    #define EXAMPLE_PIN_NUM_PCLK      21
    #define EXAMPLE_PIN_NUM_DE        47
    #define EXAMPLE_PIN_NUM_DISP_EN   -1  // Not connected
    #define EXAMPLE_PIN_NUM_BK_LIGHT  45

Touch Interface Pins
~~~~~~~~~~~~~~~~~~~

For GT911 touch controller (I2C interface):

.. code-block:: c

    #define EXAMPLE_PIN_NUM_TOUCH_SDA  19
    #define EXAMPLE_PIN_NUM_TOUCH_SCL  20
    #define EXAMPLE_PIN_NUM_TOUCH_INT  18
    #define EXAMPLE_PIN_NUM_TOUCH_RST  4

CAN Interface Pins
~~~~~~~~~~~~~~~~~

TWAI (CAN) interface configuration:

.. code-block:: c

    #define EXAMPLE_PIN_NUM_CAN_TX     5
    #define EXAMPLE_PIN_NUM_CAN_RX     6

**Pin Customization**: Modify pin assignments in the respective header files:
- Display: ``main/waveshare_rgb_lcd_port.h``
- Touch: ``main/lvgl_port.h``
- CAN: ``main/CarCanController.cpp``

Display Configuration
-------------------

Resolution and Timing
~~~~~~~~~~~~~~~~~~~~

**Display Resolution**
  :Width: 800 pixels
  :Height: 480 pixels
  :Color Depth: 16-bit (RGB565)

**Timing Parameters**
  :Pixel Clock: Configurable based on display requirements
  :Horizontal Timing: Display-specific values
  :Vertical Timing: Display-specific values

**Buffer Configuration**
  :Draw Buffer Size: Configurable in LVGL settings
  :Bounce Buffer: Configurable height for RGB interface
  :Double Buffering: Available for smooth rendering

LVGL Configuration
~~~~~~~~~~~~~~~~

**Memory Management**
  :Heap Size: Configured in LVGL settings
  :Buffer Count: Single or double buffering options
  :Memory Type: Internal or external memory selection

**Performance Settings**
  :DMA Usage: Enable for better performance
  :Partial Refresh: Available for static content
  :Anti-aliasing: Configurable quality levels

**Widget Settings**
  :Default Styles: Customizable theme and styling
  :Animation: Enable/disable animations
  :Fonts: Configurable font sets and sizes

CAN Configuration
---------------

TWAI Driver Settings
~~~~~~~~~~~~~~~~~~

**Bus Timing**
  :Bit Rate: Configurable (typical: 500 kbps)
  :Sample Point: Adjustable timing
  :Synchronization Jump Width: Timing tolerance

**Filter Configuration**
  :Acceptance Filters: Configure message filtering
  :Mask Settings: Define filter masks
  :Filter Count: Number of active filters

**Transmission Settings**
  :Queue Size: Number of pending messages
  :Retry Count: Automatic retransmission attempts
  :Priority: Message transmission priority

Vehicle-Specific Settings
~~~~~~~~~~~~~~~~~~~~~~~~

Each vehicle has specific CAN configuration:

.. code-block:: cpp

    struct VehicleCanConfig {
        uint32_t speed_msg_id;      // CAN ID for speed messages
        uint32_t gear_msg_id;       // CAN ID for gear messages
        uint32_t baud_rate;         // CAN bus speed
        SpeedMessageGenerator speed_generator;
        GearMessageGenerator gear_generator;
    };

**Example VW T7 Configuration**:

.. code-block:: cpp

    vehicle_configs[VW_T7] = {
        .speed_msg_id = 0x0FD,
        .gear_msg_id = 0x3DC,
        .baud_rate = 500000,
        .speed_generator = [this](uint8_t speed, uint8_t* data, uint8_t& dlc) {
            generateVWSpeedMessage(0.01f, speed, data, dlc);
        },
        .gear_generator = [this](Gear gear, uint8_t* data, uint8_t& dlc) {
            generateVWGearMessage(data, dlc, gear);
        }
    };

Logging Configuration
-------------------

Log Levels
~~~~~~~~~~

Configure logging verbosity for different components:

.. code-block:: c

    // Global log level
    esp_log_level_set("*", ESP_LOG_INFO);
    
    // Component-specific levels
    esp_log_level_set("CarCan", ESP_LOG_DEBUG);
    esp_log_level_set("CarCanGui", ESP_LOG_INFO);
    esp_log_level_set("LVGL", ESP_LOG_WARN);
    esp_log_level_set("TWAI", ESP_LOG_DEBUG);

**Available Levels**:
- ``ESP_LOG_NONE``: No logging
- ``ESP_LOG_ERROR``: Error messages only
- ``ESP_LOG_WARN``: Warnings and errors
- ``ESP_LOG_INFO``: Informational messages
- ``ESP_LOG_DEBUG``: Debug information
- ``ESP_LOG_VERBOSE``: All messages

Log Output Format
~~~~~~~~~~~~~~~

**Timestamp Format**:
  :Options: None, milliseconds, microseconds
  :Configuration: menuconfig → Component config → Log output

**Color Output**:
  :Enable: Colored log output for better readability
  :Disable: Plain text output for file logging

Custom Configuration Profiles
----------------------------

Development Profile
~~~~~~~~~~~~~~~~~

Optimized for development and debugging:

.. code-block:: bash

    # menuconfig settings
    CONFIG_LOG_DEFAULT_LEVEL_DEBUG=y
    CONFIG_COMPILER_OPTIMIZATION_DEBUG=y
    CONFIG_ESP32S3_DEBUG_OCDAWARE=y
    CONFIG_FREERTOS_WATCHPOINT_END_OF_STACK=y

**Characteristics**:
- Debug optimization level
- Verbose logging enabled
- Stack overflow detection
- JTAG debugging support

Testing Profile
~~~~~~~~~~~~~

Configuration for comprehensive testing:

.. code-block:: bash

    # menuconfig settings
    CONFIG_LOG_DEFAULT_LEVEL_VERBOSE=y
    CONFIG_FREERTOS_GENERATE_RUN_TIME_STATS=y
    CONFIG_FREERTOS_CHECK_STACKOVERFLOW_PTRVAL=y
    CONFIG_ESP_TASK_WDT_PANIC=y

**Characteristics**:
- Maximum logging detail
- Runtime statistics collection
- Enhanced error checking
- Task watchdog enabled

Production Profile
~~~~~~~~~~~~~~~~

Optimized for deployment:

.. code-block:: bash

    # menuconfig settings
    CONFIG_LOG_DEFAULT_LEVEL_WARN=y
    CONFIG_COMPILER_OPTIMIZATION_SIZE=y
    CONFIG_BOOTLOADER_LOG_LEVEL_WARN=y
    CONFIG_ESP32S3_REV_MIN_3=y

**Characteristics**:
- Minimal logging overhead
- Size optimization
- Reduced debug information
- Hardware revision constraints

Configuration Management
-----------------------

Saving Configurations
~~~~~~~~~~~~~~~~~~~~

**Save Current Configuration**:

.. code-block:: bash

    # Save to default config file
    idf.py save-defconfig
    
    # Save to custom file
    cp sdkconfig custom_config

**Load Saved Configuration**:

.. code-block:: bash

    # Load from saved config
    cp custom_config sdkconfig
    idf.py reconfigure

Environment-Specific Configs
~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Development Environment**:

.. code-block:: bash

    # Use development defaults
    cp configs/sdkconfig.dev sdkconfig
    idf.py reconfigure build

**Production Environment**:

.. code-block:: bash

    # Use production defaults
    cp configs/sdkconfig.prod sdkconfig
    idf.py reconfigure build

Configuration Validation
~~~~~~~~~~~~~~~~~~~~~~~

**Check Configuration Consistency**:

.. code-block:: bash

    # Validate current configuration
    idf.py reconfigure
    
    # Check for conflicts
    idf.py menuconfig  # Look for warnings

**Common Issues**:
- Pin conflicts between interfaces
- Memory allocation exceeding limits
- Incompatible timing settings
- Missing required dependencies

Advanced Configuration Options
----------------------------

Security Configuration
~~~~~~~~~~~~~~~~~~~~

**Secure Boot**:
  :Location: Security features → Enable hardware secure boot
  :Description: Cryptographic verification of firmware
  :Requirement: Secure boot keys and signed binaries

**Flash Encryption**:
  :Location: Security features → Enable flash encryption
  :Description: Encrypt firmware and data in flash
  :Requirement: Encryption keys and compatible bootloader

**Application Security**:
  :Location: Component config → Application Level Tracing
  :Description: Runtime security monitoring
  :Features: Stack overflow detection, heap corruption detection

Power Management
~~~~~~~~~~~~~~

**CPU Frequency Scaling**:
  :Location: Component config → Power Management
  :Description: Dynamic frequency adjustment
  :Options: Enable automatic frequency switching

**Sleep Modes**:
  :Location: Component config → Power Management
  :Description: Low-power modes configuration
  :Types: Light sleep, deep sleep, hibernation

**Peripheral Power**:
  :Location: Component config → Power Management
  :Description: Individual peripheral power control
  :Options: Auto-off unused peripherals

Memory Optimization
~~~~~~~~~~~~~~~~~

**Stack Size Optimization**:

.. code-block:: c

    // Custom stack sizes for tasks
    #define CAN_TASK_STACK_SIZE    4096
    #define GUI_TASK_STACK_SIZE    8192
    #define MONITOR_TASK_STACK_SIZE 2048

**Heap Configuration**:
  :Location: Component config → Heap memory debugging
  :Options: Heap tracing, corruption detection
  :Monitoring: Runtime heap usage statistics

**Flash Usage**:
  :Partition Table: Custom partition layouts
  :Code Placement: IRAM vs Flash execution
  :Data Storage: NVS vs SPIFFS vs LittleFS

Troubleshooting Configuration Issues
----------------------------------

Common Configuration Problems
~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Build Failures**:

.. code-block:: bash

    # Reset to defaults
    rm sdkconfig sdkconfig.old
    idf.py reconfigure
    
    # Clean rebuild
    idf.py fullclean build

**Runtime Issues**:

.. code-block:: bash

    # Check configuration
    idf.py show-efuse-table
    idf.py partition-table
    
    # Monitor memory usage
    idf.py size-components

**Hardware Compatibility**:
- Verify GPIO pin assignments
- Check voltage level compatibility
- Validate timing parameters
- Confirm interface protocols

Configuration Best Practices
---------------------------

Development Workflow
~~~~~~~~~~~~~~~~~~

1. **Start with defaults**: Use provided ``sdkconfig.defaults``
2. **Incremental changes**: Modify one setting at a time
3. **Version control**: Track configuration changes in git
4. **Document changes**: Maintain configuration change log
5. **Test thoroughly**: Validate each configuration change

Production Deployment
~~~~~~~~~~~~~~~~~~~

1. **Optimize for target**: Use production-specific settings
2. **Security hardening**: Enable appropriate security features
3. **Performance tuning**: Optimize for memory and speed
4. **Validation testing**: Comprehensive testing with production config
5. **Backup configuration**: Maintain configuration archives

Configuration Documentation
~~~~~~~~~~~~~~~~~~~~~~~~~

Document custom configurations:

.. code-block:: 

    Configuration Profile: Production V1.0
    Date: 2024-01-01
    Purpose: Vehicle deployment configuration
    
    Key Changes:
    - Log level set to WARN
    - Size optimization enabled
    - Security features activated
    - Custom GPIO assignments
    
    Validation:
    - Tested with VW T7 vehicle
    - Memory usage: 45% flash, 30% RAM
    - Performance: <100ms response time

This comprehensive configuration system ensures the ESP32 CAN Bus Vehicle Controller can be adapted to various hardware configurations, deployment environments, and vehicle requirements.