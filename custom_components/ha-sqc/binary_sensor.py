"""Sensor platform for SQC integration."""
from __future__ import annotations

import logging
from typing import Any
import re

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
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
        SQCPHControlBinarySensor(coordinator, config_entry),
    ]
    
    async_add_entities(entities)

class SQCBinarySensorBase(CoordinatorEntity[SQCDataUpdateCoordinator], BinarySensorEntity):
    """Base class for SQC binary sensors."""

    def __init__(
        self,
        coordinator: SQCDataUpdateCoordinator,
        config_entry: ConfigEntry,
        sensor_key: str,
        sensor_name: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._sensor_key = sensor_key
        self._attr_name = sensor_name
        self._attr_unique_id = f"{config_entry.entry_id}_{sensor_key}" 
        self._attr_device_info = self.coordinator._get_device_info(config_entry.entry_id)
    @property
    def available(self) -> bool:
        """Return True if the sensor is available."""
        return self.coordinator.last_update_success and self.coordinator.data.get("online", False)

class SQCPHControlBinarySensor(SQCBinarySensorBase):
    """ PH Control state for SQC."""

    def __init__(
        self,
        coordinator: SQCDataUpdateCoordinator,
        config_entry: ConfigEntry,
    ) -> None:
        """Initialize the PH control state."""
        super().__init__(coordinator, config_entry, "ph_control", "PH Control")

    @property
    def is_on(self):
        """Return the state of the sensor."""
        if not self.coordinator.data:
            return None
        
        html = self.coordinator.data.get("html")
        if not html:
            _LOGGER.warning("No sensor data available")
            return None
        if "Sterowanie pH:  <b>ON</b>" in html:
            return True
        if "Sterowanie pH:  <b>OFF</b>" in html:
            return False
        return None
    
class SQCAlarmBinarySensor(SQCBinarySensorBase):
    """ Alarm state for SQC."""

    def __init__(
        self,
        coordinator: SQCDataUpdateCoordinator,
        config_entry: ConfigEntry,
    ) -> None:
        """Initialize the Alarm state."""
        super().__init__(coordinator, config_entry, "alarm", "Alarm")

    @property
    def is_on(self):
        """Return the state of the sensor."""
        if not self.coordinator.data:
            return None
        
        html = self.coordinator.data.get("html")
        if not html:
            _LOGGER.warning("No sensor data available")
            return None
        if "Sterowanie pH:  <b>ON</b>" in html:
            return True
        if "Sterowanie pH:  <b>OFF</b>" in html:
            return False
        return None