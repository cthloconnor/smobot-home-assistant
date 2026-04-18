"""Constants for the Smobot integration."""

from datetime import timedelta

DOMAIN = "smobot"
DEFAULT_NAME = "Smobot"
DEFAULT_PORT = 80
DEFAULT_SCAN_INTERVAL = timedelta(seconds=30)
DEFAULT_TEMPERATURE_UNIT = "C"
DEFAULT_MIN_SETPOINT_F = 150
DEFAULT_MAX_SETPOINT_F = 450
DEFAULT_MIN_SETPOINT = DEFAULT_MIN_SETPOINT_F
DEFAULT_MAX_SETPOINT = DEFAULT_MAX_SETPOINT_F
DEFAULT_MIN_FOOD_TARGET_F = 50
DEFAULT_MAX_FOOD_TARGET_F = 250

CONF_SCAN_INTERVAL = "scan_interval"
CONF_TEMPERATURE_UNIT = "temperature_unit"
CONF_MIN_SETPOINT = "min_setpoint"
CONF_MAX_SETPOINT = "max_setpoint"
DATA_CLIENT = "client"
DATA_COORDINATOR = "coordinator"

PLATFORMS = ["sensor", "number", "binary_sensor", "climate", "button"]
