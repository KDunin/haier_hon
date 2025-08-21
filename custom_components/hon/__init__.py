import asyncio
import logging
from pathlib import Path
from typing import Any

import voluptuous as vol  # type: ignore[import-untyped]
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_EMAIL, CONF_PASSWORD
from homeassistant.helpers import config_validation as cv, aiohttp_client
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from pyhon import Hon

from .const import DOMAIN, PLATFORMS, MOBILE_ID, CONF_REFRESH_TOKEN

_LOGGER = logging.getLogger(__name__)

HON_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_EMAIL): cv.string,
        vol.Required(CONF_PASSWORD): cv.string,
    }
)

CONFIG_SCHEMA = vol.Schema(
    {DOMAIN: vol.Schema(vol.All(cv.ensure_list, [HON_SCHEMA]))},
    extra=vol.ALLOW_EXTRA,
)


class HonDataUpdateCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Custom coordinator with enhanced logging for hOn integration."""

    def __init__(self, hass: HomeAssistant, name: str):
        super().__init__(hass, _LOGGER, name=name)
        _LOGGER.info("Initialized HonDataUpdateCoordinator: %s", name)

    def async_set_updated_data(self, data: dict[str, Any]) -> None:
        """Set updated data with enhanced logging."""
        _LOGGER.debug("Coordinator %s received update data: %s", self.name, data)
        _LOGGER.info("Coordinator %s updating data for %d listeners", self.name, len(self._listeners))

        try:
            super().async_set_updated_data(data)
            _LOGGER.debug("Coordinator %s successfully updated data", self.name)
        except Exception as e:
            _LOGGER.error("Coordinator %s failed to update data: %s", self.name, e, exc_info=True)
            raise


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    _LOGGER.info("Setting up hOn integration for entry: %s", entry.entry_id)

    session = aiohttp_client.async_get_clientsession(hass)
    if (config_dir := hass.config.config_dir) is None:
        raise ValueError("Missing Config Dir")

    try:
        hon = await Hon(
            email=entry.data[CONF_EMAIL],
            password=entry.data[CONF_PASSWORD],
            mobile_id=MOBILE_ID,
            session=session,
            test_data_path=Path(config_dir),
            refresh_token=entry.data.get(CONF_REFRESH_TOKEN, ""),
        ).create()
        _LOGGER.info("Successfully created Hon instance for %s", entry.data[CONF_EMAIL])
    except Exception as e:
        _LOGGER.error("Failed to create Hon instance: %s", e)
        raise

    # Save the new refresh token
    hass.config_entries.async_update_entry(
        entry, data={**entry.data, CONF_REFRESH_TOKEN: hon.api.auth.refresh_token}
    )

    coordinator: HonDataUpdateCoordinator = HonDataUpdateCoordinator(hass, DOMAIN)

    def make_threadsafe_callback(hass, coordinator):
        def wrapper(*args, **kwargs):
            _LOGGER.debug("Threadsafe callback triggered with args: %s, kwargs: %s", args, kwargs)
            try:
                # Schedule the coordinator update to run in the event loop
                hass.loop.call_soon_threadsafe(
                    lambda: coordinator.async_set_updated_data({})
                )
                _LOGGER.debug("Threadsafe callback executed successfully")
            except Exception as e:
                _LOGGER.error("Threadsafe callback failed: %s", e, exc_info=True)
        return wrapper

    # Subscribe to updates from the Hon instance
    _LOGGER.info("Setting up update subscription for %d appliances", len(hon.appliances))
    for appliance in hon.appliances:
        _LOGGER.debug("Appliance: %s (%s) - Connection: %s",
                     appliance.nick_name, appliance.appliance_type, appliance.connection)

    hon.subscribe_updates(make_threadsafe_callback(hass, coordinator))
    _LOGGER.info("Update subscription established")

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.unique_id] = {"hon": hon, "coordinator": coordinator}
    _LOGGER.info("Stored coordinator and hon instance in hass.data")

    await async_forward_entry_setups_with_error_handling(hass, entry)
    _LOGGER.info("Successfully set up hOn integration for entry: %s", entry.entry_id)
    return True


async def async_forward_entry_setups_with_error_handling(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Forward entry setups with error handling for duplicate setup errors."""
    try:
        _LOGGER.debug("Setting up platforms: %s", PLATFORMS)
        await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
        _LOGGER.debug("Successfully set up platforms: %s", PLATFORMS)
    except ValueError as e:
        if "has already been setup" in str(e):
            _LOGGER.debug("Platform %s already set up for entry %s, ignoring", PLATFORMS, entry.entry_id)
        else:
            # Re-raise other ValueError exceptions
            _LOGGER.error("ValueError setting up platform %s: %s", PLATFORMS, e)
            raise
    except Exception as e:
        # Re-raise all other exceptions
        _LOGGER.error("Error setting up platform %s: %s", PLATFORMS, e)
        raise


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    _LOGGER.info("Unloading hOn integration for entry: %s", entry.entry_id)

    refresh_token = hass.data[DOMAIN][entry.unique_id]["hon"].api.auth.refresh_token

    hass.config_entries.async_update_entry(
        entry, data={**entry.data, CONF_REFRESH_TOKEN: refresh_token}
    )
    unload = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload:
        if not hass.data[DOMAIN]:
            hass.data.pop(DOMAIN, None)
            _LOGGER.info("Removed DOMAIN from hass.data")
    _LOGGER.info("Unload result: %s", unload)
    return unload
