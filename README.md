# SeaQuaComp Home Assistant Integration

[![GitHub Release][releases-shield]][releases]
[![License][license-shield]](LICENSE)
[![hacs][hacsbadge]][hacs]

_Home Assistant integration for SeaQuaComp aquarium controllers_

## Features

- **Water Temperature Monitoring**: Real-time temperature readings in Celsius
- **pH Level Monitoring**: Continuous pH monitoring for optimal aquarium conditions  
- **CO2 Level Monitoring**: Track CO2 concentration in parts per million (ppm)
- **Device Status**: Monitor device connectivity and online status


## Device Compatibility

The integration was tested only with SQCmini 3 but other SeaQuaComp devices with the same looking web page should be compatible as well.

## Installation

### HACS (Recommended)

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=igoro00&repository=ha-sqc&category=integration)

1. Have [HACS](https://hacs.xyz/) installed, this will allow you to easily manage and track updates.
2. Search for "SeaQuaComp" in HACS integrations.
3. Click Install below the found integration.
4. Restart Home Assistant.
5. In the HA UI go to "Configuration" -> "Integrations" click "+" and search for "SeaQuaComp".

### Manual Installation

1. Using the tool of choice open the directory (folder) for your HA configuration (where you find `configuration.yaml`).
2. If you do not have a `custom_components` directory (folder) there, you need to create it.
3. In the `custom_components` directory (folder) create a new folder called `ha-sqc`.
4. Download _all_ the files from the `custom_components/ha-sqc/` directory (folder) in this repository.
5. Place the files you downloaded in the new directory (folder) you created.
6. Restart Home Assistant.
7. In the HA UI go to "Configuration" -> "Integrations" click "+" and search for "SeaQuaComp".

## Configuration

### Through the UI

1. Go to Home Assistant Settings → Devices & Services → Integrations
2. Click "Add Integration" and search for "SeaQuaComp"
3. Enter the required information:
   - **Host**: IP address or hostname of your SeaQuaComp device (e.g., `192.168.1.100` or `http://192.168.1.100`)
   - **PIN**: 4-digit PIN code for your device

### Configuration Parameters

| Parameter | Required | Description | Example |
|-----------|----------|-------------|---------|
| Host | Yes | IP address or URL of your SeaQuaComp device | `192.168.1.100` or `http://aquarium.local` |
| PIN | Yes | 4-digit PIN code for device authentication | `1234` |

## Sensors

This integration provides the following sensors:

### Water Temperature
- **Entity ID**: `sensor.seaquacomp_water_temperature`
- **Unit**: °C (Celsius)
- **Device Class**: Temperature
- **Description**: Current water temperature reading

### Water pH
- **Entity ID**: `sensor.seaquacomp_water_ph`
- **Unit**: pH
- **Device Class**: pH
- **Description**: Current pH level of the water

### Water CO2
- **Entity ID**: `sensor.seaquacomp_water_co2`
- **Unit**: ppm (parts per million)
- **Device Class**: CO2
- **Description**: Current CO2 concentration in the water

### Device Status
- **Entity ID**: `binary_sensor.seaquacomp_online`
- **Device Class**: Connectivity
- **Description**: Indicates if the device is online and responding

## Usage Examples

### Automation Example

Create automations based on your aquarium parameters:

```yaml
automation:
  - alias: "High Temperature Alert"
    trigger:
      platform: numeric_state
      entity_id: sensor.seaquacomp_water_temperature
      above: 28
    action:
      service: notify.mobile_app_your_phone
      data:
        message: "⚠️ Aquarium temperature is too high: {{ states('sensor.seaquacomp_water_temperature') }}°C"

  - alias: "Low pH Alert"
    trigger:
      platform: numeric_state
      entity_id: sensor.seaquacomp_water_ph
      below: 6.5
    action:
      service: notify.mobile_app_your_phone
      data:
        message: "⚠️ Aquarium pH is too low: {{ states('sensor.seaquacomp_water_ph') }}"
```

### Dashboard Card Example

Add aquarium monitoring to your dashboard:

```yaml
type: entities
title: Aquarium Status
entities:
  - entity: sensor.seaquacomp_water_temperature
    name: Temperature
  - entity: sensor.seaquacomp_water_ph
    name: pH Level
  - entity: sensor.seaquacomp_water_co2
    name: CO2 Level
  - entity: binary_sensor.seaquacomp_online
    name: Device Status
```

## License

This project is under the GNU GPLv3 license.

---


[hacs]: https://github.com/hacs/integration
[hacsbadge]: https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge
[license-shield]: https://img.shields.io/github/license/igoro00/ha-sqc.svg?style=for-the-badge
[releases-shield]: https://img.shields.io/github/release/igoro00/ha-sqc.svg?style=for-the-badge
[releases]: https://github.com/igoro00/ha-sqc/releases
