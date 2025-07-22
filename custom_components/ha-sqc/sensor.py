"""Sensor platform for SQC integration."""
from __future__ import annotations

import logging
from typing import Any
import re

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    cached_property,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import SQCDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
    coordinator: SQCDataUpdateCoordinator = hass.data[DOMAIN][config_entry.entry_id]
    
    # Define your sensors here
    entities = [
        SQCWaterTempSensor(coordinator, config_entry),
        SQCWaterPHSensor(coordinator, config_entry),
        SQCWaterCO2Sensor(coordinator, config_entry),
    ]
    
    async_add_entities(entities)


class SQCSensorBase(CoordinatorEntity[SQCDataUpdateCoordinator], SensorEntity):
    """Base class for SQC sensors."""

    def __init__(
        self,
        coordinator: SQCDataUpdateCoordinator,
        config_entry: ConfigEntry,
        sensor_key: str,
        name: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._sensor_key = sensor_key
        self._attr_name = name
        self._attr_unique_id = f"{config_entry.entry_id}_{sensor_key}"
        self._attr_device_info = self.coordinator._get_device_info(config_entry.entry_id)
    @property
    def available(self) -> bool:
        """Return True if the sensor is available."""
        return self.coordinator.last_update_success and self.coordinator.data.get("online", False)

class SQCWaterTempSensor(SQCSensorBase):
    """Water temperature sensor for SQC."""

    def __init__(
        self,
        coordinator: SQCDataUpdateCoordinator,
        config_entry: ConfigEntry,
    ) -> None:
        """Initialize the temperature sensor."""
        super().__init__(coordinator, config_entry, "water_temp", "Water Temperature")
        self._attr_device_class = SensorDeviceClass.TEMPERATURE
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS

    @property
    def native_value(self):
        """Return the state of the sensor."""
        if not self.coordinator.data:
            return None
        
        html = self.coordinator.data.get("html")
        if not html:
            _LOGGER.warning("No sensor data available")
            return None

        pattern = r"Temperatura = ([\d.]+)ºC"
        match = re.search(pattern, html)
        if match:
            return float(match.group(1))
        return None
    
class SQCWaterPHSensor(SQCSensorBase):
    """Water pH sensor for SQC."""

    def __init__(
        self,
        coordinator: SQCDataUpdateCoordinator,
        config_entry: ConfigEntry,
    ) -> None:
        """Initialize the ph sensor."""
        super().__init__(coordinator, config_entry, "water_ph", "Water pH")
        self._attr_device_class = SensorDeviceClass.PH
        self._attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def native_value(self):
        """Return the state of the sensor."""
        if not self.coordinator.data:
            return None
        
        html = self.coordinator.data.get("html")
        if not html:
            _LOGGER.warning("No sensor data available")
            return None

        pattern = r"pH = ([\d.]+) \[pH\]"
        match = re.search(pattern, html)
        if match:
            return float(match.group(1))
        return None
    
class SQCWaterCO2Sensor(SQCSensorBase):
    """Water CO2 sensor for SQC."""

    def __init__(
        self,
        coordinator: SQCDataUpdateCoordinator,
        config_entry: ConfigEntry,
    ) -> None:
        """Initialize the CO2 sensor."""
        super().__init__(coordinator, config_entry, "water_co2", "Water CO2")
        self._attr_device_class = SensorDeviceClass.CO2
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_native_unit_of_measurement = "ppm"

    @property
    def native_value(self):
        """Return the state of the sensor."""
        if not self.coordinator.data:
            return None
        
        html = self.coordinator.data.get("html")
        if not html:
            _LOGGER.warning("No sensor data available")
            return None

        pattern = r"CO<sub>2</sub> = <b>([\d.]+) ppm</b>"
        match = re.search(pattern, html)
        if match:
            return float(match.group(1))
        return None