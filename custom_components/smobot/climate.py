"""Climate platform for Smobot."""

from __future__ import annotations

from homeassistant.components.climate import ClimateEntity
from homeassistant.components.climate.const import (
    HVACAction,
    HVACMode,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DATA_COORDINATOR, DOMAIN
from .entity import SmobotEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Smobot climate entity."""
    coordinator = hass.data[DOMAIN][entry.entry_id][DATA_COORDINATOR]
    async_add_entities([SmobotClimate(coordinator)])


class SmobotClimate(SmobotEntity, ClimateEntity):
    """Climate representation of the Smobot grill controller."""

    _attr_translation_key = "grill"
    _attr_hvac_modes = [HVACMode.HEAT]

    def __init__(self, coordinator) -> None:
        """Initialize the climate entity."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{self.entity_id_prefix}_grill"

    @property
    def temperature_unit(self) -> str:
        """Return the configured temperature unit."""
        return self.native_temperature_unit

    @property
    def current_temperature(self) -> float | None:
        """Return the current grill temperature."""
        return self.api_to_native_temperature(self.smobot_status.grill_temperature_value)

    @property
    def target_temperature(self) -> float | None:
        """Return the target grill temperature."""
        return self.api_to_native_temperature(self.coordinator.grill_setpoint_value)

    @property
    def hvac_mode(self) -> HVACMode:
        """Return the current HVAC mode."""
        return HVACMode.HEAT

    @property
    def hvac_action(self) -> HVACAction:
        """Return the current device action."""
        return HVACAction.HEATING if self.smobot_status.is_active else HVACAction.IDLE

    @property
    def extra_state_attributes(self):
        """Return extra climate diagnostics."""
        attrs = {}
        if self.smobot_status.grill_temperature_value is not None:
            attrs["current_temperature_f"] = self.smobot_status.grill_temperature_value
        if self.coordinator.grill_setpoint_value is not None:
            attrs["target_temperature_f"] = self.coordinator.grill_setpoint_value
        return attrs
