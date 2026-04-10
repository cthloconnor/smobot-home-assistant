"""Client for the local Smobot HTTP API."""

from __future__ import annotations

from dataclasses import dataclass
import logging
from typing import Any

from aiohttp import ClientError, ClientSession

_LOGGER = logging.getLogger(__name__)
SENTINEL_VALUE = 999


@dataclass(slots=True)
class SmobotStatus:
    """Normalized Smobot status payload."""

    cook_time: str
    grill_temperature: int
    food_probe_1_raw: int
    food_probe_2_raw: int
    error: int
    proportional: int
    integral: int
    damper_mode: int
    damper_state: int
    lid_open: bool
    grill_setpoint: int
    device_state: int
    ds: int
    sot: int
    kp: int
    ki: int
    kd: int
    flags: int

    @classmethod
    def from_api(cls, payload: dict[str, Any]) -> "SmobotStatus":
        """Build a normalized status object from the API payload."""
        return cls(
            cook_time=str(payload["time"]),
            grill_temperature=int(payload["grl"]),
            food_probe_1_raw=int(payload["fd1"]),
            food_probe_2_raw=int(payload["fd2"]),
            error=int(payload["err"]),
            proportional=int(payload["p"]),
            integral=int(payload["i"]),
            damper_mode=int(payload["d"]),
            damper_state=int(payload["dpr"]),
            lid_open=bool(payload["ld"]),
            grill_setpoint=int(payload["set"]),
            device_state=int(payload["ds"]),
            ds=int(payload["ds"]),
            sot=int(payload["sot"]),
            kp=int(payload["kp"]),
            ki=int(payload["ki"]),
            kd=int(payload["kd"]),
            flags=int(payload["flg"]),
        )

    @property
    def food_probe_1(self) -> int | None:
        """Return food probe 1 if the sensor is connected."""
        return None if self.food_probe_1_raw == SENTINEL_VALUE else self.food_probe_1_raw

    @property
    def food_probe_2(self) -> int | None:
        """Return food probe 2 if the sensor is connected."""
        return None if self.food_probe_2_raw == SENTINEL_VALUE else self.food_probe_2_raw

    @property
    def is_active(self) -> bool:
        """Return whether the Smobot appears to be actively controlling."""
        return self.grill_setpoint != SENTINEL_VALUE

    @property
    def has_error(self) -> bool:
        """Return whether the device reports an error."""
        return self.error != SENTINEL_VALUE

    @property
    def error_value(self) -> int | None:
        """Return a normalized error value."""
        return None if self.error == SENTINEL_VALUE else self.error

    @property
    def grill_setpoint_value(self) -> int | None:
        """Return the active setpoint if available."""
        return None if self.grill_setpoint == SENTINEL_VALUE else self.grill_setpoint


class SmobotApiClient:
    """Thin wrapper around the local Smobot AJAX API."""

    def __init__(self, host: str, session: ClientSession) -> None:
        """Initialize the API client."""
        self._host = host
        self._session = session
        self._base_url = f"http://{host}/ajax"

    @property
    def host(self) -> str:
        """Return the configured host."""
        return self._host

    async def async_get_status(self) -> SmobotStatus:
        """Fetch the latest Smobot status."""
        payload = await self._request_json("GET", "/smobot")
        _LOGGER.debug("Smobot status payload from %s: %s", self._host, payload)
        return SmobotStatus.from_api(payload)

    async def async_set_setpoint(self, value: int) -> dict[str, Any]:
        """Update the grill temperature setpoint."""
        return await self._request_json("POST", "/setgrillset", json={"setpoint": value})

    async def _request_json(
        self, method: str, path: str, json: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Execute an HTTP request against the local Smobot API."""
        url = f"{self._base_url}{path}"
        async with self._session.request(
            method,
            url,
            json=json,
            headers={
                "Accept": "*/*",
                "Content-Type": "application/json",
                "Accept-Encoding": "gzip, deflate",
                "Accept-Language": "en-us",
            },
            raise_for_status=True,
        ) as response:
            return await response.json()


__all__ = ["ClientError", "SmobotApiClient", "SmobotStatus"]
