"""Coordinator for Smobot data updates."""

from __future__ import annotations

from datetime import timedelta
import logging

from aiohttp import ClientError
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .client import SmobotApiClient, SmobotStatus
from .const import CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL, DOMAIN

_LOGGER = logging.getLogger(__name__)


class SmobotDataUpdateCoordinator(DataUpdateCoordinator[SmobotStatus]):
    """Fetch and cache Smobot state."""

    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
        client: SmobotApiClient,
    ) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            logger=_LOGGER,
            name=DOMAIN,
            update_interval=_as_timedelta(
                entry.options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
            ),
        )
        self.entry = entry
        self.client = client

    async def _async_update_data(self) -> SmobotStatus:
        """Fetch data from the device."""
        try:
            return await self.client.async_get_status()
        except (ClientError, KeyError, TypeError, ValueError) as err:
            raise UpdateFailed(f"Error communicating with Smobot at {self.client.host}: {err}") from err


def _as_timedelta(value: timedelta | int) -> timedelta:
    """Normalize stored polling interval values."""
    if isinstance(value, timedelta):
        return value
    return timedelta(seconds=value)
