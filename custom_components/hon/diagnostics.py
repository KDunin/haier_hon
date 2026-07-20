"""Diagnostics support for the hOn integration.

Exposes the standard HA "Download diagnostics" action on both the config
entry and individual devices. This is the primary tool for debugging when
Haier changes their cloud API: attach the downloaded JSON to a GitHub issue
and the exact shape of the (anonymized) appliance payload is right there.
"""

from __future__ import annotations

from typing import Any

from homeassistant.components.diagnostics import async_redact_data
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_EMAIL, CONF_PASSWORD
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntry
from pyhon.appliance import HonAppliance

from .const import CONF_REFRESH_TOKEN, DOMAIN

# Credentials and tokens - never useful for debugging, always sensitive.
TO_REDACT_ENTRY = {CONF_EMAIL, CONF_PASSWORD, CONF_REFRESH_TOKEN}


def _appliance_summary(appliance: HonAppliance) -> dict[str, Any]:
    """Small, structured overview of one appliance for the entry-level dump."""
    return {
        "appliance_type": appliance.appliance_type,
        "model_name": appliance.model_name,
        "connection": appliance.connection,
    }


def _appliance_dump(appliance: HonAppliance) -> dict[str, Any]:
    """Full per-appliance diagnostics.

    Uses pyhOn's own `diagnose` export, which already anonymizes serial
    numbers, MAC addresses, nicknames and coordinates - the same payload
    the "Show Device Info" button produces, just surfaced through HA's
    standard diagnostics download instead of a persistent notification.
    """
    return {
        **_appliance_summary(appliance),
        "diagnose": appliance.diagnose,
    }


def _find_appliance(hass: HomeAssistant, entry: ConfigEntry, unique_id: str) -> HonAppliance | None:
    hon = hass.data[DOMAIN][entry.unique_id]["hon"]
    for appliance in hon.appliances:
        if appliance.unique_id == unique_id:
            return appliance
    return None


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: ConfigEntry
) -> dict[str, Any]:
    """Return diagnostics for the whole config entry (all appliances)."""
    hon = hass.data[DOMAIN][entry.unique_id]["hon"]
    return {
        "entry_data": async_redact_data(dict(entry.data), TO_REDACT_ENTRY),
        "appliance_count": len(hon.appliances),
        "appliances": [_appliance_dump(appliance) for appliance in hon.appliances],
    }


async def async_get_device_diagnostics(
    hass: HomeAssistant, entry: ConfigEntry, device: DeviceEntry
) -> dict[str, Any]:
    """Return diagnostics for a single device."""
    unique_id = next(iter(device.identifiers))[1]
    appliance = _find_appliance(hass, entry, unique_id)
    if appliance is None:
        return {"error": f"No matching appliance found for device {unique_id}"}
    return _appliance_dump(appliance)
