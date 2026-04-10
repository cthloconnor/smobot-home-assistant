"""Config flow for the Smobot integration."""

from __future__ import annotations

from datetime import timedelta
from typing import Any

from aiohttp import ClientError
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.helpers.device_registry import format_mac
from homeassistant.helpers.service_info.dhcp import DhcpServiceInfo
from homeassistant.const import CONF_HOST, CONF_NAME
from homeassistant.core import callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .client import SmobotApiClient
from .const import (
    CONF_MAX_SETPOINT,
    CONF_MIN_SETPOINT,
    CONF_SCAN_INTERVAL,
    CONF_TEMPERATURE_UNIT,
    DEFAULT_MAX_SETPOINT,
    DEFAULT_MIN_SETPOINT,
    DEFAULT_NAME,
    DEFAULT_SCAN_INTERVAL,
    DEFAULT_TEMPERATURE_UNIT,
    DOMAIN,
)


async def _validate_input(hass, user_input: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input."""
    client = SmobotApiClient(user_input[CONF_HOST], async_get_clientsession(hass))
    status = await client.async_get_status()
    return {
        "title": user_input[CONF_NAME],
        "grill_temperature": status.grill_temperature,
    }


class SmobotConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Smobot."""

    VERSION = 1
    MINOR_VERSION = 1

    def __init__(self) -> None:
        """Initialize the flow."""
        self._discovered_host: str | None = None
        self._discovered_unique_id: str | None = None

    async def async_step_dhcp(self, discovery_info: DhcpServiceInfo):
        """Handle DHCP discovery."""
        host = str(discovery_info.ip)
        self._async_abort_entries_match({CONF_HOST: host})

        if discovery_info.macaddress:
            self._discovered_unique_id = format_mac(discovery_info.macaddress)
            await self.async_set_unique_id(self._discovered_unique_id)
            self._abort_if_unique_id_configured(updates={CONF_HOST: host})
        else:
            await self._async_handle_discovery_without_unique_id()

        self._discovered_host = host
        self.context["title_placeholders"] = {"name": host}
        return await self.async_step_confirm()

    async def async_step_confirm(self, user_input: dict[str, Any] | None = None):
        """Confirm discovered device setup."""
        if user_input is not None:
            return self.async_create_entry(
                title=user_input[CONF_NAME],
                data={CONF_HOST: self._discovered_host},
            )

        return self.async_show_form(
            step_id="confirm",
            data_schema=vol.Schema(
                {vol.Required(CONF_NAME, default=DEFAULT_NAME): str}
            ),
            description_placeholders={"host": self._discovered_host or ""},
        )

    async def async_step_user(self, user_input: dict[str, Any] | None = None):
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            self._async_abort_entries_match({CONF_HOST: user_input[CONF_HOST]})
            await self.async_set_unique_id(user_input[CONF_HOST])
            self._abort_if_unique_id_configured()

            try:
                info = await _validate_input(self.hass, user_input)
            except ClientError:
                errors["base"] = "cannot_connect"
            except (KeyError, TypeError, ValueError):
                errors["base"] = "invalid_response"
            else:
                return self.async_create_entry(title=info["title"], data=user_input)

        data_schema = vol.Schema(
            {
                vol.Required(CONF_NAME, default=DEFAULT_NAME): str,
                vol.Required(CONF_HOST): str,
            }
        )
        return self.async_show_form(step_id="user", data_schema=data_schema, errors=errors)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Return the options flow handler."""
        return SmobotOptionsFlow(config_entry)


class SmobotOptionsFlow(config_entries.OptionsFlow):
    """Smobot options flow."""

    def __init__(self, config_entry) -> None:
        """Initialize the options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input: dict[str, Any] | None = None):
        """Manage the Smobot options."""
        if user_input is not None:
            if user_input[CONF_MIN_SETPOINT] >= user_input[CONF_MAX_SETPOINT]:
                return self.async_show_form(
                    step_id="init",
                    data_schema=self._build_options_schema(),
                    errors={"base": "invalid_setpoint_range"},
                )

            user_input[CONF_SCAN_INTERVAL] = timedelta(
                seconds=user_input[CONF_SCAN_INTERVAL]
            )
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=self._build_options_schema(),
        )

    def _build_options_schema(self, default_unit: str | None = None) -> vol.Schema:
        """Build the options form schema."""
        if default_unit is None:
            default_unit = self.config_entry.options.get(
                CONF_TEMPERATURE_UNIT,
                DEFAULT_TEMPERATURE_UNIT,
            )

        scan_interval = self.config_entry.options.get(
            CONF_SCAN_INTERVAL,
            DEFAULT_SCAN_INTERVAL,
        )
        if isinstance(scan_interval, int):
            scan_interval = timedelta(seconds=scan_interval)

        return vol.Schema(
            {
                vol.Required(
                    CONF_SCAN_INTERVAL,
                    default=int(scan_interval.total_seconds()),
                ): vol.All(vol.Coerce(int), vol.Range(min=5, max=300)),
                vol.Required(
                    CONF_TEMPERATURE_UNIT,
                    default=default_unit,
                ): vol.In({"F": "Fahrenheit", "C": "Celsius"}),
                vol.Required(
                    CONF_MIN_SETPOINT,
                    default=self.config_entry.options.get(
                        CONF_MIN_SETPOINT,
                        DEFAULT_MIN_SETPOINT,
                    ),
                ): vol.All(vol.Coerce(int), vol.Range(min=1, max=1000)),
                vol.Required(
                    CONF_MAX_SETPOINT,
                    default=self.config_entry.options.get(
                        CONF_MAX_SETPOINT,
                        DEFAULT_MAX_SETPOINT,
                    ),
                ): vol.All(vol.Coerce(int), vol.Range(min=1, max=1000)),
            }
        )
