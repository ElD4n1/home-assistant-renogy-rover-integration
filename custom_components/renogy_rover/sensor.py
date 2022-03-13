from collections.abc import Mapping
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import (
    ELECTRIC_CURRENT_AMPERE,
    ELECTRIC_POTENTIAL_VOLT,
    PERCENTAGE,
    POWER_WATT,
    TEMP_CELSIUS,
)

from const import DOMAIN
from device import RenogyRoverEntity
from renogy_rover import RenogyRover


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Renogy Rover sensor based on a config entry."""
    entities: list[SensorEntity] = []

    client: RenogyRover = hass.data[DOMAIN][config_entry.entry_id]
    config_entry_data = config_entry.data

    entities.append(SolarVoltageSensor(client, config_entry_data))

    async_add_entities(entities, True)

class SolarVoltageSensor(RenogyRoverEntity, SensorEntity):

    def __init__(self, client: RenogyRover, config_entry_data: Mapping[str, Any]):
        super().__init__(config_entry_data)
        self.client = client
        self.entity_description = SensorEntityDescription(
            device_class=SensorDeviceClass.VOLTAGE,
            native_unit_of_measurement=ELECTRIC_POTENTIAL_VOLT,
            state_class=SensorStateClass.MEASUREMENT,
            name="Solar Voltage",
        )

    def update(self) -> None:
        """Fetch new state data for the sensor.

        This is the only method that should fetch new data for Home Assistant.
        """
        self._state = self.client.solar_voltage()