Software Architecture
===================

The ESP32 CAN Bus Vehicle Controller follows a layered architecture design that separates concerns and enables maintainable, extensible code. This document describes the overall system architecture, key components, and their interactions.

System Overview
--------------

The application is structured in three primary layers:

1. **Hardware Abstraction Layer (HAL)**: Platform-specific drivers and hardware interfaces
2. **Business Logic Layer**: Core application logic, CAN message handling, and vehicle control
3. **Presentation Layer**: User interface and interaction handling

.. code-block::

    ┌─────────────────────────────────────────────────────────┐
    │                 Presentation Layer                      │
    │  ┌─────────────────┐  ┌─────────────────────────────┐  │
    │  │   CarCanGui     │  │      LVGL Framework         │  │
    │  │   (Touch UI)    │  │   (Graphics & Events)      │  │
    │  └─────────────────┘  └─────────────────────────────┘  │
    └─────────────────────────────────────────────────────────┘
                                    │
    ┌─────────────────────────────────────────────────────────┐
    │                Business Logic Layer                     │
    │  ┌─────────────────┐  ┌─────────────────────────────┐  │
    │  │ CarCanController│  │   CarCanMessageGenerator   │  │
    │  │  (State Mgmt)   │  │    (Protocol Handlers)     │  │
    │  └─────────────────┘  └─────────────────────────────┘  │
    └─────────────────────────────────────────────────────────┘
                                    │
    ┌─────────────────────────────────────────────────────────┐
    │              Hardware Abstraction Layer                │
    │  ┌─────────────────┐  ┌─────────────────────────────┐  │
    │  │   TWAI Driver   │  │    LCD/Touch Drivers        │  │
    │  │  (CAN Bus)      │  │   (Display Interface)       │  │
    │  └─────────────────┘  └─────────────────────────────┘  │
    └─────────────────────────────────────────────────────────┘

Core Components
--------------

CarCanController
~~~~~~~~~~~~~~~

The `CarCanController` class serves as the central coordinator for the entire system. It manages:

* **Vehicle State Management**: Current vehicle type, speed, and gear position
* **CAN Bus Communication**: Initialization and management of TWAI (CAN) driver
* **Message Coordination**: Integration with message generators for vehicle-specific protocols
* **System Configuration**: Button mappings and vehicle selection

**Key Responsibilities:**

* Initialize and start CAN bus communication
* Maintain current vehicle state (speed, gear, selected vehicle)
* Coordinate with GUI for user interactions
* Delegate message generation to appropriate handlers

**File Location:** ``main/CarCanController.h``, ``main/CarCanController.cpp``

CarCanGui
~~~~~~~~

The `CarCanGui` class implements the user interface using the LVGL graphics library. It provides:

* **Vehicle Selection**: Dropdown menu for choosing target vehicle type
* **Speed Control**: Slider interface for setting speed (0-250 km/h)
* **Gear Selection**: Button interface for gear selection (P/R/N/D)
* **Real-time Feedback**: Dynamic updates based on controller state

**Key Responsibilities:**

* Create and manage LVGL UI components
* Handle user input events (touch, slider changes)
* Communicate state changes to the controller
* Update display based on system state

**File Location:** ``main/CarCanGui.h``, ``main/CarCanGui.cpp``

CarCanMessageGenerator
~~~~~~~~~~~~~~~~~~~~~

The `CarCanMessageGenerator` class provides a pluggable architecture for vehicle-specific CAN message generation:

* **Protocol Abstraction**: Common interface for different vehicle protocols
* **Message Generation**: Speed and gear messages for each supported vehicle
* **Configuration Management**: Vehicle-specific message IDs and parameters
* **Extensibility**: Easy addition of new vehicle types

**Key Responsibilities:**

* Generate vehicle-specific CAN messages
* Manage message IDs and protocol parameters
* Provide unified interface for different vehicle types
* Support runtime vehicle switching

**File Location:** ``main/CarCanMessageGenerator.h``, ``main/CarCanMessageGenerator.cpp``

Data Flow Architecture
---------------------

User Interaction Flow
~~~~~~~~~~~~~~~~~~~

1. **User Input**: Touch events on GUI components (dropdown, slider, buttons)
2. **Event Processing**: LVGL processes touch events and calls registered callbacks
3. **State Update**: GUI callbacks update controller state via method calls
4. **Message Generation**: Controller triggers appropriate message generation
5. **CAN Transmission**: Generated messages are sent via TWAI driver
6. **UI Feedback**: GUI updates to reflect current state

CAN Message Flow
~~~~~~~~~~~~~~~

1. **Configuration**: Message generator configures vehicle-specific parameters
2. **State Request**: Controller requests message generation with current state
3. **Message Creation**: Generator creates binary CAN message data
4. **Transmission**: TWAI driver sends message on CAN bus
5. **Periodic Updates**: System maintains periodic message transmission

.. code-block::

    User Touch → LVGL Event → GUI Callback → Controller State Update → 
    Message Generator → CAN Message → TWAI Driver → CAN Bus

Vehicle Protocol Architecture
---------------------------

The system uses a strategy pattern for handling different vehicle protocols:

Common Interface
~~~~~~~~~~~~~~

All vehicle protocols implement a common interface through function pointers:

* ``SpeedMessageGenerator``: Function to generate speed-related CAN messages
* ``GearMessageGenerator``: Function to generate gear-related CAN messages

Vehicle Configuration
~~~~~~~~~~~~~~~~~~~

Each vehicle type has a configuration structure containing:

* **Message IDs**: CAN identifiers for speed and gear messages
* **Baud Rate**: CAN bus communication speed
* **Generator Functions**: Protocol-specific message generation logic

.. code-block:: cpp

    struct VehicleCanConfig {
        uint32_t speed_msg_id;     // CAN ID for speed messages
        uint32_t gear_msg_id;      // CAN ID for gear messages  
        uint32_t baud_rate;        // CAN bus speed
        SpeedMessageGenerator speed_generator;  // Speed message function
        GearMessageGenerator gear_generator;    // Gear message function
    };

Message Generation Strategy
~~~~~~~~~~~~~~~~~~~~~~~~~

The system supports two approaches for message generation:

1. **Shared Functions**: Common protocols (like VW family) use shared generation functions
2. **Vehicle-Specific**: Unique protocols implement dedicated generation logic

Threading Model
--------------

The application uses FreeRTOS tasks for concurrent operation:

Main Application Task
~~~~~~~~~~~~~~~~~~~

* **Purpose**: UI management and main application logic
* **Priority**: Normal priority for responsive user interaction
* **Responsibilities**: GUI updates, user input processing

TWAI Transmission Task
~~~~~~~~~~~~~~~~~~~~

* **Purpose**: CAN message transmission
* **Priority**: High priority for real-time communication
* **Responsibilities**: Send CAN messages, manage transmission queue

TWAI Reception Task
~~~~~~~~~~~~~~~~~

* **Purpose**: CAN message reception and processing
* **Priority**: High priority for real-time communication  
* **Responsibilities**: Receive CAN messages, process incoming data

Memory Management
----------------

The system uses several memory management strategies:

Static Allocation
~~~~~~~~~~~~~~~

* **GUI Components**: LVGL objects use static allocation where possible
* **Configuration Data**: Vehicle configurations stored in static structures
* **Message Buffers**: Fixed-size buffers for CAN message data

Dynamic Allocation
~~~~~~~~~~~~~~~~

* **String Handling**: Dynamic strings for GUI labels and options
* **Task Stacks**: FreeRTOS task stacks allocated dynamically
* **Container Objects**: STL containers for flexible data structures

Configuration System
-------------------

The project uses ESP-IDF's Kconfig system for build-time configuration:

Display Configuration
~~~~~~~~~~~~~~~~~~~

* LCD resolution and buffer settings
* Touch controller options
* LVGL task priorities and timing

Communication Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~

* CAN bus parameters
* Message timing and priorities
* Debug output levels

Error Handling
-------------

The system implements comprehensive error handling:

CAN Communication Errors
~~~~~~~~~~~~~~~~~~~~~~~

* **Bus-off Detection**: Automatic recovery from bus-off conditions
* **Message Transmission Failures**: Retry logic for failed transmissions
* **Invalid State Handling**: Graceful handling of invalid vehicle states

GUI Error Handling
~~~~~~~~~~~~~~~~~

* **Invalid Input Validation**: Range checking for speed and gear inputs
* **Object Creation Failures**: Fallback behavior for LVGL object creation
* **Memory Allocation Failures**: Graceful degradation when memory is limited

Hardware Error Handling
~~~~~~~~~~~~~~~~~~~~~~

* **Display Initialization Failures**: Error reporting and retry logic
* **Touch Controller Issues**: Fallback to non-touch operation modes
* **Power Management**: Handling of low-power and reset conditions

Extensibility
------------

The architecture is designed for easy extension:

Adding New Vehicles
~~~~~~~~~~~~~~~~~

1. Define new vehicle enum in ``common.h``
2. Add button mapping in controller constructor
3. Implement message generation functions
4. Add vehicle configuration to message generator

Adding New Message Types
~~~~~~~~~~~~~~~~~~~~~~

1. Define new message generator function type
2. Add configuration fields to ``VehicleCanConfig``
3. Implement generation logic for each vehicle
4. Update controller to use new message types

Adding New GUI Features
~~~~~~~~~~~~~~~~~~~~~

1. Create new LVGL components in GUI class
2. Implement event handlers for user interaction
3. Add corresponding controller methods
4. Update message generation as needed