"""Constants for the Renogy Rover integration."""
from enum import Enum

DOMAIN = "renogy_rover"

DEFAULT_INTEGRATION_TITLE = "Renogy Rover"
DEFAULT_DEVICE_NAME = "Rover"

MANUFACTURER = "Renogy"

MIN_DEVICE_ADDRESS = 1
MAX_DEVICE_ADDRESS = 247

ATTR_DEVICE_ADDRESS = "device_address"
ATTR_SERIAL_NUMBER = "serial_number"

class ChargingState(Enum):
    DEACTIVATED = 0
    ACTIVATED = 1
    MPPT = 2
    EQUALIZING = 3
    BOOST = 4
    FLOATING = 5
    CURRENT_LIMITING = 6