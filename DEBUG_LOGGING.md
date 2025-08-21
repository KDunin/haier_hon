# Enhanced Logging for hOn Integration

This document explains how to use the enhanced logging that has been added to the hOn integration to debug why entities are not getting updated.

## What Was Added

The following logging enhancements have been added throughout the integration:

### 1. Main Integration (`__init__.py`)
- **Setup logging**: Tracks when the integration is set up and configured
- **Device connection logging**: Shows appliance connection status during setup
- **Update subscription logging**: Confirms when update subscriptions are established
- **Custom coordinator**: Enhanced coordinator with detailed update logging

### 2. Entity Base Class (`entity.py`)
- **Entity creation logging**: Tracks when entities are created
- **Update handling logging**: Shows when entities receive coordinator updates
- **Device status logging**: Displays connection and remote control status
- **State writing logging**: Confirms when HA states are written

### 3. All Entity Types
- **Sensor entities**: Log value updates, option processing, and state changes
- **Binary sensor entities**: Log state changes and availability checks
- **Switch entities**: Log on/off operations and availability status
- **Button entities**: Log button presses and command execution
- **Climate entities**: Log temperature and mode updates
- **Fan entities**: Log speed and percentage updates
- **Light entities**: Log brightness and state changes
- **Lock entities**: Log lock/unlock operations
- **Number entities**: Log value and range updates
- **Select entities**: Log option changes and availability

## How to Enable Debug Logging

### Option 1: Home Assistant Configuration (Recommended)
Add this to your `configuration.yaml`:

```yaml
logger:
  default: info
  logs:
    custom_components.hon: debug
```

### Option 2: Developer Tools > Services
Use the `logger.set_level` service:

```yaml
service: logger.set_level
data:
  custom_components.hon: debug
```

### Option 3: Command Line
If running Home Assistant from command line, use:

```bash
hass --log-level custom_components.hon=debug
```

## What to Look For

### 1. Integration Setup
Look for these log messages during startup:
```
INFO - Setting up hOn integration for entry: [entry_id]
INFO - Successfully created Hon instance for [email]
INFO - Setting up update subscription for [X] appliances
DEBUG - Appliance: [name] ([type]) - Connection: [status]
INFO - Update subscription established
INFO - Successfully set up hOn integration for entry: [entry_id]
```

### 2. Entity Updates
Look for these log messages when entities should update:
```
DEBUG - Entity [entity_id] handling coordinator update
DEBUG - Device [name] connection status: [status], remote control valid: [value]
DEBUG - Entity [entity_id] writing HA state
DEBUG - Entity [entity_id] successfully wrote HA state
```

### 3. Coordinator Updates
Look for these log messages when the coordinator receives updates:
```
DEBUG - Threadsafe callback triggered with args: [args], kwargs: [kwargs]
DEBUG - Threadsafe callback executed successfully
DEBUG - Coordinator hon received update data: [data]
INFO - Coordinator hon updating data for [X] listeners
DEBUG - Coordinator hon successfully updated data
```

### 4. Device Status
Look for these log messages to check device connectivity:
```
DEBUG - Device [name] connection status: [status], remote control valid: [value]
DEBUG - [Entity type] [entity_id] available: [status] (super=[status], remoteCtrValid=[value], connection=[status])
```

## Common Issues and What to Check

### Issue: No Updates at All
**Check for:**
- Integration setup logs
- Update subscription establishment
- Threadsafe callback execution

**Possible causes:**
- Device not connected
- Update subscription failed
- Coordinator not receiving data

### Issue: Some Entities Update, Others Don't
**Check for:**
- Entity availability logs
- Device connection status
- Remote control validity

**Possible causes:**
- Device disconnected
- Remote control disabled
- Entity-specific configuration issues

### Issue: Updates Received but Not Displayed
**Check for:**
- Entity update handling logs
- State writing logs
- Error messages in entity updates

**Possible causes:**
- Entity update errors
- State writing failures
- Invalid data values

## Testing the Logging

Run the test script to verify logging is working:

```bash
cd scripts
python test_logging.py
```

This will show sample log messages to confirm the logging system is functional.

## Troubleshooting

### No Logs Appearing
1. Check that debug logging is enabled for `custom_components.hon`
2. Restart Home Assistant after changing logging configuration
3. Check Home Assistant logs for any errors

### Too Many Logs
If you're getting overwhelmed with debug logs, you can:
1. Set specific entity types to info level
2. Focus on specific areas (e.g., only coordinator updates)
3. Use info level instead of debug for general operation

### Performance Impact
The enhanced logging has minimal performance impact, but if you experience issues:
1. Use info level instead of debug for production
2. Focus logging on specific problematic areas
3. Disable logging for working components

## Next Steps

1. **Enable debug logging** using one of the methods above
2. **Restart Home Assistant** to apply the changes
3. **Check the logs** for the specific entities that aren't updating
4. **Look for patterns** in the logs to identify the root cause
5. **Share relevant log sections** if you need additional help

The enhanced logging should provide clear visibility into why entities are not updating, making it much easier to diagnose and fix the issue.
