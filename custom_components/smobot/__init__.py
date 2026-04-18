"""The Smobot integration."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .client import SmobotApiClient
from .const import DATA_CLIENT, DATA_COORDINATOR, DOMAIN, PLATFORMS
from .coordinator import SmobotDataUpdateCoordinator


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Smobot from a config entry."""
    session = async_get_clientsession(hass)
    client = SmobotApiClient(entry.data[CONF_HOST], session)
    coordinator = SmobotDataUpdateCoordinator(hass, entry, client)
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = {
        DATA_CLIENT: client,
        DATA_COORDINATOR: coordinator,
    }
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if entry_data := hass.data.get(DOMAIN, {}).get(entry.entry_id):
        entry_data[DATA_COORDINATOR].stop_local_cook_timer_updates()

    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)
    return unload_ok


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Reload a config entry when options change."""
    await async_unload_entry(hass, entry)
    return await async_setup_entry(hass, entry)
