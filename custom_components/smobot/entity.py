"""Shared entity classes for Smobot."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTemperature
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .client import SmobotStatus
from .const import CONF_TEMPERATURE_UNIT, DEFAULT_TEMPERATURE_UNIT, DOMAIN
from .coordinator import SmobotDataUpdateCoordinator


class SmobotEntity(CoordinatorEntity[SmobotDataUpdateCoordinator]):
    """Base entity for Smobot devices."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: SmobotDataUpdateCoordinator) -> None:
        """Initialize the entity."""
        super().__init__(coordinator)
        entry: ConfigEntry = coordinator.entry
        device_id = entry.unique_id or entry.entry_id
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, device_id)},
            manufacturer="Smobot",
            model="Smobot",
            name=entry.title,
            configuration_url=f"http://{coordinator.client.host}",
        )

    @property
    def smobot_status(self) -> SmobotStatus:
        """Return the latest coordinator data."""
        return self.coordinator.data

    @property
    def entity_id_prefix(self) -> str:
        """Return a stable prefix for entity unique IDs."""
        entry: ConfigEntry = self.coordinator.entry
        return entry.unique_id or entry.entry_id

    @property
    def native_temperature_unit(self) -> str:
        """Return the configured Home Assistant temperature unit."""
        return (
            UnitOfTemperature.CELSIUS
            if self.coordinator.entry.options.get(
                CONF_TEMPERATURE_UNIT,
                DEFAULT_TEMPERATURE_UNIT,
            )
            == "C"
            else UnitOfTemperature.FAHRENHEIT
        )

    def api_to_native_temperature(self, value: int | float | None) -> float | None:
        """Convert Fahrenheit API values to the configured entity unit."""
        if value is None:
            return None
        if self.native_temperature_unit == UnitOfTemperature.CELSIUS:
            return round((float(value) - 32.0) * 5.0 / 9.0, 1)
        return float(value)

    def native_to_api_temperature(self, value: int | float) -> int:
        """Convert the configured entity unit back to Fahrenheit for the API."""
        if self.native_temperature_unit == UnitOfTemperature.CELSIUS:
            return int(round(float(value) * 9.0 / 5.0 + 32.0))
        return int(round(float(value)))
