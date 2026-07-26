"""Regression tests for HonBinarySensorEntity.is_on.

Covers two bugs found in the induction hob (IH) zone entities:

1. Dotted keys like "attributes.parameters.onOffStatus" resolved to a raw
   pyhon HonAttribute object instead of its unwrapped value, so the
   on_value comparison always failed regardless of the real appliance
   state (fixed in pyhon.appliance.HonAppliance._get_nested_item).
2. Any dotted key was unconditionally zone-suffixed for zone sub-devices,
   even for device-wide fields with no per-zone variant (e.g. connection
   status), so those entities silently never got created for zoned
   appliances (fixed in pyhon.appliance.HonAppliance.__getitem__).

These tests exercise the real pyhon.appliance.HonAppliance class and the
real BINARY_SENSORS descriptions from this integration, bypassing only
the Home Assistant entity lifecycle (coordinator/hass wiring), which is
irrelevant to the bug.
"""

from typing import Any

import pytest
from pyhon.appliance import HonAppliance
from pyhon.attributes import HonAttribute

from hon.binary_sensor import BINARY_SENSORS, HonBinarySensorEntity


def make_appliance(
    zone: int,
    parameters: dict[str, str],
    extra_attributes: dict[str, Any] | None = None,
) -> HonAppliance:
    appliance = HonAppliance(
        None,
        {"applianceTypeId": 3, "macAddress": "aa-bb-cc-dd-ee-ff", "zone": "4"},
        zone=zone,
    )
    appliance._attributes = {
        "parameters": {name: HonAttribute(value) for name, value in parameters.items()},
        **(extra_attributes or {}),
    }
    return appliance


def make_entity(device: HonAppliance, description) -> HonBinarySensorEntity:
    entity = object.__new__(HonBinarySensorEntity)
    entity._device = device
    entity.entity_description = description
    entity._attr_unique_id = "test"
    return entity


def get_description(appliance_type: str, translation_key: str):
    for description in BINARY_SENSORS[appliance_type]:
        if description.translation_key == translation_key:
            return description
    raise AssertionError(f"No {translation_key!r} description for {appliance_type!r}")


@pytest.mark.parametrize(
    "zone, on_off_value, expected", [(1, "1", True), (2, "0", False)]
)
def test_ih_zone_on_sensor_reflects_real_zone_state(zone, on_off_value, expected):
    """Regression test: this is the exact entity (binary_sensor.<model>_z1_on)
    that always reported "off" regardless of the real hob state."""
    description = get_description("IH", "on")
    device = make_appliance(zone, {f"onOffStatusZ{zone}": on_off_value})
    entity = make_entity(device, description)
    assert entity.is_on is expected


def test_ih_zone_hot_and_pan_sensors_still_work():
    hot_description = get_description("IH", "still_hot")
    pan_description = get_description("IH", "pan_status")
    device = make_appliance(1, {"hotStatusZ1": "1", "panStatusZ1": "1"})
    assert make_entity(device, hot_description).is_on is True
    assert make_entity(device, pan_description).is_on is True


def test_ih_zone_connection_sensor_falls_back_to_device_wide_status():
    """Regression test: "Connection" has no per-zone variant, so a zone
    sub-device must fall back to the shared attributes.lastConnEvent.category
    instead of silently never resolving (it used to look for a
    nonexistent "...categoryZ1" key)."""
    description = get_description("IH", "connection")
    device = make_appliance(
        1,
        {"onOffStatusZ1": "1"},
        extra_attributes={"lastConnEvent": {"category": "CONNECTED"}},
    )
    assert make_entity(device, description).is_on is True


def test_ov_on_sensor_reflects_real_state():
    description = get_description("OV", "on")
    device = make_appliance(0, {"onOffStatus": "1"})
    assert make_entity(device, description).is_on is True


def test_ap_on_sensor_reflects_real_state():
    """Regression test: on_value was the string "1", but pyhon returns
    the numeric value 1 for this field, so the comparison always failed."""
    description = get_description("AP", "on")
    device = make_appliance(0, {"onOffStatus": "1"})
    assert make_entity(device, description).is_on is True


@pytest.mark.parametrize("appliance_type", list(BINARY_SENSORS))
def test_on_value_type_matches_what_pyhon_returns_for_numeric_fields(appliance_type):
    """Static guard against the AP-style bug: any description whose
    on_value looks like a bare digit must use an int/float, not a string,
    since pyhon always unwraps numeric attribute values to int/float."""
    for description in BINARY_SENSORS[appliance_type]:
        if (
            isinstance(description.on_value, str)
            and description.on_value.strip("-").isdigit()
        ):
            pytest.fail(
                f"{appliance_type}/{description.translation_key}: on_value="
                f"{description.on_value!r} is a numeric-looking string; pyhon "
                "unwraps numeric parameter values to int/float, so this "
                "comparison will never match. Use an int instead."
            )
