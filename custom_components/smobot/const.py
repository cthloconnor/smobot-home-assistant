"""Constants for the Smobot integration."""

from datetime import timedelta

DOMAIN = "smobot"
DEFAULT_NAME = "Smobot"
DEFAULT_PORT = 80
DEFAULT_SCAN_INTERVAL = timedelta(seconds=30)
DEFAULT_TEMPERATURE_UNIT = "C"
DEFAULT_MIN_FOOD_TARGET_F = 50
DEFAULT_MAX_FOOD_TARGET_F = 250

CONF_SCAN_INTERVAL = "scan_interval"
CONF_TEMPERATURE_UNIT = "temperature_unit"
DATA_CLIENT = "client"
DATA_COORDINATOR = "coordinator"

PLATFORMS = ["sensor", "number", "binary_sensor", "climate", "button"]
