"""Climate platform for Smobot."""

from __future__ import annotations

from homeassistant.components.climate import ClimateEntity
from homeassistant.components.climate.const import (
    ClimateEntityFeature,
    HVACAction,
    HVACMode,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_TEMPERATURE, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    CONF_MAX_SETPOINT,
    CONF_MIN_SETPOINT,
    CONF_TEMPERATURE_UNIT,
    DATA_COORDINATOR,
    DEFAULT_MAX_SETPOINT,
    DEFAULT_MIN_SETPOINT,
    DEFAULT_TEMPERATURE_UNIT,
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
        return (
            UnitOfTemperature.CELSIUS
            if self.coordinator.entry.options.get(
                CONF_TEMPERATURE_UNIT,
                DEFAULT_TEMPERATURE_UNIT,
            )
            == "C"
            else UnitOfTemperature.FAHRENHEIT
        )

    @property
    def current_temperature(self) -> float | None:
        """Return the current grill temperature."""
        if self.smobot_status.grill_temperature_value is None:
            return None
        return float(self.smobot_status.grill_temperature_value)

    @property
    def target_temperature(self) -> float | None:
        """Return the target grill temperature."""
        if self.smobot_status.grill_setpoint_value is None:
            return None
        return float(self.smobot_status.grill_setpoint_value)

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
                DEFAULT_MIN_SETPOINT,
            )
        )

    @property
    def max_temp(self) -> float:
        """Return the maximum setpoint."""
        return float(
            self.coordinator.entry.options.get(
                CONF_MAX_SETPOINT,
                DEFAULT_MAX_SETPOINT,
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
        await self.coordinator.client.async_set_setpoint(int(clamped_temperature))
        await self.coordinator.async_request_refresh()
