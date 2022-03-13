from collections.abc import Mapping
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity import EntityCategory
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
    ENERGY_KILO_WATT_HOUR,
    POWER_WATT,
    TEMP_CELSIUS,
)

from .const import DOMAIN
from .device import RenogyRoverEntity
from .renogy_rover import RenogyRover


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
    entities.append(SolarCurrentSensor(client, config_entry_data))
    entities.append(SolarPowerSensor(client, config_entry_data))
    entities.append(BatteryVoltageSensor(client, config_entry_data))
    entities.append(EnergyProductionTodaySensor(client, config_entry_data))
    entities.append(ControllerTemperatureSensor(client, config_entry_data))
    entities.append(ChargingStatusSensor(client, config_entry_data))

    async_add_entities(entities, True)

class SolarVoltageSensor(RenogyRoverEntity, SensorEntity):

    def __init__(self, client: RenogyRover, config_entry_data: Mapping[str, Any]):
        super().__init__(config_entry_data)
        self.client = client
        self.entity_description = SensorEntityDescription(
            key="solar_voltage",
            device_class=SensorDeviceClass.VOLTAGE,
            native_unit_of_measurement=ELECTRIC_POTENTIAL_VOLT,
            state_class=SensorStateClass.MEASUREMENT,
            name="Solar Voltage",
        )

    def update(self) -> None:
        """
        Fetch new state data for the sensor.
        """
        self._attr_native_value = self.client.solar_voltage()

class SolarCurrentSensor(RenogyRoverEntity, SensorEntity):

    def __init__(self, client: RenogyRover, config_entry_data: Mapping[str, Any]):
        super().__init__(config_entry_data)
        self.client = client
        self.entity_description = SensorEntityDescription(
            key="solar_current",
            device_class=SensorDeviceClass.CURRENT,
            native_unit_of_measurement=ELECTRIC_CURRENT_AMPERE,
            state_class=SensorStateClass.MEASUREMENT,
            name="Solar Current",
        )

    def update(self) -> None:
        """
        Fetch new state data for the sensor.
        """
        self._attr_native_value = self.client.solar_current()

class SolarPowerSensor(RenogyRoverEntity, SensorEntity):

    def __init__(self, client: RenogyRover, config_entry_data: Mapping[str, Any]):
        super().__init__(config_entry_data)
        self.client = client
        self.entity_description = SensorEntityDescription(
            key="solar_power",
            device_class=SensorDeviceClass.POWER,
            native_unit_of_measurement=POWER_WATT,
            state_class=SensorStateClass.MEASUREMENT,
            name="Solar Power",
        )

    def update(self) -> None:
        """
        Fetch new state data for the sensor.
        """
        self._attr_native_value = self.client.solar_power()

class BatteryVoltageSensor(RenogyRoverEntity, SensorEntity):

    def __init__(self, client: RenogyRover, config_entry_data: Mapping[str, Any]):
        super().__init__(config_entry_data)
        self.client = client
        self.entity_description = SensorEntityDescription(
            key="battery_voltage",
            device_class=SensorDeviceClass.VOLTAGE,
            native_unit_of_measurement=ELECTRIC_POTENTIAL_VOLT,
            state_class=SensorStateClass.MEASUREMENT,
            name="Battery Voltage",
        )

    def update(self) -> None:
        """
        Fetch new state data for the sensor.
        """
        self._attr_native_value = self.client.battery_voltage()

class EnergyProductionTodaySensor(RenogyRoverEntity, SensorEntity):

    def __init__(self, client: RenogyRover, config_entry_data: Mapping[str, Any]):
        super().__init__(config_entry_data)
        self.client = client
        self.entity_description = SensorEntityDescription(
            key="energy_production_today",
            device_class=SensorDeviceClass.ENERGY,
            native_unit_of_measurement=ENERGY_KILO_WATT_HOUR,
            state_class=SensorStateClass.TOTAL_INCREASING,
            name="Energy Production Today",
        )

    def update(self) -> None:
        """
        Fetch new state data for the sensor.
        """
        self._attr_native_value = self.client.power_generation_today()

class ControllerTemperatureSensor(RenogyRoverEntity, SensorEntity):

    def __init__(self, client: RenogyRover, config_entry_data: Mapping[str, Any]):
        super().__init__(config_entry_data)
        self.client = client
        self.entity_description = SensorEntityDescription(
            key="controller_temperature",
            device_class=SensorDeviceClass.TEMPERATURE,
            native_unit_of_measurement=TEMP_CELSIUS,
            state_class=SensorStateClass.MEASUREMENT,
            name="Controller Temperature",
            entity_category=EntityCategory.DIAGNOSTIC
        )

    def update(self) -> None:
        """
        Fetch new state data for the sensor.
        """
        self._attr_native_value = self.client.controller_temperature()

class ChargingStatusSensor(RenogyRoverEntity, SensorEntity):

    def __init__(self, client: RenogyRover, config_entry_data: Mapping[str, Any]):
        super().__init__(config_entry_data)
        self.client = client
        self.entity_description = SensorEntityDescription(
            key="charging_status",
            state_class=SensorStateClass.MEASUREMENT,
            name="Charging Status",
            entity_category=EntityCategory.DIAGNOSTIC
        )

    def update(self) -> None:
        """
        Fetch new state data for the sensor.
        """
        self._attr_native_value = self.client.charging_status_label()