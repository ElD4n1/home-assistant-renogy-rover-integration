"""Config flow for Renogy Rover integration."""
from __future__ import annotations

from collections.abc import Mapping
import logging
from typing import Any

from serial import SerialException
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import ATTR_HW_VERSION, ATTR_MODEL, ATTR_SW_VERSION, CONF_PORT
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError

from .const import ATTR_SERIAL_NUMBER, DEFAULT_INTEGRATION_TITLE, DOMAIN
from .renogy_rover import RenogyRover

_LOGGER = logging.getLogger(__name__)


def connect_and_read_device_info(
    hass: HomeAssistant, data: Mapping[str, Any]
) -> dict[str, str]:
    """Validate the user input allows us to connect.

    Data has the keys from DATA_SCHEMA with values provided by the user.
    """
    com_port = data[CONF_PORT]
    _LOGGER.debug("Intitialising com port=%s", com_port)
    device_info = {}
    try:
        client = RenogyRover(com_port, 1)
        device_info[ATTR_SERIAL_NUMBER] = client.serial_number()
        device_info[ATTR_SW_VERSION], device_info[ATTR_HW_VERSION] = client.version()
        device_info[ATTR_MODEL] = client.model()
        _LOGGER.debug("Returning device info=%s", device_info)
    except SerialException as error:
        _LOGGER.exception("Cannot open serial port %s", com_port[CONF_PORT])
        if error.errno == 19:  # No such device.
            raise InvalidPort from error
        else:
            raise CannotOpenPort from error
    except Exception as err:  # pylint: disable=broad-except
        _LOGGER.exception("Could not connect to device=%s", com_port)
        raise err

    return device_info


def scan_comports() -> tuple[list[str] | None, str | None]:
    """Find and store available COM ports for the GUI dropdown."""
    com_ports = serial.tools.list_ports.comports(include_links=True)
    com_ports_list = []
    for port in com_ports:
        com_ports_list.append(port.device)
        _LOGGER.debug("COM port option: %s", port.device)
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
        return await self.async_step_init()

    async def async_step_init(self, user_input: dict[str, Any] | None = None):
        """Handle the first step, which is selecting the serial port."""
        errors = {}
        if self._com_ports_list is None:
            result = await self.hass.async_add_executor_job(scan_comports)
            self._com_ports_list, self._default_com_port = result
            if self._default_com_port is None:
                return self.async_abort(reason="no_serial_ports")

        # Handle the initial step.
        if user_input is not None:
            # Check if the port is already configured
            for existing_entry in self.hass.config_entries.async_entries(DOMAIN):
                if existing_entry.data[CONF_PORT] == user_input[CONF_PORT]:
                    return self.async_abort(reason="port_already_configured")

            # Try to connect and read device info
            try:
                self.init_info = await self.hass.async_add_executor_job(
                    connect_and_read_device_info, self.hass, user_input
                )
            except InvalidPort:
                errors["base"] = "invalid_serial_port"
            except CannotOpenPort:
                errors["base"] = "cannot_open_serial_port"
                _LOGGER.exception("Cannot open serial port %s", user_input[CONF_PORT])
            except Exception:  # pylint: disable=broad-except
                errors["base"] = "cannot_connect"
                _LOGGER.error(
                    "Unable to communicate with Rover at %s", user_input[CONF_PORT]
                )
            else:
                self.init_info.update(user_input)
                return self.async_create_entry(
                    title=DEFAULT_INTEGRATION_TITLE, data=self.init_info
                )

        # If no user input, must be first pass through the config.
        data_schema = {
            vol.Required(CONF_PORT, default=self._default_com_port): vol.In(
                self._com_ports_list
            ),
        }

        # Show initial form.
        return self.async_show_form(
            step_id="init", data_schema=vol.Schema(data_schema), errors=errors
        )


class CannotOpenPort(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidPort(HomeAssistantError):
    """Error to indicate the serial port is invalid."""
