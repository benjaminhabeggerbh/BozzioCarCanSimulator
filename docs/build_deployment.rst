Build and Deployment Guide
==========================

This guide provides step-by-step instructions for setting up the development environment, building the ESP32 CAN Bus Vehicle Controller firmware, and deploying it to hardware.

Prerequisites
------------

Development Environment
~~~~~~~~~~~~~~~~~~~~~~

**Operating System Support:**
* Ubuntu 20.04 LTS or later
* macOS 10.15 or later  
* Windows 10 with WSL2 (recommended) or Windows natively

**Hardware Requirements:**
* ESP32-S3 development board
* USB cable for programming
* Waveshare RGB LCD display (optional for development)
* CAN transceiver board (for full functionality)

Software Dependencies
~~~~~~~~~~~~~~~~~~~

ESP-IDF Framework
^^^^^^^^^^^^^^^

The project requires ESP-IDF v5.0 or later.

**Installation on Linux/macOS:**

.. code-block:: bash

    # Clone ESP-IDF repository
    git clone --recursive https://github.com/espressif/esp-idf.git
    cd esp-idf
    git checkout v5.0
    git submodule update --init --recursive
    
    # Install ESP-IDF
    ./install.sh esp32s3
    
    # Set up environment
    . ./export.sh

**Installation on Windows:**

1. Download ESP-IDF Windows installer from Espressif website
2. Run the installer and follow the setup wizard
3. Select ESP32-S3 as the target chip
4. Install to default location (C:\\Espressif)

**Verification:**

.. code-block:: bash

    # Check ESP-IDF installation
    idf.py --version
    
    # Expected output: ESP-IDF v5.0 or later

Additional Tools
^^^^^^^^^^^^^^

**Git:** Required for cloning the repository

.. code-block:: bash

    # Linux (Ubuntu/Debian)
    sudo apt-get install git
    
    # macOS (with Homebrew)
    brew install git
    
    # Windows: Download from git-scm.com

**Python 3.7+:** Usually included with ESP-IDF installation

.. code-block:: bash

    python3 --version

Project Setup
------------

Repository Clone
~~~~~~~~~~~~~~

.. code-block:: bash

    # Clone the project repository
    git clone <repository-url> esp32-can-controller
    cd esp32-can-controller
    
    # Initialize and update submodules
    git submodule update --init --recursive

Environment Configuration
~~~~~~~~~~~~~~~~~~~~~~~~

**Set ESP-IDF Environment:**

.. code-block:: bash

    # Linux/macOS (run in each new terminal)
    . $HOME/esp/esp-idf/export.sh
    
    # Or add to .bashrc/.zshrc for automatic setup
    echo 'alias get_idf=". $HOME/esp/esp-idf/export.sh"' >> ~/.bashrc

**Verify Environment:**

.. code-block:: bash

    # Check that ESP-IDF tools are available
    which idf.py
    echo $IDF_PATH

Configuration
------------

Project Configuration
~~~~~~~~~~~~~~~~~~~

The project uses ESP-IDF's menuconfig system for configuration:

.. code-block:: bash

    # Open configuration menu
    idf.py menuconfig

**Key Configuration Sections:**

1. **Serial flasher config**
   
   * Set flash size to 8MB or 16MB
   * Configure baud rate (default: 460800)

2. **Example Configuration**
   
   * Enable/disable touch controller (GT911)
   * Configure LCD buffer settings
   * Set LVGL task parameters

3. **Component config > ESP32S3-Specific**
   
   * Configure CPU frequency (240 MHz recommended)
   * Set flash and PSRAM configuration

Hardware-Specific Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Display Configuration:**

Edit ``main/lvgl_port.h`` for your specific display:

.. code-block:: c

    // Display resolution
    #define LCD_H_RES              800
    #define LCD_V_RES              480
    
    // Color depth
    #define LCD_BIT_PER_PIXEL      16
    
    // Buffer configuration
    #define EXAMPLE_LCD_RGB_BOUNCE_BUFFER_HEIGHT  10

**GPIO Pin Configuration:**

Modify ``main/waveshare_rgb_lcd_port.h`` for your hardware:

.. code-block:: c

    // RGB data pins
    #define EXAMPLE_PIN_NUM_RGB_R0  1
    #define EXAMPLE_PIN_NUM_RGB_R1  2
    // ... additional pin definitions
    
    // Control pins
    #define EXAMPLE_PIN_NUM_HSYNC   46
    #define EXAMPLE_PIN_NUM_VSYNC   3
    #define EXAMPLE_PIN_NUM_PCLK    21

**CAN Interface Configuration:**

Update CAN pins in ``main/CarCanController.cpp``:

.. code-block:: c

    // TWAI (CAN) pin configuration
    #define CAN_TX_GPIO_NUM  5
    #define CAN_RX_GPIO_NUM  6

Building the Project
-------------------

Full Build Process
~~~~~~~~~~~~~~~~

.. code-block:: bash

    # Clean previous builds (optional)
    idf.py fullclean
    
    # Set target chip (if not already set)
    idf.py set-target esp32s3
    
    # Build the project
    idf.py build

**Build Output:**

The build process creates several files in the ``build/`` directory:

* ``lvgl_porting.bin`` - Main application binary
* ``bootloader/bootloader.bin`` - Bootloader binary
* ``partition_table/partition-table.bin`` - Partition table
* ``lvgl_porting.elf`` - ELF file with debug symbols

Incremental Builds
~~~~~~~~~~~~~~~~~

For faster development cycles:

.. code-block:: bash

    # Build only changed files
    idf.py build
    
    # Build and flash in one command
    idf.py flash
    
    # Build, flash, and monitor
    idf.py flash monitor

Build Configuration Options
~~~~~~~~~~~~~~~~~~~~~~~~~

**Debug Build:**

.. code-block:: bash

    # Enable debug symbols and disable optimization
    idf.py menuconfig
    # Navigate to: Compiler options -> Optimization Level -> Debug (-Og)
    idf.py build

**Release Build:**

.. code-block:: bash

    # Enable optimization for size
    idf.py menuconfig
    # Navigate to: Compiler options -> Optimization Level -> Optimize for size (-Os)
    idf.py build

**Custom Configuration:**

.. code-block:: bash

    # Save current configuration
    idf.py save-defconfig
    
    # Load saved configuration
    cp sdkconfig.defaults sdkconfig
    idf.py reconfigure

Flashing and Deployment
----------------------

Hardware Connection
~~~~~~~~~~~~~~~~~

1. **Connect ESP32-S3 to Computer:**
   
   * Use high-quality USB cable
   * Connect to USB port (not USB charging port)
   * Ensure ESP32-S3 is in download mode (may require holding BOOT button)

2. **Verify Connection:**

.. code-block:: bash

    # List available serial ports
    idf.py -p /dev/ttyUSB0 monitor  # Linux
    idf.py -p /dev/cu.usbserial-*   # macOS  
    idf.py -p COM3 monitor          # Windows

Flashing Process
~~~~~~~~~~~~~~

**Automatic Flashing:**

.. code-block:: bash

    # Flash with automatic port detection
    idf.py flash
    
    # Flash to specific port
    idf.py -p /dev/ttyUSB0 flash
    
    # Flash with higher baud rate (faster)
    idf.py -b 921600 flash

**Manual Flashing Steps:**

.. code-block:: bash

    # Erase flash (if needed)
    idf.py erase-flash
    
    # Flash bootloader, partition table, and application
    idf.py flash
    
    # Verify flash
    idf.py monitor

**First-Time Setup:**

.. code-block:: bash

    # Complete setup for new device
    idf.py erase-flash
    idf.py set-target esp32s3
    idf.py build
    idf.py flash

Monitoring and Debugging
~~~~~~~~~~~~~~~~~~~~~~~

**Serial Monitor:**

.. code-block:: bash

    # Start serial monitor
    idf.py monitor
    
    # Monitor with specific port and baud rate
    idf.py -p /dev/ttyUSB0 -b 115200 monitor
    
    # Exit monitor: Ctrl+]

**Debug Output Levels:**

Modify log levels in ``main/main.cpp``:

.. code-block:: c

    // Set global log level
    esp_log_level_set("*", ESP_LOG_INFO);
    
    // Set component-specific log levels
    esp_log_level_set("CarCan", ESP_LOG_DEBUG);
    esp_log_level_set("CarCanGui", ESP_LOG_VERBOSE);

Deployment Configurations
------------------------

Development Deployment
~~~~~~~~~~~~~~~~~~~~

For development and testing:

.. code-block:: bash

    # Enable debug features
    idf.py menuconfig
    # Component config -> Log output -> Default log verbosity -> Debug
    
    # Build and deploy
    idf.py build flash monitor

**Development Features:**
* Verbose logging enabled
* Debug symbols included
* Assertions enabled
* Stack overflow detection

Production Deployment
~~~~~~~~~~~~~~~~~~~

For production releases:

.. code-block:: bash

    # Configure for production
    idf.py menuconfig
    # Component config -> Log output -> Default log verbosity -> Warning
    # Compiler options -> Optimization Level -> Optimize for size (-Os)
    # Component config -> ESP32S3-Specific -> Enable secure boot (optional)

**Production Features:**
* Minimal logging
* Optimized for size and performance
* Security features enabled
* Stack overflow detection minimal

OTA (Over-The-Air) Updates
~~~~~~~~~~~~~~~~~~~~~~~~~

**OTA Partition Configuration:**

Modify ``partitions.csv`` for OTA support:

.. code-block::

    # Name,   Type, SubType, Offset,  Size, Flags
    nvs,      data, nvs,     0x9000,  0x6000,
    phy_init, data, phy,     0xf000,  0x1000,
    factory,  app,  factory, 0x10000, 1M,
    ota_0,    app,  ota_0,   0x110000,1M,
    ota_1,    app,  ota_1,   0x210000,1M,

**Enable OTA in Code:**

Add OTA capabilities to ``main/main.cpp``:

.. code-block:: c

    #include "esp_ota_ops.h"
    #include "esp_http_client.h"
    
    // OTA update function implementation
    void ota_update_task(void *pvParameter);

Testing and Validation
---------------------

Unit Testing
~~~~~~~~~~

**Component Tests:**

.. code-block:: bash

    # Run component unit tests
    idf.py build
    cd components/your_component
    idf.py test

**Custom Test Cases:**

Create test files in ``test/`` directory:

.. code-block:: c

    // test/test_can_controller.c
    #include "unity.h"
    #include "CarCanController.h"
    
    TEST_CASE("Test vehicle selection", "[can_controller]")
    {
        CarCanController controller;
        controller.setCurrentVehicle(VW_T7);
        TEST_ASSERT_EQUAL(VW_T7, controller.getCurrentVehicle());
    }

Integration Testing
~~~~~~~~~~~~~~~~~

**Hardware-in-the-Loop Testing:**

.. code-block:: bash

    # Flash test firmware
    idf.py -D SDKCONFIG_DEFAULTS="sdkconfig.test" build flash
    
    # Run automated tests
    python test/integration_tests.py

**CAN Bus Testing:**

.. code-block:: bash

    # Use CAN analyzer tools
    # - CANtact
    # - PCAN-USB
    # - SocketCAN (Linux)

Performance Testing
~~~~~~~~~~~~~~~~~

**Memory Usage Analysis:**

.. code-block:: bash

    # Analyze memory usage
    idf.py size
    idf.py size-components
    idf.py size-files

**Timing Analysis:**

Add timing measurements to code:

.. code-block:: c

    #include "esp_timer.h"
    
    int64_t start_time = esp_timer_get_time();
    // ... code to measure ...
    int64_t end_time = esp_timer_get_time();
    ESP_LOGI(TAG, "Execution time: %lld us", end_time - start_time);

Troubleshooting
--------------

Common Build Issues
~~~~~~~~~~~~~~~~~

**Missing Dependencies:**

.. code-block:: bash

    # Update submodules
    git submodule update --init --recursive
    
    # Clean and rebuild
    idf.py fullclean
    idf.py build

**Configuration Issues:**

.. code-block:: bash

    # Reset to defaults
    rm sdkconfig
    idf.py reconfigure
    
    # Check configuration
    idf.py show-efuse-table

**Memory Issues:**

.. code-block:: bash

    # Check partition sizes
    idf.py partition-table
    
    # Analyze memory usage
    idf.py size

Flash Issues
~~~~~~~~~~

**Connection Problems:**

.. code-block:: bash

    # Check device connection
    ls /dev/ttyUSB*  # Linux
    ls /dev/cu.*     # macOS
    
    # Try different baud rates
    idf.py -b 115200 flash

**Flash Corruption:**

.. code-block:: bash

    # Erase entire flash
    idf.py erase-flash
    
    # Re-flash bootloader
    idf.py bootloader-flash

Runtime Issues
~~~~~~~~~~~~

**System Crashes:**

.. code-block:: bash

    # Decode crash dump
    idf.py monitor
    # Copy crash dump and decode with:
    xtensa-esp32s3-elf-addr2line -pfiaC -e build/lvgl_porting.elf [ADDRESS]

**Performance Issues:**

.. code-block:: bash

    # Check CPU usage
    # Add task monitoring code
    vTaskGetRunTimeStats(buffer);
    ESP_LOGI(TAG, "Task stats:\n%s", buffer);

Advanced Features
----------------

Custom Bootloader
~~~~~~~~~~~~~~~

**Modify Bootloader:**

.. code-block:: bash

    # Enter bootloader directory
    cd $IDF_PATH/components/bootloader
    
    # Customize bootloader_start.c
    # Rebuild project
    idf.py bootloader

Secure Boot
~~~~~~~~~

**Enable Secure Boot:**

.. code-block:: bash

    # Configure secure boot
    idf.py menuconfig
    # Security features -> Enable hardware secure boot in bootloader
    
    # Generate keys
    idf.py secure-generate-flash-encryption-key my_flash_encryption_key.bin
    
    # Build with secure boot
    idf.py build

Flash Encryption
~~~~~~~~~~~~~~

**Enable Flash Encryption:**

.. code-block:: bash

    # Configure encryption
    idf.py menuconfig
    # Security features -> Enable flash encryption on boot
    
    # Build encrypted firmware
    idf.py build

Production Tools
--------------

Mass Production
~~~~~~~~~~~~~

**Automated Flashing:**

.. code-block:: bash

    #!/bin/bash
    # mass_flash.sh
    for port in /dev/ttyUSB*; do
        idf.py -p $port flash &
    done
    wait

**Factory Image Creation:**

.. code-block:: bash

    # Create factory image
    idf.py build
    esptool.py --chip esp32s3 merge_bin -o factory_image.bin \
        --flash_mode dio --flash_freq 80m --flash_size 8MB \
        0x0 build/bootloader/bootloader.bin \
        0x8000 build/partition_table/partition-table.bin \
        0x10000 build/lvgl_porting.bin

Quality Assurance
~~~~~~~~~~~~~~~

**Automated Testing:**

.. code-block:: python

    # test_automation.py
    import subprocess
    import time
    
    def test_device(port):
        # Flash firmware
        subprocess.run(['idf.py', '-p', port, 'flash'])
        
        # Run tests
        subprocess.run(['idf.py', '-p', port, 'monitor'])
    
    # Test multiple devices
    ports = ['/dev/ttyUSB0', '/dev/ttyUSB1']
    for port in ports:
        test_device(port)

Version Management
~~~~~~~~~~~~~~~~

**Firmware Versioning:**

Add version information to ``main/main.cpp``:

.. code-block:: c

    #define FIRMWARE_VERSION "1.0.0"
    #define BUILD_DATE __DATE__
    #define BUILD_TIME __TIME__
    
    ESP_LOGI(TAG, "Firmware Version: %s", FIRMWARE_VERSION);
    ESP_LOGI(TAG, "Build Date: %s %s", BUILD_DATE, BUILD_TIME);

**Git Integration:**

.. code-block:: bash

    # Add git hash to build
    echo "CONFIG_APP_PROJECT_VER=\"$(git describe --always)\"" >> sdkconfig

Continuous Integration
--------------------

GitHub Actions
~~~~~~~~~~~~

Create ``.github/workflows/build.yml``:

.. code-block:: yaml

    name: Build ESP32 Firmware
    
    on: [push, pull_request]
    
    jobs:
      build:
        runs-on: ubuntu-latest
        steps:
        - uses: actions/checkout@v2
          with:
            submodules: recursive
        
        - name: Setup ESP-IDF
          uses: espressif/esp-idf-ci-action@v1
          with:
            esp_idf_version: v5.0
        
        - name: Build firmware
          run: |
            idf.py set-target esp32s3
            idf.py build
        
        - name: Upload artifacts
          uses: actions/upload-artifact@v2
          with:
            name: firmware
            path: build/*.bin

Docker Build Environment
~~~~~~~~~~~~~~~~~~~~~~

Create ``Dockerfile``:

.. code-block:: dockerfile

    FROM espressif/idf:v5.0
    
    WORKDIR /project
    COPY . .
    
    RUN idf.py set-target esp32s3
    RUN idf.py build
    
    CMD ["idf.py", "build"]

**Usage:**

.. code-block:: bash

    # Build with Docker
    docker build -t esp32-can-controller .
    docker run --rm -v $(pwd):/project esp32-can-controller