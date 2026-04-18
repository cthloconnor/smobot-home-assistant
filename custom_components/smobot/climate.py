"""Climate platform for Smobot."""

from __future__ import annotations

from homeassistant.components.climate import ClimateEntity
from homeassistant.components.climate.const import (
    ClimateEntityFeature,
    HVACAction,
    HVACMode,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_TEMPERATURE
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    CONF_MAX_SETPOINT,
    CONF_MIN_SETPOINT,
    DATA_COORDINATOR,
    DEFAULT_MAX_SETPOINT_F,
    DEFAULT_MIN_SETPOINT_F,
    DOMAIN,
)
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
    _attr_supported_features = ClimateEntityFeature.TARGET_TEMPERATURE

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
    def target_temperature_step(self) -> float:
        """Return target step size."""
        return 1.0

    @property
    def min_temp(self) -> float:
        """Return the minimum setpoint."""
        return float(
            self.coordinator.entry.options.get(
                CONF_MIN_SETPOINT,
                self.api_to_native_temperature(DEFAULT_MIN_SETPOINT_F),
            )
        )

    @property
    def max_temp(self) -> float:
        """Return the maximum setpoint."""
        return float(
            self.coordinator.entry.options.get(
                CONF_MAX_SETPOINT,
                self.api_to_native_temperature(DEFAULT_MAX_SETPOINT_F),
            )
        )

    @property
    def hvac_mode(self) -> HVACMode:
        """Return the current HVAC mode."""
        return HVACMode.HEAT

    @property
    def hvac_action(self) -> HVACAction:
        """Return the current device action."""
        return HVACAction.HEATING if self.smobot_status.is_active else HVACAction.IDLE

    async def async_set_temperature(self, **kwargs) -> None:
        """Set the grill setpoint."""
        if (temperature := kwargs.get(ATTR_TEMPERATURE)) is None:
            return
        clamped_temperature = max(self.min_temp, min(self.max_temp, float(temperature)))
        await self.coordinator.async_set_grill_setpoint(
            self.native_to_api_temperature(clamped_temperature)
        )

    @property
    def extra_state_attributes(self):
        """Return extra climate diagnostics."""
        attrs = {}
        if self.smobot_status.grill_temperature_value is not None:
            attrs["current_temperature_f"] = self.smobot_status.grill_temperature_value
        if self.coordinator.grill_setpoint_value is not None:
            attrs["target_temperature_f"] = self.coordinator.grill_setpoint_value
        return attrs
