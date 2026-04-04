"""Number platform for Smobot."""

from __future__ import annotations

from homeassistant.components.number import NumberDeviceClass, NumberEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTemperature
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
    """Set up Smobot number entities."""
    coordinator = hass.data[DOMAIN][entry.entry_id][DATA_COORDINATOR]
    async_add_entities([SmobotSetpointNumber(coordinator)])


class SmobotSetpointNumber(SmobotEntity, NumberEntity):
    """Number entity that controls the grill setpoint."""

    _attr_translation_key = "grill_setpoint"
    _attr_device_class = NumberDeviceClass.TEMPERATURE
    _attr_native_step = 1

    def __init__(self, coordinator) -> None:
        """Initialize the number entity."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{self.entity_id_prefix}_grill_setpoint"

    @property
    def native_value(self) -> float:
        """Return the current setpoint."""
        return float(self.smobot_status.grill_setpoint)

    @property
    def native_min_value(self) -> float:
        """Return the minimum setpoint."""
        return float(
            self.coordinator.entry.options.get(
                CONF_MIN_SETPOINT,
                DEFAULT_MIN_SETPOINT,
            )
        )

    @property
    def native_max_value(self) -> float:
        """Return the maximum setpoint."""
        return float(
            self.coordinator.entry.options.get(
                CONF_MAX_SETPOINT,
                DEFAULT_MAX_SETPOINT,
            )
        )

    @property
    def native_unit_of_measurement(self) -> str:
        """Return the configured unit."""
        return (
            UnitOfTemperature.CELSIUS
            if self.coordinator.entry.options.get(
                CONF_TEMPERATURE_UNIT,
                DEFAULT_TEMPERATURE_UNIT,
            )
            == "C"
            else UnitOfTemperature.FAHRENHEIT
        )

    async def async_set_native_value(self, value: float) -> None:
        """Update the grill setpoint on the device."""
        await self.coordinator.client.async_set_setpoint(int(value))
        await self.coordinator.async_request_refresh()
