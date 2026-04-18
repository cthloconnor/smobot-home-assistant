"""Number platform for Smobot."""

from __future__ import annotations

from homeassistant.components.number import NumberDeviceClass, NumberEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import STATE_UNAVAILABLE, STATE_UNKNOWN
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.restore_state import RestoreEntity

from .const import (
    DATA_COORDINATOR,
    DEFAULT_MAX_FOOD_TARGET_F,
    DEFAULT_MIN_FOOD_TARGET_F,
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
    async_add_entities(
        [
            SmobotFoodProbeTargetNumber(coordinator, probe_number=1),
            SmobotFoodProbeTargetNumber(coordinator, probe_number=2),
        ]
    )


class SmobotFoodProbeTargetNumber(SmobotEntity, RestoreEntity, NumberEntity):
    """Local helper for food probe target temperatures."""

    _attr_device_class = NumberDeviceClass.TEMPERATURE
    _attr_native_step = 1

    def __init__(self, coordinator, probe_number: int) -> None:
        """Initialize the food probe target helper."""
        super().__init__(coordinator)
        self._probe_number = probe_number
        self._target_temperature_f: int | None = None
        self._attr_translation_key = f"food_probe_{probe_number}_target"
        self._attr_unique_id = (
            f"{self.entity_id_prefix}_food_probe_{probe_number}_target"
        )

    async def async_added_to_hass(self) -> None:
        """Restore the previous target temperature after restart."""
        await super().async_added_to_hass()
        last_state = await self.async_get_last_state()
        if last_state is None or last_state.state in (STATE_UNAVAILABLE, STATE_UNKNOWN):
            return

        if temperature_f := last_state.attributes.get("temperature_f"):
            self._target_temperature_f = int(round(float(temperature_f)))
            return

        self._target_temperature_f = self.native_to_api_temperature(
            float(last_state.state)
        )

    @property
    def native_value(self) -> float | None:
        """Return the configured food probe target."""
        return self.api_to_native_temperature(self._target_temperature_f)

    @property
    def native_min_value(self) -> float:
        """Return the minimum food target."""
        return float(self.api_to_native_temperature(DEFAULT_MIN_FOOD_TARGET_F))

    @property
    def native_max_value(self) -> float:
        """Return the maximum food target."""
        return float(self.api_to_native_temperature(DEFAULT_MAX_FOOD_TARGET_F))

    @property
    def native_unit_of_measurement(self) -> str:
        """Return the configured unit."""
        return self.native_temperature_unit

    async def async_set_native_value(self, value: float) -> None:
        """Update the local food probe target."""
        clamped_value = max(self.native_min_value, min(self.native_max_value, value))
        self._target_temperature_f = self.native_to_api_temperature(clamped_value)
        self.async_write_ha_state()

    @property
    def extra_state_attributes(self):
        """Return helper details and Fahrenheit conversion."""
        if self._target_temperature_f is None:
            return {"probe": self._probe_number}
        return {
            "probe": self._probe_number,
            "temperature_f": self._target_temperature_f,
        }
