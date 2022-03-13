# Home Assistant Renogy Rover Custom Integration
Integrates Renogy Rover Solar Charge Controllers connected via USB/UART into Home Assistant.

Installable via HACS as custom integration.

# Sensors
I only added the sensors that I need, there are more available from the underlying library.

Available Sensors:
- Solar Voltage
- Solar Current
- Solar Power
- Battery Voltage
- Energy Production Today
- Charging Status (deactivated, mppt, floating, ...)
- Controller Temperature

# Credits
Thanks to Brian S. Corbin for providing the Modbus driver which I took from here: https://github.com/corbinbs/solarshed/blob/e63d2031e50d41015dd67e48154f4dd2cba1c9cb/solarshed/controllers/renogy_rover.py
