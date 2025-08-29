Getting Started
===============

This guide will help you quickly set up and run the ESP32 CAN Bus Vehicle Controller. Follow these steps to get your system operational.

Quick Start
----------

Prerequisites Checklist
~~~~~~~~~~~~~~~~~~~~~~

Before you begin, ensure you have:

- [ ] ESP32-S3 development board
- [ ] USB cable for programming
- [ ] Computer with Linux, macOS, or Windows
- [ ] Internet connection for downloading dependencies

**Optional (for full functionality):**

- [ ] Waveshare RGB LCD display (800x480)
- [ ] CAN transceiver board
- [ ] Vehicle with CAN bus access (OBD-II port)

30-Second Setup
~~~~~~~~~~~~~

For experienced developers who want to jump right in:

.. code-block:: bash

    # 1. Install ESP-IDF v5.0+
    git clone --recursive https://github.com/espressif/esp-idf.git
    cd esp-idf && ./install.sh esp32s3 && . ./export.sh
    
    # 2. Clone and build project
    git clone <repository-url> esp32-can-controller
    cd esp32-can-controller
    idf.py set-target esp32s3
    idf.py build
    
    # 3. Flash to device
    idf.py flash monitor

Step-by-Step Installation
-----------------------

Step 1: Install ESP-IDF
~~~~~~~~~~~~~~~~~~~~~~

**Linux/macOS:**

.. code-block:: bash

    # Download ESP-IDF
    cd ~/
    git clone --recursive https://github.com/espressif/esp-idf.git
    cd esp-idf
    git checkout v5.0
    
    # Install dependencies
    ./install.sh esp32s3
    
    # Set up environment (add to ~/.bashrc for persistence)
    . ./export.sh

**Windows:**

1. Download the ESP-IDF Windows installer from `Espressif's website <https://docs.espressif.com/projects/esp-idf/en/latest/esp32/get-started/windows-setup.html>`_
2. Run the installer and select ESP32-S3 support
3. Open ESP-IDF Command Prompt from Start Menu

**Verification:**

.. code-block:: bash

    idf.py --version
    # Should output: ESP-IDF v5.0 or later

Step 2: Download Project
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

    # Clone the repository
    git clone <repository-url> esp32-can-controller
    cd esp32-can-controller
    
    # Initialize submodules
    git submodule update --init --recursive

Step 3: Configure Project
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

    # Set target chip
    idf.py set-target esp32s3
    
    # Optional: Configure project settings
    idf.py menuconfig

**Key configuration options:**

- **Flash size**: Set to 8MB or 16MB in "Serial flasher config"
- **Touch controller**: Enable GT911 in "Example Configuration" if using touch
- **Debug level**: Set logging verbosity in "Component config > Log output"

Step 4: Build Project
~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

    # Build the firmware
    idf.py build

This creates the firmware files in the ``build/`` directory:

- ``lvgl_porting.bin`` - Main application
- ``bootloader/bootloader.bin`` - System bootloader
- ``partition_table/partition-table.bin`` - Memory layout

Step 5: Connect Hardware
~~~~~~~~~~~~~~~~~~~~~~

1. **Connect ESP32-S3 to computer** via USB cable
2. **Check connection:**

.. code-block:: bash

    # Linux
    ls /dev/ttyUSB* /dev/ttyACM*
    
    # macOS
    ls /dev/cu.usbserial* /dev/cu.usbmodem*
    
    # Windows (in Command Prompt)
    mode

3. **Put ESP32-S3 in download mode** (may require holding BOOT button while pressing RESET)

Step 6: Flash Firmware
~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

    # Flash with automatic port detection
    idf.py flash
    
    # Or specify port manually
    idf.py -p /dev/ttyUSB0 flash  # Linux
    idf.py -p COM3 flash           # Windows

Step 7: Test Operation
~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

    # Start serial monitor to see output
    idf.py monitor
    
    # Expected output:
    # I (xxx) APP_MAIN: Starting application...
    # I (xxx) CarCan: Selected vehicle: VW T7
    # ...

Press ``Ctrl+]`` to exit the monitor.

First Run Experience
------------------

What You Should See
~~~~~~~~~~~~~~~~~

When the system boots successfully, you should observe:

**Serial Output:**
- Boot messages from ESP-IDF
- Application startup logs
- Vehicle controller initialization
- GUI system startup

**Display (if connected):**
- Black screen briefly during initialization
- GUI interface appears with:
  - Vehicle selection dropdown (defaulting to "VW T7")
  - Speed slider (0-250 km/h)
  - Gear selection buttons (P, R, N, D)

**Default State:**
- Selected vehicle: VW T7
- Speed: 0 km/h
- Gear: Park (P)

Basic Usage
~~~~~~~~~

**Using the GUI (with display):**

1. **Select Vehicle**: Tap the dropdown menu to choose your vehicle type
2. **Set Speed**: Drag the speed slider to set desired speed (0-250 km/h)
3. **Select Gear**: Tap P, R, N, or D buttons to change gear position
4. **Monitor Output**: Check serial console for CAN message generation

**Using Serial Commands (development):**

The system supports serial commands for testing:

.. code-block:: bash

    # In the monitor, type commands:
    set_vehicle 4      # Set to VW T7 (ID 4)
    set_speed 50       # Set speed to 50 km/h
    set_gear 3         # Set gear to Drive (3)

Hardware Setup Options
--------------------

Minimal Setup (Development)
~~~~~~~~~~~~~~~~~~~~~~~~~

For software development and testing without full hardware:

**Required:**
- ESP32-S3 development board
- USB cable

**Features Available:**
- Serial console interface
- CAN message generation (in software)
- Core functionality testing

**Limitations:**
- No visual GUI (serial commands only)
- No actual CAN bus communication
- No touch interface

Basic Display Setup
~~~~~~~~~~~~~~~~~~

For GUI development and demonstration:

**Required:**
- ESP32-S3 development board
- Waveshare RGB LCD display
- Connection cables

**Features Available:**
- Full GUI interface
- Touch interaction (if GT911 enabled)
- Visual feedback and control

**Limitations:**
- No CAN bus communication
- No vehicle integration

Full System Setup
~~~~~~~~~~~~~~~

For complete functionality and vehicle integration:

**Required:**
- ESP32-S3 development board
- Waveshare RGB LCD display
- CAN transceiver board
- Vehicle with CAN bus access

**Features Available:**
- Complete GUI interface
- Real CAN bus communication
- Vehicle integration
- Full feature set

Configuration Examples
--------------------

Development Configuration
~~~~~~~~~~~~~~~~~~~~~~~~

For software development without hardware:

.. code-block:: bash

    idf.py menuconfig
    
    # Disable touch controller
    Example Configuration → LCD Touch Controller → Disable GT911
    
    # Enable verbose logging
    Component config → Log output → Default log verbosity → Debug
    
    # Disable CAN (if no transceiver)
    # Edit main/main.cpp and comment out controller.startCan();

Production Configuration
~~~~~~~~~~~~~~~~~~~~~~

For deployment in vehicles:

.. code-block:: bash

    idf.py menuconfig
    
    # Enable touch controller
    Example Configuration → LCD Touch Controller → Enable GT911
    
    # Minimize logging
    Component config → Log output → Default log verbosity → Warning
    
    # Optimize for size
    Compiler options → Optimization Level → Optimize for size (-Os)

Testing Configuration
~~~~~~~~~~~~~~~~~~~

For comprehensive testing:

.. code-block:: bash

    idf.py menuconfig
    
    # Maximum logging
    Component config → Log output → Default log verbosity → Verbose
    
    # Debug optimization
    Compiler options → Optimization Level → Debug (-Og)
    
    # Enable all features
    Example Configuration → Enable all options

Common Issues and Solutions
-------------------------

Build Issues
~~~~~~~~~~

**Issue: "idf.py command not found"**

.. code-block:: bash

    # Solution: Set up ESP-IDF environment
    . ~/esp/esp-idf/export.sh

**Issue: "Target 'esp32s3' not found"**

.. code-block:: bash

    # Solution: Set target explicitly
    idf.py set-target esp32s3

**Issue: Submodule errors**

.. code-block:: bash

    # Solution: Update submodules
    git submodule update --init --recursive

Flashing Issues
~~~~~~~~~~~~~

**Issue: "Failed to connect to ESP32-S3"**

Solutions:
1. Hold BOOT button while pressing RESET
2. Try different USB cable
3. Check USB port permissions (Linux: add user to dialout group)
4. Try lower baud rate: ``idf.py -b 115200 flash``

**Issue: "Permission denied" (Linux)**

.. code-block:: bash

    # Solution: Add user to dialout group
    sudo usermod -a -G dialout $USER
    # Logout and login again

Runtime Issues
~~~~~~~~~~~~

**Issue: Black screen on display**

Solutions:
1. Check display power connections (5V)
2. Verify RGB cable connections
3. Check GPIO pin assignments in code
4. Test with simple display example first

**Issue: No CAN messages**

Solutions:
1. Verify CAN transceiver power
2. Check CANH/CANL connections
3. Ensure 120Ω termination resistors
4. Verify vehicle CAN bus compatibility

**Issue: Touch not working**

Solutions:
1. Enable GT911 in menuconfig
2. Check I2C connections (SDA, SCL)
3. Verify touch controller power (3.3V)
4. Run touch calibration

Next Steps
---------

Once you have the basic system running:

1. **Explore the GUI**: Try different vehicle selections and settings
2. **Read the Documentation**: Review the software architecture and API reference
3. **Hardware Integration**: Connect CAN transceiver and test with a vehicle
4. **Customization**: Modify vehicle configurations for your specific needs
5. **Development**: Add new features or vehicle support

Useful Resources
--------------

- **ESP-IDF Documentation**: https://docs.espressif.com/projects/esp-idf/
- **LVGL Documentation**: https://docs.lvgl.io/
- **Hardware Setup Guide**: See ``hardware_setup.rst`` in this documentation
- **API Reference**: See ``api_reference.rst`` for detailed class documentation
- **Build Guide**: See ``build_deployment.rst`` for advanced build options

Support and Community
--------------------

If you encounter issues:

1. **Check the Troubleshooting section** in ``build_deployment.rst``
2. **Review the Hardware Setup guide** for connection issues
3. **Enable debug logging** to get more detailed error messages
4. **Check ESP-IDF GitHub issues** for known problems
5. **Search LVGL documentation** for GUI-related issues

Development Workflow
------------------

Recommended development workflow:

1. **Start with minimal setup** (ESP32-S3 only)
2. **Add display** for GUI development
3. **Add CAN transceiver** for communication testing
4. **Test with vehicle** for integration validation
5. **Optimize for production** when ready to deploy

This progressive approach helps isolate issues and ensures each component works before adding complexity.

Example Development Session
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

    # Terminal 1: Build and flash
    cd esp32-can-controller
    . ~/esp/esp-idf/export.sh
    idf.py build flash
    
    # Terminal 2: Monitor output
    idf.py monitor
    
    # Make code changes, then in Terminal 1:
    idf.py build flash
    
    # Monitor automatically restarts to show new output

This workflow provides fast iteration cycles for development.