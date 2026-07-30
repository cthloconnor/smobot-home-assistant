"""The Smobot integration."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.entity_registry import RegistryEntryDisabler

from .client import SmobotApiClient
from .const import DATA_CLIENT, DATA_COORDINATOR, DOMAIN, PLATFORMS
from .coordinator import SmobotDataUpdateCoordinator

_TIMER_ENTITIES = (
    ("sensor", "local_cook_timer"),
    ("button", "start_cook_timer"),
    ("button", "pause_cook_timer"),
    ("button", "reset_cook_timer"),
)


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
    _enable_previously_hidden_timer_entities(hass, entry)
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


def _enable_previously_hidden_timer_entities(
    hass: HomeAssistant, entry: ConfigEntry
) -> None:
    """Enable timer entities that older versions disabled by default.

    Entries explicitly disabled by the user are intentionally left alone.
    """
    registry = er.async_get(hass)
    unique_id_prefix = entry.unique_id or entry.entry_id

    for platform, key in _TIMER_ENTITIES:
        entity_id = registry.async_get_entity_id(
            platform,
            DOMAIN,
            f"{unique_id_prefix}_{key}",
        )
        if entity_id is None:
            continue
        registry_entry = registry.async_get(entity_id)
        if (
            registry_entry is not None
            and registry_entry.disabled_by == RegistryEntryDisabler.INTEGRATION
        ):
            registry.async_update_entity(entity_id, disabled_by=None)
