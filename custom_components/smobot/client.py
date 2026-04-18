"""Client for the local Smobot HTTP API."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta
import json
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
    raw_payload: dict[str, Any]

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
            raw_payload=dict(payload),
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
    def grill_temperature_value(self) -> int | None:
        """Return grill temperature if the device is reporting one."""
        return None if self.grill_temperature == SENTINEL_VALUE else self.grill_temperature

    @property
    def is_active(self) -> bool:
        """Return whether the Smobot appears to be actively controlling."""
        return self.grill_setpoint_value is not None

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
        if self.grill_setpoint <= 0 or self.grill_setpoint == SENTINEL_VALUE:
            return None
        return self.grill_setpoint

    @property
    def operating_state(self) -> str:
        """Return a human-readable operating state."""
        if self.grill_setpoint_value is None:
            return "idle"
        if self.grill_temperature_value is None:
            return "starting"
        return "active"

    @property
    def probe_status(self) -> str:
        """Return a human-readable summary of connected probes."""
        probes = int(self.food_probe_1 is not None) + int(self.food_probe_2 is not None)
        if probes == 0:
            return "no_probes"
        if probes == 1:
            return "one_probe"
        return "two_probes"

    @property
    def raw_payload_json(self) -> str:
        """Return the raw device payload as compact JSON."""
        return json.dumps(self.raw_payload, sort_keys=True, separators=(",", ":"))

    @property
    def damper_mode_label(self) -> str:
        """Return a friendly damper mode label."""
        if self.damper_mode == SENTINEL_VALUE:
            return "idle"
        if self.damper_mode == 0:
            return "auto"
        if self.damper_mode == 1:
            return "manual"
        return f"mode_{self.damper_mode}"


def format_elapsed_time(value: timedelta | None) -> str | None:
    """Format elapsed time as HH:MM:SS."""
    if value is None:
        return None
    total_seconds = max(0, int(value.total_seconds()))
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


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
        """Update the grill temperature setpoint and verify it was accepted."""
        setpoint = int(value)
        await self._request_json(
            "POST",
            "/setgrillset",
            json={"setpoint": setpoint},
            expect_json=False,
        )

        status = await self.async_get_status()
        if status.grill_setpoint_value == setpoint:
            return {}

        raise ValueError(
            "Smobot did not accept setpoint "
            f"{setpoint}; device reported {status.grill_setpoint}"
        )

    async def _request_json(
        self,
        method: str,
        path: str,
        json: dict[str, Any] | None = None,
        data: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
        expect_json: bool = True,
    ) -> dict[str, Any]:
        """Execute an HTTP request against the local Smobot API."""
        url = f"{self._base_url}{path}"
        headers = {
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "en-us",
        }
        if json is not None:
            headers["Content-Type"] = "application/json"
        async with self._session.request(
            method,
            url,
            json=json,
            data=data,
            params=params,
            headers=headers,
            raise_for_status=True,
        ) as response:
            if not expect_json:
                await response.read()
                return {}
            return await response.json()


__all__ = ["ClientError", "SmobotApiClient", "SmobotStatus"]
