"""The Renogy Rover integration."""
from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_PORT, CONF_HOST, CONF_TYPE, Platform
from homeassistant.core import HomeAssistant

from .config_flow import connect_and_read_device_info
from .const import ATTR_DEVICE_ADDRESS, ATTR_SERIAL_NUMBER, DOMAIN, DEVICE_TYPE_UART, DEVICE_TYPE_TCP
from .renogy_rover import RenogyRoverUART, RenogyRoverTCP

PLATFORMS: list[Platform] = [Platform.SENSOR]

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Renogy Rover from a config entry."""
    device_info = await hass.async_add_executor_job(
        connect_and_read_device_info, hass, entry.data
    )

    # Validation check
    if not device_matches_entry(device_info, entry):
        _LOGGER.error(
            'Device serial number "%s" does not match serial number "%s" in config entry!' % (device_info[ATTR_SERIAL_NUMBER], entry.data[ATTR_SERIAL_NUMBER])
        )
        return False

    if entry.data[CONF_TYPE] == DEVICE_TYPE_UART:
        hass.data.setdefault(DOMAIN, {})[entry.entry_id] = RenogyRoverUART(entry.data[CONF_PORT], entry.data[ATTR_DEVICE_ADDRESS])
    elif entry.data[CONF_TYPE] == DEVICE_TYPE_TCP:
        hass.data.setdefault(DOMAIN, {})[entry.entry_id] = RenogyRoverTCP(entry.data[CONF_HOST])

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


def device_matches_entry(
    device_info: dict[str, str], config_entry: ConfigEntry
) -> bool:
    """Check if device info matches config entry."""
    return device_info[ATTR_SERIAL_NUMBER] == config_entry.data[ATTR_SERIAL_NUMBER]