# Config flow for Renogy Rover integration.
from __future__ import annotations

from collections.abc import Mapping
import logging
import os
from typing import Any

from serial import SerialException
import minimalmodbus
import serial.tools.list_ports
import voluptuous as vol

from homeassistant import config_entries
<<<<<<< HEAD
from homeassistant.const import ATTR_HW_VERSION, ATTR_MODEL, ATTR_SW_VERSION, CONF_PORT, CONF_HOST, CONF_TYPE, DEVICE_TYPE_UART, DEVICE_TYPE_TCP
=======
from homeassistant.const import ATTR_HW_VERSION, ATTR_MODEL, ATTR_SW_VERSION, CONF_PORT, CONF_HOST, CONF_TYPE
>>>>>>> a12d2b6 (Added TCP Port configuration. Fixed incorrect imports and modbus references. Added custom dialog labels. Added French language translations.)
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError

<<<<<<< HEAD
from .const import ATTR_DEVICE_ADDRESS, ATTR_SERIAL_NUMBER, DEFAULT_INTEGRATION_TITLE, DOMAIN, MAX_DEVICE_ADDRESS, MIN_DEVICE_ADDRESS
=======
from .const import ATTR_DEVICE_ADDRESS, ATTR_SERIAL_NUMBER, DEFAULT_INTEGRATION_TITLE, DOMAIN, MAX_DEVICE_ADDRESS, MIN_DEVICE_ADDRESS, DEVICE_TYPE_UART, DEVICE_TYPE_TCP
>>>>>>> a12d2b6 (Added TCP Port configuration. Fixed incorrect imports and modbus references. Added custom dialog labels. Added French language translations.)
from .renogy_rover import RenogyRoverUART, RenogyRoverTCP

_LOGGER = logging.getLogger(__name__)

DEVICE_TYPE_SCHEMA = vol.Schema({
    vol.Required(CONF_TYPE, default=DEVICE_TYPE_UART): vol.In([DEVICE_TYPE_UART, DEVICE_TYPE_TCP]),
})

def connect_and_read_device_info(
    hass: HomeAssistant, data: Mapping[str, Any]
) -> dict[str, str]:
    """Validate the user input allows us to connect.

    Data has the keys from DATA_SCHEMA with values provided by the user.
    """
    device_type = data[CONF_TYPE]
    device_info = {}

    if device_type == DEVICE_TYPE_UART:
        com_port = data[CONF_PORT]
        _LOGGER.debug("Initializing UART com port=%s", com_port)
        min_device_address = data.get(ATTR_DEVICE_ADDRESS, MIN_DEVICE_ADDRESS)
        max_device_address = data.get(ATTR_DEVICE_ADDRESS, MAX_DEVICE_ADDRESS)
        for device_address in range(min_device_address, max_device_address + 1):
            try:
                client = RenogyRoverUART(com_port, device_address)
                _LOGGER.debug(f"Scanned address {device_address}: connection established")
                device_info[ATTR_DEVICE_ADDRESS] = device_address
                device_info[ATTR_SERIAL_NUMBER] = client.serial_number()
                device_info[ATTR_SW_VERSION], device_info[ATTR_HW_VERSION] = client.version()
                device_info[ATTR_MODEL] = client.model()
                _LOGGER.debug("Returning device info=%s", device_info)
                break
            except SerialException as error:
                _LOGGER.exception("Cannot open serial port %s", com_port)
                if error.errno == 19:  # No such device.
                    raise InvalidPort from error
                else:
                    raise CannotOpenPort from error
            except minimalmodbus.NoResponseError as error:
                _LOGGER.debug(f"Scanned address {device_address}: no answer")
                if device_address == max_device_address:
                    raise NoDeviceFound from error
                else:
                    continue
            except Exception as err:  # pylint: disable=broad-except
                _LOGGER.exception("Could not connect to device=%s", com_port)
                raise err

    elif device_type == DEVICE_TYPE_TCP:
        host = data[CONF_HOST]
<<<<<<< HEAD
        _LOGGER.debug("Initializing TCP host=%s", host)
        try:
            client = RenogyRoverTCP(host)
=======
        port = data[CONF_PORT]
        _LOGGER.debug("Initializing TCP host=%s, port=%s", host, port)
        try:
            client = RenogyRoverTCP(host, port)
>>>>>>> a12d2b6 (Added TCP Port configuration. Fixed incorrect imports and modbus references. Added custom dialog labels. Added French language translations.)
            device_info[ATTR_SERIAL_NUMBER] = client.serial_number()
            device_info[ATTR_SW_VERSION], device_info[ATTR_HW_VERSION] = client.version()
            device_info[ATTR_MODEL] = client.model()
            _LOGGER.debug("Returning device info=%s", device_info)
        except Exception as err:  # pylint: disable=broad-except
<<<<<<< HEAD
            _LOGGER.exception("Could not connect to device=%s", host)
=======
            _LOGGER.exception("Could not connect to device=%s, port=%s", host, port)
>>>>>>> a12d2b6 (Added TCP Port configuration. Fixed incorrect imports and modbus references. Added custom dialog labels. Added French language translations.)
            raise CannotConnect from err

    return device_info


def scan_comports() -> tuple[list[str] | None, str | None]:
    """Find and store available COM ports for the GUI dropdown."""
    com_ports = serial.tools.list_ports.comports(include_links=True)
    com_ports_list = []

    # On Home Assistant OS there is a directory with symlinks derived from device ids,
    # which should be used to have deterministic device selection after reboot (USB number can change!)
    serial_id_links_dir = "/dev/serial/by-id"
    if os.path.exists(serial_id_links_dir):
        for device_link_name in os.listdir(serial_id_links_dir):
            com_ports_list.append(os.path.join(serial_id_links_dir, device_link_name))
            _LOGGER.debug("Found COM port: %s", device_link_name)
    else:
        for port in com_ports:
            com_ports_list.append(port.device)
            _LOGGER.debug("Found COM port: %s", port.device)

    if len(com_ports_list) > 0:
        return com_ports_list, com_ports_list[0]

    _LOGGER.warning("No COM ports found")
    return None, None


class RenogyRoverConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Renogy Rover."""

    VERSION = 1

    def __init__(self):
        """Initialise the config flow."""
        self.init_info = None
        self._com_ports_list = None
        self._default_com_port = None

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle a flow initialised by the user."""
        return await self.async_step_device_type(user_input)

    async def async_step_device_type(self, user_input: dict[str, Any] | None = None):
        """Handle the step to select device type."""
        errors = {}
        if user_input is not None:
            self.init_info = user_input
            if user_input[CONF_TYPE] == DEVICE_TYPE_UART:
                return await self.async_step_uart()
            elif user_input[CONF_TYPE] == DEVICE_TYPE_TCP:
                return await self.async_step_tcp()

        return self.async_show_form(
            step_id="device_type", data_schema=DEVICE_TYPE_SCHEMA, errors=errors
        )

    async def async_step_uart(self, user_input: dict[str, Any] | None = None):
        """Handle the step to configure UART connection."""
        errors = {}
        if self._com_ports_list is None:
            result = await self.hass.async_add_executor_job(scan_comports)
            self._com_ports_list, self._default_com_port = result
            if self._default_com_port is None:
                return self.async_abort(reason="no_serial_ports")

        if user_input is not None:
            user_input.update(self.init_info)
            try:
                self.init_info = await self.hass.async_add_executor_job(
                    connect_and_read_device_info, self.hass, user_input
                )
            except InvalidPort:
                errors["base"] = "invalid_serial_port"
            except CannotOpenPort:
                errors["base"] = "cannot_open_serial_port"
                _LOGGER.exception("Cannot open serial port %s", user_input[CONF_PORT])
            except NoDeviceFound:
                errors["base"] = "no_device_found"
                _LOGGER.exception("The serial port is working, but no device was found on the bus. Probably a cable issue.")
            except Exception:  # pylint: disable=broad-except
                errors["base"] = "cannot_connect"
                _LOGGER.error(
                    "Unable to communicate with Rover at %s", user_input[CONF_PORT]
                )
            else:
                await self.async_set_unique_id(f"{self.init_info[ATTR_SERIAL_NUMBER]}")
                self._abort_if_unique_id_configured(updates={CONF_PORT: user_input[CONF_PORT]})
                self.init_info.update(user_input)
                return self.async_create_entry(
                    title=DEFAULT_INTEGRATION_TITLE, data=self.init_info
                )

        data_schema = {
            vol.Required(CONF_PORT, default=self._default_com_port): vol.In(
                self._com_ports_list
            ),
        }

        return self.async_show_form(
            step_id="uart", data_schema=vol.Schema(data_schema), errors=errors
        )

    async def async_step_tcp(self, user_input: dict[str, Any] | None = None):
        """Handle the step to configure TCP connection."""
        errors = {}
        if user_input is not None:
            user_input.update(self.init_info)
            try:
                self.init_info = await self.hass.async_add_executor_job(
                    connect_and_read_device_info, self.hass, user_input
                )
            except CannotConnect:
                errors["base"] = "cannot_connect"
<<<<<<< HEAD
                _LOGGER.exception("Cannot connect to TCP device at %s", user_input[CONF_HOST])
            except Exception:  # pylint: disable=broad-except
                errors["base"] = "cannot_connect"
                _LOGGER.error(
                    "Unable to communicate with Rover at %s", user_input[CONF_HOST]
                )
            else:
                await self.async_set_unique_id(f"{self.init_info[ATTR_SERIAL_NUMBER]}")
                self._abort_if_unique_id_configured(updates={CONF_HOST: user_input[CONF_HOST]})
=======
                _LOGGER.exception("Cannot connect to TCP device at %s, port %s", user_input[CONF_HOST], user_input[CONF_PORT])
            except Exception:  # pylint: disable=broad-except
                errors["base"] = "cannot_connect"
                _LOGGER.error(
                    "Unable to communicate with Rover at %s, port %s", user_input[CONF_HOST], user_input[CONF_PORT]
                )
            else:
                await self.async_set_unique_id(f"{self.init_info[ATTR_SERIAL_NUMBER]}")
                self._abort_if_unique_id_configured(updates={CONF_HOST: user_input[CONF_HOST],CONF_PORT: user_input[CONF_PORT]})
>>>>>>> a12d2b6 (Added TCP Port configuration. Fixed incorrect imports and modbus references. Added custom dialog labels. Added French language translations.)
                self.init_info.update(user_input)
                return self.async_create_entry(
                    title=DEFAULT_INTEGRATION_TITLE, data=self.init_info
                )

        data_schema = {
            vol.Required(CONF_HOST): str,
<<<<<<< HEAD
=======
            vol.Required(CONF_PORT, default=502): vol.All(int, vol.Range(min=1, max=65535))
>>>>>>> a12d2b6 (Added TCP Port configuration. Fixed incorrect imports and modbus references. Added custom dialog labels. Added French language translations.)
        }

        return self.async_show_form(
            step_id="tcp", data_schema=vol.Schema(data_schema), errors=errors
        )


class CannotOpenPort(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidPort(HomeAssistantError):
    """Error to indicate the serial port is invalid."""


class NoDeviceFound(HomeAssistantError):
<<<<<<< HEAD
    """Error to indicate that no device was found on the bus."""
=======
    """Error to indicate that no device was found on the bus."""
>>>>>>> a12d2b6 (Added TCP Port configuration. Fixed incorrect imports and modbus references. Added custom dialog labels. Added French language translations.)
