ESP32 CAN Bus Vehicle Controller Documentation
============================================

Welcome to the ESP32 CAN Bus Vehicle Controller documentation. This project implements a sophisticated touchscreen-based CAN bus controller for multiple vehicle types, built on the ESP32-S3 platform with LVGL GUI framework.

Project Overview
---------------

The ESP32 CAN Bus Vehicle Controller is an embedded application that provides a touchscreen interface for controlling and monitoring CAN bus messages in various vehicle systems. The controller supports multiple vehicle types including Volkswagen T-series vans, Mercedes Sprinter vans, and Jeep vehicles.

Key Features
-----------

* **Multi-Vehicle Support**: Compatible with VW T5/T6/T6.1/T7, Mercedes Sprinter (various years), Jeep Renegade, and Mercedes Viano
* **Touchscreen GUI**: Modern LVGL-based user interface with vehicle selection, speed control, and gear selection
* **CAN Bus Communication**: Full CAN bus integration with vehicle-specific message protocols
* **Real-time Control**: Live speed adjustment (0-250 km/h) and gear selection (P/R/N/D)
* **Hardware Integration**: Support for Waveshare ESP32-S3 RGB LCD displays with touch capability
* **Configurable Parameters**: Extensive configuration options through ESP-IDF menuconfig

Hardware Requirements
--------------------

* ESP32-S3 microcontroller
* Waveshare RGB LCD display with touch controller (GT911 optional)
* CAN bus transceiver
* Power supply and connection hardware

Software Architecture
--------------------

The application follows a modular architecture with clear separation of concerns:

* **Controller Layer**: `CarCanController` manages CAN bus communication and vehicle state
* **GUI Layer**: `CarCanGui` provides the user interface using LVGL
* **Message Generation**: Vehicle-specific CAN message generators for different protocols
* **Hardware Abstraction**: Platform-specific drivers for display and touch interfaces

Table of Contents
================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   getting_started
   hardware_setup
   software_architecture
   api_reference
   vehicle_support
   configuration
   build_deployment
   troubleshooting

Getting Started
==============

This documentation will guide you through setting up, configuring, and deploying the ESP32 CAN Bus Vehicle Controller.

1. **Hardware Setup**: Prepare your ESP32-S3 board and connect the necessary peripherals
2. **Software Installation**: Install ESP-IDF and required dependencies  
3. **Configuration**: Configure the project for your specific hardware and vehicle
4. **Build and Flash**: Compile and deploy the firmware to your device
5. **Testing**: Verify functionality with your target vehicle

Supported Vehicles
=================

The controller currently supports the following vehicle types:

* **Volkswagen**: T5, T6, T6.1, T7
* **Mercedes-Benz**: Sprinter (multiple years), Viano
* **Jeep**: Renegade, Renegade MHEV

Each vehicle type has specific CAN message protocols and identifiers that are handled by dedicated message generators.

Contributing
===========

This project welcomes contributions. Please ensure all code follows the established patterns and includes appropriate documentation.

License
=======

[License information would go here]

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`