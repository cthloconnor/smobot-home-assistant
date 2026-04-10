"""Sensor platform for Smobot."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity, SensorEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory, PERCENTAGE, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .client import SmobotStatus
from .const import CONF_TEMPERATURE_UNIT, DATA_COORDINATOR, DEFAULT_TEMPERATURE_UNIT, DOMAIN
from .entity import SmobotEntity


@dataclass(frozen=True, kw_only=True)
class SmobotSensorEntityDescription(SensorEntityDescription):
    """Describe a Smobot sensor."""

    value_fn: Callable[[SmobotStatus], int | str | None]
    diagnostic: bool = False
    temperature: bool = False


SENSORS: tuple[SmobotSensorEntityDescription, ...] = (
    SmobotSensorEntityDescription(
        key="grill_temperature",
        translation_key="grill_temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        suggested_display_precision=0,
        value_fn=lambda status: status.grill_temperature_value,
        temperature=True,
    ),
    SmobotSensorEntityDescription(
        key="food_probe_1",
        translation_key="food_probe_1",
        device_class=SensorDeviceClass.TEMPERATURE,
        suggested_display_precision=0,
        value_fn=lambda status: status.food_probe_1,
        temperature=True,
    ),
    SmobotSensorEntityDescription(
        key="food_probe_2",
        translation_key="food_probe_2",
        device_class=SensorDeviceClass.TEMPERATURE,
        suggested_display_precision=0,
        value_fn=lambda status: status.food_probe_2,
        temperature=True,
    ),
    SmobotSensorEntityDescription(
        key="damper_state",
        translation_key="damper_state",
        icon="mdi:air-filter",
        native_unit_of_measurement=PERCENTAGE,
        value_fn=lambda status: status.damper_state,
        diagnostic=True,
    ),
    SmobotSensorEntityDescription(
        key="damper_mode",
        translation_key="damper_mode",
        icon="mdi:valve",
        value_fn=lambda status: status.damper_mode,
        diagnostic=True,
    ),
    SmobotSensorEntityDescription(
        key="cook_time",
        translation_key="cook_time",
        icon="mdi:timer-outline",
        value_fn=lambda status: status.cook_time,
        diagnostic=True,
    ),
    SmobotSensorEntityDescription(
        key="error",
        translation_key="error",
        icon="mdi:alert-circle-outline",
        value_fn=lambda status: status.error_value,
        diagnostic=True,
    ),
    SmobotSensorEntityDescription(
        key="proportional",
        translation_key="proportional",
        icon="mdi:calculator-variant-outline",
        value_fn=lambda status: status.proportional,
        diagnostic=True,
    ),
    SmobotSensorEntityDescription(
        key="integral",
        translation_key="integral",
        icon="mdi:calculator-variant-outline",
        value_fn=lambda status: status.integral,
        diagnostic=True,
    ),
    SmobotSensorEntityDescription(
        key="kp",
        translation_key="kp",
        icon="mdi:tune",
        value_fn=lambda status: status.kp,
        diagnostic=True,
    ),
    SmobotSensorEntityDescription(
        key="ki",
        translation_key="ki",
        icon="mdi:tune",
        value_fn=lambda status: status.ki,
        diagnostic=True,
    ),
    SmobotSensorEntityDescription(
        key="kd",
        translation_key="kd",
        icon="mdi:tune",
        value_fn=lambda status: status.kd,
        diagnostic=True,
    ),
    SmobotSensorEntityDescription(
        key="device_state",
        translation_key="device_state",
        icon="mdi:state-machine",
        value_fn=lambda status: status.device_state,
        diagnostic=True,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Smobot sensors from a config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id][DATA_COORDINATOR]
    async_add_entities(SmobotSensor(coordinator, description) for description in SENSORS)


class SmobotSensor(SmobotEntity, SensorEntity):
    """Representation of a Smobot sensor."""

    entity_description: SmobotSensorEntityDescription

    def __init__(
        self,
        coordinator,
        description: SmobotSensorEntityDescription,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{self.entity_id_prefix}_{description.key}"
        if description.diagnostic:
            self._attr_entity_category = EntityCategory.DIAGNOSTIC
            self._attr_entity_registry_enabled_default = False

    @property
    def native_value(self):
        """Return the sensor state."""
        return self.entity_description.value_fn(self.smobot_status)

    @property
    def native_unit_of_measurement(self):
        """Return the sensor unit."""
        if not self.entity_description.temperature:
            return self.entity_description.native_unit_of_measurement
        unit = self.coordinator.entry.options.get(
            CONF_TEMPERATURE_UNIT,
            DEFAULT_TEMPERATURE_UNIT,
        )
        return (
            UnitOfTemperature.CELSIUS
            if unit == "C"
            else UnitOfTemperature.FAHRENHEIT
        )
