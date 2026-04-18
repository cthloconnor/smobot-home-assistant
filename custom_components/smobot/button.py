"""Button platform for Smobot."""

from __future__ import annotations

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DATA_COORDINATOR, DOMAIN
from .entity import SmobotEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Smobot buttons."""
    coordinator = hass.data[DOMAIN][entry.entry_id][DATA_COORDINATOR]
    async_add_entities(
        [
            SmobotRefreshButton(coordinator),
            SmobotStartCookTimerButton(coordinator),
            SmobotPauseCookTimerButton(coordinator),
            SmobotResetCookTimerButton(coordinator),
        ]
    )


class SmobotRefreshButton(SmobotEntity, ButtonEntity):
    """Button that manually refreshes Smobot data."""

    _attr_translation_key = "refresh"
    _attr_icon = "mdi:refresh"
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, coordinator) -> None:
        """Initialize the refresh button."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{self.entity_id_prefix}_refresh"

    async def async_press(self) -> None:
        """Refresh Smobot state from the device."""
        await self.coordinator.async_request_refresh()


class SmobotStartCookTimerButton(SmobotEntity, ButtonEntity):
    """Button that starts or resumes the local cook timer."""

    _attr_translation_key = "start_cook_timer"
    _attr_icon = "mdi:play"

    def __init__(self, coordinator) -> None:
        """Initialize the start timer button."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{self.entity_id_prefix}_start_cook_timer"

    async def async_press(self) -> None:
        """Start or resume the local cook timer."""
        await self.coordinator.async_start_cook_timer()


class SmobotPauseCookTimerButton(SmobotEntity, ButtonEntity):
    """Button that pauses the local cook timer."""

    _attr_translation_key = "pause_cook_timer"
    _attr_icon = "mdi:pause"

    def __init__(self, coordinator) -> None:
        """Initialize the pause timer button."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{self.entity_id_prefix}_pause_cook_timer"

    async def async_press(self) -> None:
        """Pause the local cook timer."""
        await self.coordinator.async_pause_cook_timer()


class SmobotResetCookTimerButton(SmobotEntity, ButtonEntity):
    """Button that resets the local cook timer."""

    _attr_translation_key = "reset_cook_timer"
    _attr_icon = "mdi:restart"

    def __init__(self, coordinator) -> None:
        """Initialize the reset timer button."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{self.entity_id_prefix}_reset_cook_timer"

    async def async_press(self) -> None:
        """Reset the local cook timer."""
        await self.coordinator.async_reset_cook_timer()
