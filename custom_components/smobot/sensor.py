"""Sensor platform for Smobot."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity, SensorEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory, PERCENTAGE, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .client import SmobotStatus, format_elapsed_time
from .const import DATA_COORDINATOR, DOMAIN
from .entity import SmobotEntity


@dataclass(frozen=True, kw_only=True)
class SmobotSensorEntityDescription(SensorEntityDescription):
    """Describe a Smobot sensor."""

    value_fn: Callable[[SmobotStatus], int | str | None]
    diagnostic: bool = False
    temperature: bool = False
    fahrenheit_helper: bool = False


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
        key="grill_setpoint",
        translation_key="grill_setpoint",
        device_class=SensorDeviceClass.TEMPERATURE,
        suggested_display_precision=0,
        value_fn=lambda status: status.grill_setpoint_value,
        temperature=True,
    ),
    SmobotSensorEntityDescription(
        key="grill_temperature_f",
        translation_key="grill_temperature_f",
        device_class=SensorDeviceClass.TEMPERATURE,
        suggested_display_precision=0,
        value_fn=lambda status: status.grill_temperature_value,
        fahrenheit_helper=True,
    ),
    SmobotSensorEntityDescription(
        key="food_probe_1_f",
        translation_key="food_probe_1_f",
        device_class=SensorDeviceClass.TEMPERATURE,
        suggested_display_precision=0,
        value_fn=lambda status: status.food_probe_1,
        fahrenheit_helper=True,
    ),
    SmobotSensorEntityDescription(
        key="food_probe_2_f",
        translation_key="food_probe_2_f",
        device_class=SensorDeviceClass.TEMPERATURE,
        suggested_display_precision=0,
        value_fn=lambda status: status.food_probe_2,
        fahrenheit_helper=True,
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
        value_fn=lambda status: status.damper_mode_label,
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
    SmobotSensorEntityDescription(
        key="operating_state",
        translation_key="operating_state",
        icon="mdi:grill-outline",
        value_fn=lambda status: status.operating_state,
        diagnostic=True,
    ),
    SmobotSensorEntityDescription(
        key="probe_status",
        translation_key="probe_status",
        icon="mdi:thermometer-lines",
        value_fn=lambda status: status.probe_status,
        diagnostic=True,
    ),
    SmobotSensorEntityDescription(
        key="raw_payload",
        translation_key="raw_payload",
        icon="mdi:code-json",
        value_fn=lambda status: status.raw_payload_json,
        diagnostic=True,
    ),
    SmobotSensorEntityDescription(
        key="local_cook_timer",
        translation_key="local_cook_timer",
        icon="mdi:timer-sand",
        value_fn=lambda status: None,
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
        if description.diagnostic or description.fahrenheit_helper:
            self._attr_entity_category = EntityCategory.DIAGNOSTIC
            self._attr_entity_registry_enabled_default = False

    @property
    def native_value(self):
        """Return the sensor state."""
        if self.entity_description.key == "local_cook_timer":
            return format_elapsed_time(self.coordinator.local_cook_elapsed)
        if self.entity_description.fahrenheit_helper:
            return self.entity_description.value_fn(self.smobot_status)
        if self.entity_description.temperature:
            return self.api_to_native_temperature(
                self.entity_description.value_fn(self.smobot_status)
            )
        return self.entity_description.value_fn(self.smobot_status)

    @property
    def native_unit_of_measurement(self):
        """Return the sensor unit."""
        if self.entity_description.fahrenheit_helper:
            return UnitOfTemperature.FAHRENHEIT
        if not self.entity_description.temperature:
            return self.entity_description.native_unit_of_measurement
        return self.native_temperature_unit

    @property
    def extra_state_attributes(self):
        """Return secondary Fahrenheit temperature values where helpful."""
        if self.entity_description.fahrenheit_helper:
            return {}
        if not self.entity_description.temperature:
            return {}
        raw_value = self.entity_description.value_fn(self.smobot_status)
        if raw_value is None:
            return {}
        return {"temperature_f": raw_value}
