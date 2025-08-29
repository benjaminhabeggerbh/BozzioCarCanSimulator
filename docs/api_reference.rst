API Reference
=============

This section provides detailed documentation for all classes, functions, and interfaces in the ESP32 CAN Bus Vehicle Controller project.

Core Classes
-----------

CarCanController
~~~~~~~~~~~~~~~

The main controller class that manages vehicle state and CAN bus communication.

**Header File:** ``main/CarCanController.h``

Class Declaration
^^^^^^^^^^^^^^^

.. code-block:: cpp

    class CarCanController {
    public:
        CarCanController();
        void btnCallback(button_id_t button);
        ButtonMap getButtonMap();
        void startCan();
        button_id_t getCurrentVehicle() const;
        void setCurrentVehicle(button_id_t vehicle);
        
        // Speed control (0-250 km/h)
        void setSpeed(uint8_t speed_kmh);
        uint8_t getSpeed() const;
        
        // Gear control
        void setGear(Gear gear);
        Gear getGear() const;

        // Message generation
        bool hasMessageGenerator() const;
        void sendPeriodicMessages();
        CarCanMessageGenerator message_generator;
        
    private:
        ButtonMap button_map;
        button_id_t current_vehicle;
        uint8_t current_speed_kmh;
        Gear current_gear;
    };

Constructor
^^^^^^^^^^^

**CarCanController()**

Initializes the controller with default values and sets up the button mapping for supported vehicles.

* **Parameters:** None
* **Returns:** None
* **Default Values:**
  * Current vehicle: ``VW_T7``
  * Current speed: ``0 km/h``
  * Current gear: ``Gear::PARK``

Public Methods
^^^^^^^^^^^^^

**void btnCallback(button_id_t button)**

Handles button press events from the GUI, typically used for vehicle selection.

* **Parameters:**
  * ``button`` - The button identifier that was pressed
* **Returns:** ``void``
* **Side Effects:** Updates current vehicle selection and logs the change

**ButtonMap getButtonMap()**

Returns the mapping of button IDs to their display labels.

* **Parameters:** None
* **Returns:** ``ButtonMap`` - Map containing vehicle button definitions
* **Usage:** Used by GUI to populate vehicle selection dropdown

**void startCan()**

Initializes and starts the CAN bus communication tasks.

* **Parameters:** None
* **Returns:** ``void``
* **Side Effects:** 
  * Creates TWAI transmission task
  * Creates TWAI reception task
  * Initializes CAN driver

**button_id_t getCurrentVehicle() const**

Gets the currently selected vehicle type.

* **Parameters:** None
* **Returns:** ``button_id_t`` - Current vehicle identifier
* **Thread Safety:** Read-only, safe for concurrent access

**void setCurrentVehicle(button_id_t vehicle)**

Sets the current vehicle type if it exists in the button map.

* **Parameters:**
  * ``vehicle`` - Vehicle identifier to select
* **Returns:** ``void``
* **Validation:** Checks if vehicle exists in button map before setting

**void setSpeed(uint8_t speed_kmh)**

Sets the target speed for CAN message generation.

* **Parameters:**
  * ``speed_kmh`` - Speed in kilometers per hour (0-250)
* **Returns:** ``void``
* **Validation:** Ensures speed is within valid range (0-250 km/h)

**uint8_t getSpeed() const**

Gets the current target speed setting.

* **Parameters:** None
* **Returns:** ``uint8_t`` - Current speed in km/h
* **Range:** 0-250 km/h

**void setGear(Gear gear)**

Sets the target gear position for CAN message generation.

* **Parameters:**
  * ``gear`` - Target gear position (PARK, REVERSE, NEUTRAL, DRIVE)
* **Returns:** ``void``
* **Side Effects:** Updates internal gear state

**Gear getGear() const**

Gets the current gear position setting.

* **Parameters:** None
* **Returns:** ``Gear`` - Current gear position
* **Thread Safety:** Read-only, safe for concurrent access

**bool hasMessageGenerator() const**

Checks if the current vehicle has message generation support.

* **Parameters:** None
* **Returns:** ``bool`` - True if message generation is supported
* **Usage:** GUI can disable features for unsupported vehicles

**void sendPeriodicMessages()**

Sends periodic CAN messages based on current vehicle state.

* **Parameters:** None
* **Returns:** ``void``
* **Side Effects:** Transmits speed and gear messages via CAN bus

CarCanGui
~~~~~~~~

The user interface class that manages LVGL-based GUI components.

**Header File:** ``main/CarCanGui.h``

Class Declaration
^^^^^^^^^^^^^^^

.. code-block:: cpp

    class CarCanGui {
    public:
        CarCanGui(CarCanController& controller);
        void createGui();

    private:
        lv_obj_t *container;
        lv_obj_t *dropdown;
        lv_obj_t *speed_slider;
        lv_obj_t *speed_label;
        lv_obj_t *gear_buttons[4];  // P, R, N, D buttons
        CarCanController& controller;
        ButtonMap button_map;
        
        void createVehicleSelector();
        void createSpeedControl();
        void createGearControl();
        
        static void dropdown_event_handler(lv_event_t * e);
        static void speed_event_handler(lv_event_t * e);
        static void gear_event_handler(lv_event_t * e);
    };

Constructor
^^^^^^^^^^^

**CarCanGui(CarCanController& controller)**

Initializes the GUI with a reference to the controller and retrieves button mappings.

* **Parameters:**
  * ``controller`` - Reference to the main controller instance
* **Returns:** None
* **Side Effects:** Sets up internal references and copies button map

Public Methods
^^^^^^^^^^^^^

**void createGui()**

Creates and initializes all GUI components on the active screen.

* **Parameters:** None
* **Returns:** ``void``
* **Side Effects:**
  * Creates main container (800x400 pixels)
  * Creates vehicle selector dropdown
  * Creates speed control slider
  * Creates gear selection buttons
  * Centers container on screen

Private Methods
^^^^^^^^^^^^^^

**void createVehicleSelector()**

Creates the dropdown menu for vehicle selection.

* **Parameters:** None
* **Returns:** ``void``
* **Implementation Details:**
  * Populates dropdown with vehicle labels from button map
  * Sets initial selection to match controller state
  * Registers event handler for selection changes

**void createSpeedControl()**

Creates the speed control slider and associated label.

* **Parameters:** None
* **Returns:** ``void``
* **Implementation Details:**
  * Creates slider with range 0-250
  * Creates dynamic label showing current speed
  * Registers event handler for slider changes

**void createGearControl()**

Creates the gear selection buttons (P, R, N, D).

* **Parameters:** None
* **Returns:** ``void``
* **Implementation Details:**
  * Creates four buttons in a row
  * Sets button labels and styles
  * Registers event handlers for button presses

Static Event Handlers
^^^^^^^^^^^^^^^^^^^

**static void dropdown_event_handler(lv_event_t * e)**

Handles vehicle selection dropdown events.

* **Parameters:**
  * ``e`` - LVGL event structure
* **Returns:** ``void``
* **Functionality:**
  * Retrieves selected vehicle index
  * Maps index to vehicle ID
  * Calls controller to update vehicle selection

**static void speed_event_handler(lv_event_t * e)**

Handles speed slider change events.

* **Parameters:**
  * ``e`` - LVGL event structure
* **Returns:** ``void``
* **Functionality:**
  * Retrieves slider value (0-250)
  * Updates speed label display
  * Calls controller to update speed setting

**static void gear_event_handler(lv_event_t * e)**

Handles gear button press events.

* **Parameters:**
  * ``e`` - LVGL event structure
* **Returns:** ``void``
* **Functionality:**
  * Identifies which gear button was pressed
  * Maps button to gear enum value
  * Calls controller to update gear setting

CarCanMessageGenerator
~~~~~~~~~~~~~~~~~~~~~

The message generation class that handles vehicle-specific CAN protocols.

**Header File:** ``main/CarCanMessageGenerator.h``

Class Declaration
^^^^^^^^^^^^^^^

.. code-block:: cpp

    class CarCanMessageGenerator {
    public:
        CarCanMessageGenerator();
        
        void generateSpeedMessage(button_id_t vehicle, uint8_t speed_kmh, 
                                uint8_t* data, uint8_t& dlc);
        void generateGearMessage(button_id_t vehicle, Gear gear, 
                               uint8_t* data, uint8_t& dlc);
        std::vector<uint32_t> getRequiredMessageIds(button_id_t vehicle) const;
        uint32_t getCANBaudRate(button_id_t vehicle) const;
        bool hasSupport(button_id_t vehicle) const;

    private:
        std::map<button_id_t, VehicleCanConfig> vehicle_configs;
        void initializeVehicleConfigs();

        // Common message generation functions
        static void generateVWSpeedMessage(float speed_factor, uint8_t speed_kmh, 
                                         uint8_t* data, uint8_t& dlc);
        static void generateVWGearMessage(uint8_t* data, uint8_t& dlc, Gear gear);
    };

Constructor
^^^^^^^^^^^

**CarCanMessageGenerator()**

Initializes the message generator and loads vehicle configurations.

* **Parameters:** None
* **Returns:** None
* **Side Effects:** Calls ``initializeVehicleConfigs()`` to set up vehicle protocols

Public Methods
^^^^^^^^^^^^^

**void generateSpeedMessage(button_id_t vehicle, uint8_t speed_kmh, uint8_t* data, uint8_t& dlc)**

Generates a speed CAN message for the specified vehicle type.

* **Parameters:**
  * ``vehicle`` - Target vehicle type
  * ``speed_kmh`` - Speed value in km/h (0-250)
  * ``data`` - Output buffer for CAN message data (8 bytes)
  * ``dlc`` - Output parameter for data length code
* **Returns:** ``void``
* **Preconditions:** Vehicle must have configured message generator
* **Postconditions:** ``data`` contains vehicle-specific speed message, ``dlc`` set to message length

**void generateGearMessage(button_id_t vehicle, Gear gear, uint8_t* data, uint8_t& dlc)**

Generates a gear position CAN message for the specified vehicle type.

* **Parameters:**
  * ``vehicle`` - Target vehicle type
  * ``gear`` - Target gear position
  * ``data`` - Output buffer for CAN message data (8 bytes)
  * ``dlc`` - Output parameter for data length code
* **Returns:** ``void``
* **Preconditions:** Vehicle must have configured message generator
* **Postconditions:** ``data`` contains vehicle-specific gear message, ``dlc`` set to message length

**std::vector<uint32_t> getRequiredMessageIds(button_id_t vehicle) const**

Returns the list of CAN message IDs required for the specified vehicle.

* **Parameters:**
  * ``vehicle`` - Target vehicle type
* **Returns:** ``std::vector<uint32_t>`` - List of CAN message IDs
* **Usage:** Used for CAN filter configuration

**uint32_t getCANBaudRate(button_id_t vehicle) const**

Returns the required CAN bus baud rate for the specified vehicle.

* **Parameters:**
  * ``vehicle`` - Target vehicle type
* **Returns:** ``uint32_t`` - Baud rate in bits per second
* **Common Values:** 500000 (500 kbps) for most automotive applications

**bool hasSupport(button_id_t vehicle) const**

Checks if the specified vehicle type has message generation support.

* **Parameters:**
  * ``vehicle`` - Vehicle type to check
* **Returns:** ``bool`` - True if vehicle is supported
* **Usage:** Used by GUI to enable/disable features

Private Methods
^^^^^^^^^^^^^^

**void initializeVehicleConfigs()**

Initializes the vehicle configuration map with supported vehicles and their protocols.

* **Parameters:** None
* **Returns:** ``void``
* **Implementation:** Sets up ``VehicleCanConfig`` structures for each supported vehicle

**static void generateVWSpeedMessage(float speed_factor, uint8_t speed_kmh, uint8_t* data, uint8_t& dlc)**

Generates speed messages using Volkswagen protocol format.

* **Parameters:**
  * ``speed_factor`` - Speed scaling factor (typically 0.01)
  * ``speed_kmh`` - Speed in km/h
  * ``data`` - Output message buffer
  * ``dlc`` - Output data length (set to 8)
* **Returns:** ``void``
* **Protocol:** Places scaled speed value in bytes 4-5 of message

**static void generateVWGearMessage(uint8_t* data, uint8_t& dlc, Gear gear)**

Generates gear messages using Volkswagen protocol format.

* **Parameters:**
  * ``data`` - Output message buffer
  * ``dlc`` - Output data length (set to 8)
  * ``gear`` - Target gear position
* **Returns:** ``void``
* **Protocol:** Places gear value in byte 5 of message

Data Types and Enumerations
--------------------------

button_id_t
~~~~~~~~~~

Enumeration of supported vehicle types.

.. code-block:: cpp

    enum button_id_t {
        VW_T5 = 1,
        VW_T6 = 2,
        VW_T61 = 3,
        VW_T7 = 4,
        MB_SPRINTER = 5,
        MB_SPRINTER_2023 = 6,
        JEEP_RENEGADE = 7,
        JEEP_RENEGADE_MHEV = 8,
        MB_VIANO = 9
    };

**Values:**

* ``VW_T5`` - Volkswagen T5 van
* ``VW_T6`` - Volkswagen T6 van  
* ``VW_T61`` - Volkswagen T6.1 van
* ``VW_T7`` - Volkswagen T7 van
* ``MB_SPRINTER`` - Mercedes Sprinter van
* ``MB_SPRINTER_2023`` - Mercedes Sprinter 2023+ model
* ``JEEP_RENEGADE`` - Jeep Renegade
* ``JEEP_RENEGADE_MHEV`` - Jeep Renegade MHEV (Mild Hybrid)
* ``MB_VIANO`` - Mercedes Viano

Gear
~~~

Enumeration of transmission gear positions.

.. code-block:: cpp

    enum class Gear {
        PARK,
        REVERSE,
        NEUTRAL,
        DRIVE
    };

**Values:**

* ``PARK`` - Park position (P)
* ``REVERSE`` - Reverse gear (R)
* ``NEUTRAL`` - Neutral position (N)
* ``DRIVE`` - Drive mode (D)

ButtonEntry
~~~~~~~~~~

Structure containing display information for vehicle buttons.

.. code-block:: cpp

    struct ButtonEntry {
        const char* label;
    };

**Members:**

* ``label`` - Display text for the vehicle type

ButtonMap
~~~~~~~~

Type alias for mapping vehicle IDs to their display information.

.. code-block:: cpp

    using ButtonMap = std::map<button_id_t, ButtonEntry>;

VehicleCanConfig
~~~~~~~~~~~~~~~

Structure containing CAN protocol configuration for a specific vehicle.

.. code-block:: cpp

    struct VehicleCanConfig {
        uint32_t speed_msg_id;
        uint32_t gear_msg_id;
        uint32_t baud_rate;
        SpeedMessageGenerator speed_generator;
        GearMessageGenerator gear_generator;
    };

**Members:**

* ``speed_msg_id`` - CAN identifier for speed messages
* ``gear_msg_id`` - CAN identifier for gear messages
* ``baud_rate`` - Required CAN bus speed in bps
* ``speed_generator`` - Function to generate speed messages
* ``gear_generator`` - Function to generate gear messages

Function Types
~~~~~~~~~~~~~

**SpeedMessageGenerator**

.. code-block:: cpp

    using SpeedMessageGenerator = std::function<void(uint8_t speed_kmh, uint8_t* data, uint8_t& dlc)>;

Function type for generating vehicle-specific speed messages.

**GearMessageGenerator**

.. code-block:: cpp

    using GearMessageGenerator = std::function<void(Gear gear, uint8_t* data, uint8_t& dlc)>;

Function type for generating vehicle-specific gear messages.

Hardware Abstraction Functions
-----------------------------

CAN/TWAI Functions
~~~~~~~~~~~~~~~~

**void send_can_message(uint32_t message_id, uint8_t* data, uint8_t dlc)**

Sends a CAN message via the TWAI driver.

* **Parameters:**
  * ``message_id`` - CAN identifier (11-bit or 29-bit)
  * ``data`` - Message data buffer
  * ``dlc`` - Data length code (0-8)
* **Returns:** ``void``
* **Implementation:** Uses ESP-IDF TWAI driver for transmission

**void twai_task(void *pvParameter)**

FreeRTOS task for handling CAN message transmission.

* **Parameters:**
  * ``pvParameter`` - Task parameter (typically controller instance)
* **Returns:** ``void`` (never returns)
* **Functionality:** Manages periodic message transmission

**void twai_receive_task(void *pvParameter)**

FreeRTOS task for handling CAN message reception.

* **Parameters:**
  * ``pvParameter`` - Task parameter
* **Returns:** ``void`` (never returns)
* **Functionality:** Receives and processes incoming CAN messages

Display Functions
~~~~~~~~~~~~~~~

**void waveshare_esp32_s3_rgb_lcd_init()**

Initializes the Waveshare RGB LCD display hardware.

* **Parameters:** None
* **Returns:** ``void``
* **Side Effects:** Configures GPIO pins, initializes display driver
* **Implementation:** Located in ``waveshare_rgb_lcd_port.c``

LVGL Integration Functions
~~~~~~~~~~~~~~~~~~~~~~~~

**void gui_main(const ButtonMap& buttons)**

Main GUI initialization function (legacy interface).

* **Parameters:**
  * ``buttons`` - Button mapping for vehicle selection
* **Returns:** ``void``
* **Note:** This function is legacy; new code should use ``CarCanGui`` class

Constants and Configuration
--------------------------

CAN Configuration
~~~~~~~~~~~~~~~

.. code-block:: cpp

    #define CAN_BAUDRATE_500K    500000  // Standard automotive CAN speed
    #define CAN_BAUDRATE_250K    250000  // Alternative CAN speed
    #define CAN_BAUDRATE_125K    125000  // Low-speed CAN

Display Configuration
~~~~~~~~~~~~~~~~~~~

.. code-block:: cpp

    #define LCD_H_RES            800     // Horizontal resolution
    #define LCD_V_RES            480     // Vertical resolution
    #define LCD_BIT_PER_PIXEL    16      // Color depth (RGB565)

Speed Limits
~~~~~~~~~~

.. code-block:: cpp

    #define MIN_SPEED_KMH        0       // Minimum speed setting
    #define MAX_SPEED_KMH        250     // Maximum speed setting

Error Codes
----------

The system uses ESP-IDF standard error codes plus some custom error definitions:

CAN Communication Errors
~~~~~~~~~~~~~~~~~~~~~~~

* ``ESP_OK`` - Operation successful
* ``ESP_ERR_INVALID_ARG`` - Invalid parameter provided
* ``ESP_ERR_TIMEOUT`` - CAN transmission timeout
* ``ESP_FAIL`` - General CAN operation failure

GUI Errors
~~~~~~~~~

* ``ESP_ERR_NO_MEM`` - Insufficient memory for GUI components
* ``ESP_ERR_INVALID_STATE`` - GUI not properly initialized

Vehicle Configuration Errors
~~~~~~~~~~~~~~~~~~~~~~~~~~~

* ``ESP_ERR_NOT_FOUND`` - Vehicle type not supported
* ``ESP_ERR_NOT_SUPPORTED`` - Feature not available for vehicle

Usage Examples
-------------

Basic Controller Usage
~~~~~~~~~~~~~~~~~~~~

.. code-block:: cpp

    // Initialize controller
    CarCanController controller;
    
    // Set vehicle type
    controller.setCurrentVehicle(VW_T7);
    
    // Set speed and gear
    controller.setSpeed(50);  // 50 km/h
    controller.setGear(Gear::DRIVE);
    
    // Start CAN communication
    controller.startCan();

GUI Integration
~~~~~~~~~~~~~

.. code-block:: cpp

    // Initialize display hardware
    waveshare_esp32_s3_rgb_lcd_init();
    
    // Create controller and GUI
    CarCanController controller;
    CarCanGui gui(controller);
    
    // Create GUI components
    gui.createGui();
    
    // Start CAN communication
    controller.startCan();

Message Generation
~~~~~~~~~~~~~~~~

.. code-block:: cpp

    CarCanMessageGenerator generator;
    uint8_t data[8];
    uint8_t dlc;
    
    // Generate speed message for VW T7
    generator.generateSpeedMessage(VW_T7, 100, data, dlc);
    
    // Send via CAN
    send_can_message(0x0FD, data, dlc);

Thread Safety
------------

The system is designed for multi-threaded operation with the following considerations:

Thread-Safe Operations
~~~~~~~~~~~~~~~~~~~~

* Reading current vehicle, speed, and gear state
* Message generation functions (stateless)
* CAN message transmission and reception

Non-Thread-Safe Operations
~~~~~~~~~~~~~~~~~~~~~~~~~

* Modifying vehicle, speed, or gear state
* GUI component creation and modification
* Vehicle configuration changes

Synchronization Recommendations
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* Use FreeRTOS mutexes for state modifications
* Implement message queues for inter-task communication
* Use atomic operations for simple flag variables

Performance Considerations
-------------------------

Memory Usage
~~~~~~~~~~

* **Static Memory**: ~50KB for code and constants
* **Dynamic Memory**: ~100KB for GUI components and buffers
* **Stack Memory**: ~16KB total for all tasks

Timing Requirements
~~~~~~~~~~~~~~~~~

* **GUI Responsiveness**: <100ms for touch events
* **CAN Message Timing**: Configurable, typically 10-100ms intervals
* **Display Refresh**: 60 FPS for smooth operation

Optimization Tips
~~~~~~~~~~~~~~~

* Use static allocation where possible
* Minimize dynamic memory allocation in ISRs
* Cache frequently accessed configuration data
* Use DMA for display operations when available