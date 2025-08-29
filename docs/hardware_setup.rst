Hardware Setup
==============

This document provides detailed information about the hardware requirements, components, and setup procedures for the ESP32 CAN Bus Vehicle Controller.

Hardware Requirements
--------------------

Core Components
~~~~~~~~~~~~~~

ESP32-S3 Development Board
^^^^^^^^^^^^^^^^^^^^^^^^^

* **Processor**: ESP32-S3 dual-core Xtensa LX7 @ 240MHz
* **Memory**: 512KB SRAM, 384KB ROM
* **Flash**: Minimum 4MB (8MB or 16MB recommended)
* **WiFi/Bluetooth**: Built-in WiFi 802.11 b/g/n and Bluetooth 5.0
* **GPIO**: Sufficient pins for display, touch, and CAN interfaces

**Recommended Boards:**
* ESP32-S3-DevKitC-1
* ESP32-S3-DevKitM-1  
* Freenove ESP32-S3-WROOM

Waveshare RGB LCD Display
^^^^^^^^^^^^^^^^^^^^^^^^

* **Resolution**: 800x480 pixels
* **Size**: 7-inch diagonal
* **Interface**: RGB parallel interface
* **Touch Controller**: GT911 (optional, configurable)
* **Power**: 5V/3.3V compatible
* **Connector**: Standard RGB connector with touch interface

**Supported Models:**
* Waveshare 7inch DSI LCD (C) 800×480
* Waveshare 5inch DSI LCD 800×480
* Compatible RGB LCD panels with similar specifications

CAN Bus Transceiver
^^^^^^^^^^^^^^^^^^

* **Protocol**: ISO 11898 compliant
* **Speed**: Up to 1 Mbps (500 kbps typical for automotive)
* **Voltage**: 5V or 3.3V compatible
* **Protection**: ESD and short-circuit protection

**Recommended Components:**
* SN65HVD230 CAN transceiver board
* MCP2515 CAN controller with SPI interface (alternative)
* TJA1050 CAN transceiver

Power Supply
^^^^^^^^^^^

* **Input Voltage**: 12V DC (automotive standard)
* **Output**: 5V/3A for display, 3.3V/1A for ESP32
* **Regulation**: Low noise, stable regulation required
* **Protection**: Reverse polarity, overcurrent protection

**Recommended Solutions:**
* Automotive-grade DC-DC converters
* LM2596-based step-down modules
* Integrated power management boards

Additional Components
~~~~~~~~~~~~~~~~~~~

Connectors and Cables
^^^^^^^^^^^^^^^^^^^^

* **CAN Bus Connector**: DB9 or OBD-II connector for vehicle interface
* **Power Connector**: Automotive-grade power connector
* **Display Cable**: FFC/FPC cable for RGB interface
* **Touch Cable**: I2C cable for touch controller (if used)

Enclosure
^^^^^^^^

* **Material**: ABS plastic or aluminum
* **Size**: Accommodate 7-inch display and electronics
* **Mounting**: VESA or custom mounting options
* **Protection**: IP54 rating recommended for automotive use

Wiring and Connections
--------------------

ESP32-S3 Pin Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~

Display Interface (RGB)
^^^^^^^^^^^^^^^^^^^^^^

The RGB display interface requires multiple GPIO pins for data and control signals:

.. code-block::

    RGB Data Pins:
    - R0-R4: GPIO pins for red color data (5 bits)
    - G0-G5: GPIO pins for green color data (6 bits)  
    - B0-B4: GPIO pins for blue color data (5 bits)
    
    Control Pins:
    - HSYNC: Horizontal sync signal
    - VSYNC: Vertical sync signal
    - PCLK: Pixel clock signal
    - DE: Data enable signal
    - DISP: Display enable (optional)
    - BCKL: Backlight control (PWM)

**Example Pin Assignment:**

.. code-block::

    // RGB Data Lines
    #define LCD_R0_GPIO    1
    #define LCD_R1_GPIO    2
    #define LCD_R2_GPIO    42
    #define LCD_R3_GPIO    41
    #define LCD_R4_GPIO    40
    
    #define LCD_G0_GPIO    39
    #define LCD_G1_GPIO    38
    #define LCD_G2_GPIO    37
    #define LCD_G3_GPIO    36
    #define LCD_G4_GPIO    35
    #define LCD_G5_GPIO    34
    
    #define LCD_B0_GPIO    33
    #define LCD_B1_GPIO    26
    #define LCD_B2_GPIO    25
    #define LCD_B3_GPIO    24
    #define LCD_B4_GPIO    23
    
    // Control Lines
    #define LCD_HSYNC_GPIO 46
    #define LCD_VSYNC_GPIO 3
    #define LCD_PCLK_GPIO  21
    #define LCD_DE_GPIO    47
    #define LCD_DISP_GPIO  -1  // Not used
    #define LCD_BCKL_GPIO  45  // Backlight PWM

Touch Interface (I2C)
^^^^^^^^^^^^^^^^^^^

If using the GT911 touch controller:

.. code-block::

    // I2C Interface
    #define TOUCH_SDA_GPIO  19
    #define TOUCH_SCL_GPIO  20
    #define TOUCH_INT_GPIO  18  // Touch interrupt
    #define TOUCH_RST_GPIO  4   // Touch reset

CAN Bus Interface
^^^^^^^^^^^^^^^

For TWAI (CAN) communication:

.. code-block::

    // TWAI/CAN Interface
    #define CAN_TX_GPIO     5   // CAN transmit
    #define CAN_RX_GPIO     6   // CAN receive

Power and Control
^^^^^^^^^^^^^^^

.. code-block::

    // Power Management
    #define POWER_EN_GPIO   7   // Power enable (optional)
    #define STATUS_LED_GPIO 8   // Status LED

CAN Bus Wiring
~~~~~~~~~~~~~

Vehicle OBD-II Connection
^^^^^^^^^^^^^^^^^^^^^^^

Standard OBD-II pinout for CAN bus connection:

.. code-block::

    OBD-II Connector (looking into connector):
    
    1  2  3  4  5  6  7  8
     9 10 11 12 13 14 15 16
    
    Pin  6: CAN High (CAN_H)
    Pin 14: CAN Low (CAN_L)
    Pin 16: Battery Positive (+12V)
    Pin  4: Chassis Ground
    Pin  5: Signal Ground

**Connection Diagram:**

.. code-block::

    Vehicle OBD-II          CAN Transceiver         ESP32-S3
    ┌─────────────┐        ┌─────────────────┐     ┌──────────────┐
    │ Pin 6 (H)   │────────│ CANH            │     │              │
    │ Pin 14 (L)  │────────│ CANL            │     │              │
    │ Pin 16 (+12V)│───────│ VCC             │     │              │
    │ Pin 4/5 (GND)│───────│ GND             │     │              │
    └─────────────┘        │ TXD             │─────│ GPIO5 (TX)   │
                           │ RXD             │─────│ GPIO6 (RX)   │
                           └─────────────────┘     └──────────────┘

Power Distribution
~~~~~~~~~~~~~~~~

.. code-block::

    Vehicle 12V ──┬── Power Supply Module ──┬── 5V ── Display Power
                  │                         └── 3.3V ── ESP32-S3
                  └── CAN Transceiver ──────── 5V/3.3V

Display Connection
~~~~~~~~~~~~~~~~~

RGB Interface Wiring
^^^^^^^^^^^^^^^^^^^

The RGB display connects via a flat flexible cable (FFC) or individual wires:

.. code-block::

    Display Connector     ESP32-S3 GPIO
    ┌───────────────┐    ┌─────────────┐
    │ R0-R4         │────│ RGB_R pins  │
    │ G0-G5         │────│ RGB_G pins  │  
    │ B0-B4         │────│ RGB_B pins  │
    │ HSYNC         │────│ HSYNC pin   │
    │ VSYNC         │────│ VSYNC pin   │
    │ PCLK          │────│ PCLK pin    │
    │ DE            │────│ DE pin      │
    │ VCC           │────│ 5V Power    │
    │ GND           │────│ Ground      │
    └───────────────┘    └─────────────┘

Touch Interface Wiring (Optional)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If using touch functionality:

.. code-block::

    Touch Controller     ESP32-S3
    ┌───────────────┐   ┌──────────────┐
    │ SDA           │───│ GPIO19 (SDA) │
    │ SCL           │───│ GPIO20 (SCL) │
    │ INT           │───│ GPIO18 (INT) │
    │ RST           │───│ GPIO4 (RST)  │
    │ VCC           │───│ 3.3V         │
    │ GND           │───│ Ground       │
    └───────────────┘   └──────────────┘

Assembly Instructions
-------------------

Step 1: Power Supply Setup
~~~~~~~~~~~~~~~~~~~~~~~~~

1. **Install DC-DC Converter**: Mount the 12V to 5V/3.3V converter in the enclosure
2. **Connect Input Power**: Wire the 12V input from vehicle power or OBD-II pin 16
3. **Add Protection**: Install fuse and reverse polarity protection
4. **Test Voltages**: Verify 5V and 3.3V outputs before connecting components

Step 2: ESP32-S3 Preparation
~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. **Flash Test Firmware**: Upload a simple test program to verify board functionality
2. **GPIO Configuration**: Configure pins according to the pinout table
3. **Power Connection**: Connect 3.3V and ground to the development board
4. **Status LED**: Connect status LED to monitor system operation

Step 3: Display Installation
~~~~~~~~~~~~~~~~~~~~~~~~~~

1. **Mount Display**: Secure the LCD panel in the enclosure front panel
2. **Connect RGB Cable**: Attach the FFC cable between display and ESP32-S3
3. **Power Connection**: Connect 5V power to the display
4. **Backlight Control**: Connect PWM signal for backlight dimming
5. **Test Display**: Verify display initialization and basic graphics

Step 4: Touch Controller Setup (Optional)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. **I2C Connections**: Wire SDA, SCL, INT, and RST signals
2. **Power Supply**: Connect 3.3V and ground to touch controller
3. **Calibration**: Run touch calibration routine after assembly
4. **Test Touch**: Verify touch responsiveness and accuracy

Step 5: CAN Interface Installation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. **Mount Transceiver**: Install CAN transceiver board in enclosure
2. **ESP32 Connection**: Wire TX and RX signals to ESP32-S3
3. **CAN Bus Wiring**: Connect CANH and CANL to vehicle CAN bus
4. **Termination**: Add 120Ω termination resistor if required
5. **Test Communication**: Verify CAN message transmission and reception

Step 6: Final Assembly
~~~~~~~~~~~~~~~~~~~~

1. **Enclosure Assembly**: Mount all components in the enclosure
2. **Cable Management**: Secure and route all cables properly
3. **Connector Installation**: Mount external connectors (power, CAN, etc.)
4. **Sealing**: Apply appropriate sealing for environmental protection
5. **Labeling**: Add labels for connectors and controls

Testing and Verification
-----------------------

Hardware Test Checklist
~~~~~~~~~~~~~~~~~~~~~~

Power System Tests
^^^^^^^^^^^^^^^^

- [ ] 12V input voltage measurement
- [ ] 5V output voltage and current capacity
- [ ] 3.3V output voltage and ripple
- [ ] Power consumption measurement
- [ ] Thermal testing under load

Display Tests
^^^^^^^^^^^

- [ ] Display initialization
- [ ] Color pattern generation
- [ ] Backlight control functionality
- [ ] Touch calibration and response
- [ ] GUI component rendering

CAN Interface Tests
^^^^^^^^^^^^^^^^^

- [ ] CAN transceiver communication
- [ ] Message transmission verification
- [ ] Message reception testing
- [ ] Bus error handling
- [ ] Termination resistance verification

System Integration Tests
^^^^^^^^^^^^^^^^^^^^^^

- [ ] Complete power-on sequence
- [ ] GUI operation and responsiveness
- [ ] CAN message generation accuracy
- [ ] Vehicle protocol compatibility
- [ ] Long-term stability testing

Troubleshooting
--------------

Common Issues
~~~~~~~~~~~

Display Not Working
^^^^^^^^^^^^^^^^^

**Symptoms**: Black screen, no display output

**Possible Causes:**
- Incorrect power supply voltage
- Wrong GPIO pin assignments
- Faulty RGB cable connection
- Display timing configuration errors

**Solutions:**
- Verify 5V power supply to display
- Check RGB pin assignments in code
- Inspect FFC cable for damage
- Review display timing parameters

Touch Not Responding
^^^^^^^^^^^^^^^^^^

**Symptoms**: No touch input, incorrect touch coordinates

**Possible Causes:**
- I2C communication failure
- Touch controller not powered
- Incorrect touch calibration
- Hardware connection issues

**Solutions:**
- Test I2C communication with scope
- Verify 3.3V power to touch controller
- Run touch calibration routine
- Check SDA, SCL, INT, RST connections

CAN Communication Failure
^^^^^^^^^^^^^^^^^^^^^^^^

**Symptoms**: Cannot send/receive CAN messages

**Possible Causes:**
- CAN transceiver not powered
- Wrong CAN bus wiring
- Incorrect baud rate configuration
- Missing termination resistors

**Solutions:**
- Check transceiver power supply
- Verify CANH/CANL connections
- Configure correct CAN baud rate
- Add 120Ω termination if needed

Performance Issues
^^^^^^^^^^^^^^^^

**Symptoms**: Slow GUI response, display artifacts

**Possible Causes:**
- Insufficient power supply current
- GPIO drive strength too low
- Clock timing issues
- Memory allocation problems

**Solutions:**
- Increase power supply capacity
- Adjust GPIO drive strength settings
- Optimize display clock timing
- Review memory usage and allocation

Safety Considerations
-------------------

Electrical Safety
~~~~~~~~~~~~~~~

- Use automotive-grade components rated for 12V operation
- Install proper fusing and overcurrent protection
- Ensure proper grounding to vehicle chassis
- Use shielded cables for CAN bus connections
- Follow automotive electrical standards (ISO 26262)

Environmental Protection
~~~~~~~~~~~~~~~~~~~~~~

- Seal enclosure against moisture and dust (IP54 minimum)
- Use temperature-rated components (-40°C to +85°C)
- Provide adequate ventilation for heat dissipation
- Protect against vibration and mechanical shock
- Consider EMI/EMC requirements for automotive use

Vehicle Integration
~~~~~~~~~~~~~~~~~

- Verify CAN bus compatibility before connection
- Use appropriate connectors for vehicle interface
- Follow manufacturer guidelines for OBD-II access
- Consider impact on vehicle warranty
- Test thoroughly before permanent installation

Maintenance
----------

Regular Maintenance Tasks
~~~~~~~~~~~~~~~~~~~~~~~

- Clean display screen regularly
- Check cable connections for wear
- Verify CAN bus termination integrity
- Monitor power supply voltages
- Update firmware as needed

Replacement Procedures
~~~~~~~~~~~~~~~~~~~~

- Keep spare components for critical parts
- Document configuration settings
- Test replacements before installation
- Maintain calibration data backups
- Follow proper ESD handling procedures