Troubleshooting
===============

This guide provides solutions to common issues encountered when building, deploying, and running the ESP32 CAN Bus Vehicle Controller.

Build and Compilation Issues
---------------------------

ESP-IDF Environment Problems
~~~~~~~~~~~~~~~~~~~~~~~~~~

**Error: "idf.py command not found"**

*Symptoms:*
- Command not recognized in terminal
- ESP-IDF tools unavailable

*Solutions:*

.. code-block:: bash

    # Set up ESP-IDF environment
    cd ~/esp/esp-idf
    . ./export.sh
    
    # Add to shell profile for persistence
    echo 'alias get_idf=". $HOME/esp/esp-idf/export.sh"' >> ~/.bashrc
    
    # Verify installation
    which idf.py
    echo $IDF_PATH

**Error: "Target 'esp32s3' not found"**

*Symptoms:*
- Build fails with unsupported target
- ESP32-S3 not recognized

*Solutions:*

.. code-block:: bash

    # Explicitly set target
    idf.py set-target esp32s3
    
    # Verify target
    idf.py show-efuse-table
    
    # Check ESP-IDF version (requires v4.4+)
    idf.py --version

**Error: Python dependency issues**

*Symptoms:*
- ImportError for required Python modules
- pip install failures

*Solutions:*

.. code-block:: bash

    # Reinstall ESP-IDF python dependencies
    cd $IDF_PATH
    ./install.sh esp32s3
    
    # Update pip
    python -m pip install --upgrade pip
    
    # Manual dependency installation
    pip install -r $IDF_PATH/requirements.txt

Submodule and Dependency Issues
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Error: Missing submodules**

*Symptoms:*
- Build fails with missing headers
- LVGL or other components not found

*Solutions:*

.. code-block:: bash

    # Initialize and update all submodules
    git submodule update --init --recursive
    
    # Force update if corrupted
    git submodule foreach --recursive git clean -xfd
    git submodule foreach --recursive git reset --hard
    git submodule update --init --recursive

**Error: Component registration failed**

*Symptoms:*
- CMake errors about missing components
- Component.mk not found errors

*Solutions:*

.. code-block:: bash

    # Clean and reconfigure
    idf.py fullclean
    idf.py reconfigure
    
    # Check component paths
    ls components/
    
    # Verify CMakeLists.txt syntax
    cat CMakeLists.txt

Memory and Storage Issues
~~~~~~~~~~~~~~~~~~~~~~~

**Error: "Region 'iram0_0_seg' overflowed"**

*Symptoms:*
- Linking fails due to insufficient IRAM
- Functions too large for IRAM

*Solutions:*

.. code-block:: bash

    # Reduce IRAM usage
    idf.py menuconfig
    # Component config → ESP32S3-Specific → Place RTC_DATA into → Flash
    
    # Move functions to flash
    # Remove IRAM_ATTR from non-critical functions
    
    # Check memory usage
    idf.py size

**Error: "No space left on device"**

*Symptoms:*
- Build fails with disk space errors
- Insufficient storage for build files

*Solutions:*

.. code-block:: bash

    # Clean build directory
    idf.py fullclean
    
    # Clean Docker images (if using Docker)
    docker system prune -a
    
    # Check disk space
    df -h
    
    # Clean temporary files
    rm -rf /tmp/esp-*

**Error: Flash size insufficient**

*Symptoms:*
- Partition table doesn't fit
- Application size exceeds flash

*Solutions:*

.. code-block:: bash

    # Increase flash size
    idf.py menuconfig
    # Serial flasher config → Flash size → 8MB or 16MB
    
    # Optimize for size
    # Compiler options → Optimization Level → Optimize for size (-Os)
    
    # Check partition table
    idf.py partition-table

Configuration Errors
~~~~~~~~~~~~~~~~~~~

**Error: Kconfig warnings or errors**

*Symptoms:*
- Configuration conflicts
- Invalid configuration combinations

*Solutions:*

.. code-block:: bash

    # Reset configuration
    rm sdkconfig sdkconfig.old
    idf.py reconfigure
    
    # Check for conflicts
    idf.py menuconfig
    # Look for warnings in red text
    
    # Use default configuration
    cp sdkconfig.defaults sdkconfig
    idf.py reconfigure

Flashing and Hardware Issues
---------------------------

Connection Problems
~~~~~~~~~~~~~~~~~

**Error: "Failed to connect to ESP32-S3"**

*Symptoms:*
- Serial port not detected
- Flash command fails
- Device not responding

*Solutions:*

.. code-block:: bash

    # Check USB connection
    ls /dev/ttyUSB* /dev/ttyACM*  # Linux
    ls /dev/cu.usbserial*         # macOS
    
    # Try different USB cable
    # Use shorter, high-quality cable
    
    # Manual boot mode
    # Hold BOOT button while pressing RESET
    
    # Try different baud rate
    idf.py -b 115200 flash

**Error: Permission denied accessing serial port**

*Symptoms:*
- "Permission denied" error on Linux
- Cannot open /dev/ttyUSB0

*Solutions:*

.. code-block:: bash

    # Add user to dialout group (Linux)
    sudo usermod -a -G dialout $USER
    
    # Apply group changes (logout/login or)
    newgrp dialout
    
    # Set permissions temporarily
    sudo chmod 666 /dev/ttyUSB0
    
    # Check current permissions
    ls -l /dev/ttyUSB*

**Error: Brownout detector triggered**

*Symptoms:*
- Device resets during flashing
- Brownout reset messages
- Unstable operation

*Solutions:*

.. code-block:: bash

    # Use external power supply
    # Check USB port power capacity
    
    # Disable brownout detector temporarily
    idf.py menuconfig
    # Component config → ESP32S3-Specific → Hardware Brownout Detector → Disable
    
    # Lower flash voltage
    # Component config → ESP32S3-Specific → Flash voltage

Flashing Errors
~~~~~~~~~~~~~

**Error: "Hash of data verified" failures**

*Symptoms:*
- Flash verification fails
- Data corruption during flash
- Inconsistent flashing results

*Solutions:*

.. code-block:: bash

    # Erase flash completely
    idf.py erase-flash
    
    # Flash at lower speed
    idf.py -b 115200 flash
    
    # Check flash integrity
    idf.py read-flash 0x0 0x1000 flash_test.bin
    
    # Try different ESP32-S3 board

**Error: Bootloader issues**

*Symptoms:*
- Device doesn't boot after flashing
- Stuck in bootloader mode
- Invalid bootloader errors

*Solutions:*

.. code-block:: bash

    # Reflash bootloader
    idf.py bootloader-flash
    
    # Erase and reflash everything
    idf.py erase-flash
    idf.py flash
    
    # Check bootloader compatibility
    idf.py show-efuse-table

Runtime Issues
-------------

Display Problems
~~~~~~~~~~~~~~

**Issue: Black screen, no display output**

*Symptoms:*
- Display remains black
- No GUI elements visible
- Backlight may or may not work

*Diagnosis:*

.. code-block:: bash

    # Check serial output for errors
    idf.py monitor
    
    # Look for display initialization messages
    # Check for GPIO configuration errors

*Solutions:*

1. **Power Supply Check:**

.. code-block:: bash

    # Verify 5V power to display
    # Check current consumption (should be 200-500mA)
    # Ensure stable power source

2. **GPIO Pin Verification:**

.. code-block:: c

    // Verify pin assignments in waveshare_rgb_lcd_port.h
    #define EXAMPLE_PIN_NUM_RGB_R0    1
    #define EXAMPLE_PIN_NUM_RGB_G0    39
    #define EXAMPLE_PIN_NUM_RGB_B0    33
    // ... check all pins match your hardware

3. **Cable Connections:**

.. code-block:: bash

    # Check FFC cable orientation
    # Verify all pins connected
    # Test with known-good cable

4. **Timing Configuration:**

.. code-block:: c

    // Check display timing in lvgl_port.c
    // Verify pixel clock frequency
    // Adjust timing parameters for your display

**Issue: Display artifacts or corruption**

*Symptoms:*
- Garbled graphics
- Color artifacts
- Partial display updates

*Solutions:*

.. code-block:: bash

    # Reduce pixel clock frequency
    # Check signal integrity with oscilloscope
    # Verify power supply stability
    
    # Adjust bounce buffer size
    idf.py menuconfig
    # Example Configuration → RGB Bounce buffer height → Increase

**Issue: Touch not working**

*Symptoms:*
- No response to touch input
- Incorrect touch coordinates
- Intermittent touch operation

*Diagnosis:*

.. code-block:: c

    // Enable touch debug logging
    esp_log_level_set("TOUCH", ESP_LOG_DEBUG);

*Solutions:*

1. **I2C Communication Check:**

.. code-block:: bash

    # Verify I2C wiring
    # SDA: GPIO19, SCL: GPIO20
    # Check pull-up resistors (typically 4.7kΩ)

2. **Touch Controller Configuration:**

.. code-block:: bash

    # Enable GT911 in menuconfig
    idf.py menuconfig
    # Example Configuration → Touch Controller → Enable GT911

3. **Calibration:**

.. code-block:: c

    // Add touch calibration routine
    // Implement touch coordinate mapping
    // Store calibration in NVS

CAN Communication Issues
~~~~~~~~~~~~~~~~~~~~~~

**Issue: No CAN messages transmitted**

*Symptoms:*
- CAN bus silent
- No messages on CAN analyzer
- TWAI driver errors

*Diagnosis:*

.. code-block:: c

    // Enable CAN debug logging
    esp_log_level_set("TWAI", ESP_LOG_DEBUG);
    esp_log_level_set("CarCan", ESP_LOG_DEBUG);

*Solutions:*

1. **Hardware Check:**

.. code-block:: bash

    # Verify CAN transceiver power (3.3V or 5V)
    # Check CANH/CANL connections
    # Ensure 120Ω termination resistors

2. **Driver Configuration:**

.. code-block:: c

    // Check TWAI configuration
    twai_general_config_t g_config = TWAI_GENERAL_CONFIG_DEFAULT(
        GPIO_NUM_5,  // TX pin
        GPIO_NUM_6,  // RX pin  
        TWAI_MODE_NORMAL
    );

3. **Bus Timing:**

.. code-block:: c

    // Verify timing configuration for 500kbps
    twai_timing_config_t t_config = TWAI_TIMING_CONFIG_500KBITS();

**Issue: CAN bus errors**

*Symptoms:*
- Bus-off conditions
- Error frames
- Message transmission failures

*Solutions:*

.. code-block:: c

    // Implement error handling
    twai_status_info_t status;
    twai_get_status_info(&status);
    
    if (status.state == TWAI_STATE_BUS_OFF) {
        // Recover from bus-off
        twai_initiate_recovery();
    }

**Issue: Wrong CAN message format**

*Symptoms:*
- Vehicle doesn't respond to messages
- Incorrect message content
- Protocol incompatibility

*Solutions:*

1. **Message Analysis:**

.. code-block:: bash

    # Use CAN analyzer to capture vehicle messages
    # Compare with generated messages
    # Verify message timing

2. **Protocol Verification:**

.. code-block:: c

    // Log generated messages
    ESP_LOGI("CAN", "Speed msg: ID=0x%03X Data=%02X %02X %02X %02X",
             msg_id, data[0], data[1], data[2], data[3]);

GUI and System Issues
~~~~~~~~~~~~~~~~~~~

**Issue: System crashes or resets**

*Symptoms:*
- Watchdog resets
- Panic errors
- Unexpected reboots

*Diagnosis:*

.. code-block:: bash

    # Decode crash dump
    idf.py monitor
    # Copy backtrace and decode:
    xtensa-esp32s3-elf-addr2line -pfiaC -e build/lvgl_porting.elf [ADDRESS]

*Solutions:*

1. **Stack Overflow:**

.. code-block:: bash

    # Increase task stack sizes
    # Enable stack overflow detection
    idf.py menuconfig
    # Component config → FreeRTOS → Check for stack overflow

2. **Memory Issues:**

.. code-block:: bash

    # Monitor heap usage
    idf.py size-components
    
    # Enable heap tracing
    # Component config → Heap memory debugging

**Issue: Poor GUI performance**

*Symptoms:*
- Slow touch response
- Jerky animations
- Display lag

*Solutions:*

.. code-block:: bash

    # Optimize LVGL configuration
    # Enable DMA for display
    # Reduce buffer size if memory constrained
    # Increase task priority

**Issue: Memory leaks**

*Symptoms:*
- Gradually increasing memory usage
- Eventually runs out of memory
- Heap corruption errors

*Solutions:*

.. code-block:: c

    // Enable heap debugging
    heap_caps_check_integrity_all(true);
    
    // Monitor heap usage
    size_t free_heap = esp_get_free_heap_size();
    ESP_LOGI("MEM", "Free heap: %d bytes", free_heap);

Vehicle Integration Issues
------------------------

Protocol Compatibility
~~~~~~~~~~~~~~~~~~~~

**Issue: Vehicle doesn't respond to CAN messages**

*Symptoms:*
- No observable changes in vehicle behavior
- Vehicle systems don't acknowledge messages
- CAN gateway blocking messages

*Solutions:*

1. **Message ID Verification:**

.. code-block:: bash

    # Capture actual vehicle CAN traffic
    # Verify message IDs match vehicle protocol
    # Check for gateway filtering

2. **Message Format Validation:**

.. code-block:: c

    // Compare message format with vehicle specification
    // Verify byte order and scaling factors
    // Check DLC (Data Length Code)

3. **Timing Requirements:**

.. code-block:: c

    // Implement proper message timing
    // Some vehicles require specific intervals
    // Add message sequencing if needed

**Issue: CAN bus overload**

*Symptoms:*
- High bus utilization
- Message transmission delays
- Bus error frames

*Solutions:*

.. code-block:: c

    // Reduce message transmission rate
    // Implement intelligent filtering
    // Prioritize critical messages

Safety and Security Issues
~~~~~~~~~~~~~~~~~~~~~~~~

**Issue: Vehicle gateway blocks messages**

*Symptoms:*
- Messages transmitted but no vehicle response
- Gateway module filtering traffic
- Security access required

*Solutions:*

1. **Authentication:**

.. code-block:: c

    // Implement vehicle-specific authentication
    // Send unlock/security access messages
    // Use manufacturer diagnostic protocols

2. **Alternative Access Points:**

.. code-block:: bash

    # Try different CAN buses if available
    # Use OBD-II vs direct CAN access
    # Check for multiple CAN networks

Performance Optimization
----------------------

Memory Optimization
~~~~~~~~~~~~~~~~~

**Issue: High memory usage**

*Solutions:*

.. code-block:: c

    // Use static allocation where possible
    static uint8_t can_tx_buffer[8];
    
    // Optimize LVGL memory usage
    // Reduce buffer sizes
    // Use external PSRAM if available

**Issue: Slow response times**

*Solutions:*

.. code-block:: c

    // Optimize task priorities
    // Use IRAM for critical functions
    // Enable compiler optimizations

.. code-block:: bash

    # Enable release optimizations
    idf.py menuconfig
    # Compiler options → Optimization Level → Optimize for performance (-O2)

Debugging Tools and Techniques
-----------------------------

Serial Debugging
~~~~~~~~~~~~~~~

**Enable Comprehensive Logging:**

.. code-block:: c

    // Set detailed logging levels
    esp_log_level_set("*", ESP_LOG_INFO);
    esp_log_level_set("CarCan", ESP_LOG_DEBUG);
    esp_log_level_set("CarCanGui", ESP_LOG_DEBUG);
    esp_log_level_set("TWAI", ESP_LOG_VERBOSE);

**Custom Debug Output:**

.. code-block:: c

    // Add debug hooks
    #ifdef DEBUG_MODE
    #define DEBUG_LOG(tag, format, ...) ESP_LOGI(tag, format, ##__VA_ARGS__)
    #else
    #define DEBUG_LOG(tag, format, ...)
    #endif

Hardware Debugging
~~~~~~~~~~~~~~~~~

**Oscilloscope Analysis:**

.. code-block:: bash

    # Check signal integrity
    # Verify timing requirements
    # Analyze power supply ripple
    # Check CAN bus differential signals

**Logic Analyzer:**

.. code-block:: bash

    # Capture I2C communication
    # Analyze SPI transactions
    # Verify GPIO timing
    # Debug protocol issues

Memory Analysis
~~~~~~~~~~~~~

**Heap Monitoring:**

.. code-block:: c

    // Periodic heap checks
    void monitor_heap() {
        size_t free_heap = esp_get_free_heap_size();
        size_t min_free = esp_get_minimum_free_heap_size();
        ESP_LOGI("HEAP", "Free: %d, Min: %d", free_heap, min_free);
    }

**Stack Analysis:**

.. code-block:: c

    // Monitor task stack usage
    UBaseType_t uxHighWaterMark = uxTaskGetStackHighWaterMark(NULL);
    ESP_LOGI("STACK", "Remaining stack: %d", uxHighWaterMark);

Common Error Codes
-----------------

ESP-IDF Error Codes
~~~~~~~~~~~~~~~~~~

* ``ESP_OK (0)``: Success
* ``ESP_FAIL (-1)``: Generic failure
* ``ESP_ERR_NO_MEM (0x101)``: Out of memory
* ``ESP_ERR_INVALID_ARG (0x102)``: Invalid argument
* ``ESP_ERR_TIMEOUT (0x107)``: Operation timeout
* ``ESP_ERR_NOT_FOUND (0x105)``: Resource not found

TWAI Error Codes
~~~~~~~~~~~~~~~

* ``ESP_ERR_INVALID_STATE``: TWAI driver not installed/started
* ``ESP_ERR_TIMEOUT``: Message transmission timeout
* ``ESP_ERR_NOT_SUPPORTED``: Feature not supported

Project-Specific Errors
~~~~~~~~~~~~~~~~~~~~~~

* ``Vehicle not supported``: Invalid vehicle ID
* ``Message generation failed``: Protocol error
* ``GUI initialization failed``: Display/touch error

Prevention Strategies
-------------------

Development Best Practices
~~~~~~~~~~~~~~~~~~~~~~~~~

1. **Incremental Testing:**
   - Test each component individually
   - Validate hardware before software integration
   - Use progressive complexity

2. **Version Control:**
   - Commit working configurations
   - Tag stable releases
   - Document changes thoroughly

3. **Hardware Validation:**
   - Use multimeter for power verification
   - Test cables and connections
   - Verify signal levels

4. **Code Review:**
   - Check resource management
   - Validate error handling
   - Review memory allocation

Production Deployment
~~~~~~~~~~~~~~~~~~~

1. **Pre-deployment Testing:**
   - Comprehensive hardware testing
   - Long-term stability testing
   - Vehicle compatibility validation

2. **Quality Assurance:**
   - Automated testing procedures
   - Performance benchmarking
   - Safety validation

3. **Documentation:**
   - Maintain troubleshooting logs
   - Document known issues
   - Create deployment checklists

This troubleshooting guide provides systematic approaches to identify and resolve common issues with the ESP32 CAN Bus Vehicle Controller. Regular reference to these procedures can help maintain system reliability and performance.