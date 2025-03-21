# SCADA-PLC-Project

This is a SCADA software designed to control, display, and store data from a PLC (Programmable Logic Controller) for industrial plants.

## Software to Simulate a PLC

In the "software_to_simulate_plc" folder, you'll find a PLC simulator that uses MODBUS to communicate with the SCADA software. This simulator demonstrates how the system works and handles real PLC data.

## SCADA Software

We have divided the software into three main components:

### 1. Data Acquisition
This component acts as a MODBUS client, allowing communication to receive and send data to the PLC.

### 2. IHM (Human-Machine Interface)
The IHM is a graphical interface that is helpful for programming and visualizing the industrial plant processes.

### 3. Data Storage
Using SQLite, we've implemented a fast and simple solution for storing data from the PLC, such as temperature, pressure, velocity, and more.
