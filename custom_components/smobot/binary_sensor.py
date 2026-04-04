"""Binary sensor platform for Smobot."""

from __future__ import annotations

from homeassistant.components.binary_sensor import BinarySensorDeviceClass, BinarySensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DATA_COORDINATOR, DOMAIN
from .entity import SmobotEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Smobot binary sensors."""
    coordinator = hass.data[DOMAIN][entry.entry_id][DATA_COORDINATOR]
    async_add_entities([SmobotLidOpenBinarySensor(coordinator)])


class SmobotLidOpenBinarySensor(SmobotEntity, BinarySensorEntity):
    """Binary sensor that reports whether the grill lid is open."""

    _attr_translation_key = "lid_open"
    _attr_device_class = BinarySensorDeviceClass.OPENING
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, coordinator) -> None:
        """Initialize the binary sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{self.entity_id_prefix}_lid_open"
        self._attr_entity_registry_enabled_default = False

    @property
    def is_on(self) -> bool:
        """Return true if the lid is open."""
        return self.smobot_status.lid_open
