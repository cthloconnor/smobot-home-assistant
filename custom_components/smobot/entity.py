"""Shared entity classes for Smobot."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .client import SmobotStatus
from .const import DOMAIN
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
