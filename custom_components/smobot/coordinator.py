"""Coordinator for Smobot data updates."""

from __future__ import annotations

from datetime import datetime, timedelta
import logging

from aiohttp import ClientError
from homeassistant.components import persistent_notification
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.util.dt import utcnow
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
        self._optimistic_grill_setpoint_f: int | None = None
        self._optimistic_grill_setpoint_until: datetime | None = None
        self._cook_elapsed_before_pause = timedelta(0)
        self._local_cook_started_at: datetime | None = None
        self._cook_prompt_sent = False

    async def _async_update_data(self) -> SmobotStatus:
        """Fetch data from the device."""
        try:
            status = await self.client.async_get_status()
        except (ClientError, KeyError, TypeError, ValueError) as err:
            raise UpdateFailed(
                f"Error communicating with Smobot at {self.client.host}: {err}"
            ) from err
        self._update_optimistic_setpoint(status)
        self._update_local_cook_timer(status)
        return status

    @property
    def grill_setpoint_value(self) -> int | None:
        """Return the best available grill setpoint in API Fahrenheit units."""
        if self.data is not None and self.data.grill_setpoint_value is not None:
            return self.data.grill_setpoint_value
        if (
            self._optimistic_grill_setpoint_f is not None
            and self._optimistic_grill_setpoint_until is not None
            and utcnow() < self._optimistic_grill_setpoint_until
        ):
            return self._optimistic_grill_setpoint_f
        return None

    async def async_set_grill_setpoint(self, value_f: int) -> None:
        """Set the grill setpoint and keep a short optimistic local value."""
        await self.client.async_set_setpoint(value_f)
        self._optimistic_grill_setpoint_f = value_f
        self._optimistic_grill_setpoint_until = utcnow() + timedelta(minutes=10)
        await self.async_request_refresh()

    @property
    def local_cook_elapsed(self) -> timedelta | None:
        """Return locally tracked cook elapsed time."""
        if self._local_cook_started_at is not None:
            return self._cook_elapsed_before_pause + (
                utcnow() - self._local_cook_started_at
            )
        if self._cook_elapsed_before_pause > timedelta(0):
            return self._cook_elapsed_before_pause
        return None

    @property
    def cook_timer_running(self) -> bool:
        """Return whether the local cook timer is running."""
        return self._local_cook_started_at is not None

    async def async_start_cook_timer(self) -> None:
        """Start or resume the local cook timer."""
        if self._local_cook_started_at is None:
            self._local_cook_started_at = utcnow()
            self._cook_prompt_sent = True
            await self.async_request_refresh()

    async def async_pause_cook_timer(self) -> None:
        """Pause the local cook timer."""
        if self._local_cook_started_at is None:
            return
        self._cook_elapsed_before_pause += utcnow() - self._local_cook_started_at
        self._local_cook_started_at = None
        await self.async_request_refresh()

    async def async_reset_cook_timer(self) -> None:
        """Reset the local cook timer."""
        self._cook_elapsed_before_pause = timedelta(0)
        self._local_cook_started_at = None
        self._cook_prompt_sent = False
        persistent_notification.async_dismiss(
            self.hass,
            notification_id=f"{DOMAIN}_{self.entry.entry_id}_cook_timer",
        )
        await self.async_request_refresh()

    def _update_optimistic_setpoint(self, status: SmobotStatus) -> None:
        """Clear optimistic setpoint state once the device reports a real value."""
        if status.grill_setpoint_value is not None:
            self._optimistic_grill_setpoint_f = None
            self._optimistic_grill_setpoint_until = None
            return
        if (
            self._optimistic_grill_setpoint_until is not None
            and utcnow() >= self._optimistic_grill_setpoint_until
        ):
            self._optimistic_grill_setpoint_f = None
            self._optimistic_grill_setpoint_until = None

    def _cook_timer_can_start(self, status: SmobotStatus) -> bool:
        """Return whether the device is reporting valid cook values."""
        return (
            status.grill_temperature_value is not None
            and status.grill_setpoint_value is not None
        )

    def _maybe_prompt_for_cook_timer(self, status: SmobotStatus) -> None:
        """Prompt once when a valid cook appears but the timer is not running."""
        if (
            self._cook_prompt_sent
            or self.cook_timer_running
            or self.local_cook_elapsed is not None
            or not self._cook_timer_can_start(status)
        ):
            return None
        persistent_notification.async_create(
            self.hass,
            "The Smobot is reporting valid grill and set temperatures. "
            "Do you want to start a cook timer? Use the Smobot Start cook timer "
            "button to begin.",
            title="Start Smobot cook timer?",
            notification_id=f"{DOMAIN}_{self.entry.entry_id}_cook_timer",
        )
        self._cook_prompt_sent = True

    def _update_local_cook_timer(self, status: SmobotStatus) -> None:
        """Prompt for a local cook timer when the device is ready."""
        self._maybe_prompt_for_cook_timer(status)


def _as_timedelta(value: timedelta | int) -> timedelta:
    """Normalize stored polling interval values."""
    if isinstance(value, timedelta):
        return value
    return timedelta(seconds=value)
