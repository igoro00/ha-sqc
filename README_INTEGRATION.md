# SeaQuaComp Home Assistant Integration

A custom Home Assistant integration for SeaQuaComp devices that allows you to monitor sensors via REST API.

## Features

- **HACS Compatible**: Can be installed via HACS (Home Assistant Community Store)
- **UI Configuration**: Easy setup through Home Assistant's configuration UI
- **Secure Authentication**: PIN-based authentication (4-digit PIN required)
- **Multiple Sensors**: Supports temperature, humidity, and status sensors
- **Local Polling**: Connects directly to your device without cloud dependency

## Installation

### Via HACS (Recommended)

1. Make sure you have [HACS](https://hacs.xyz/) installed
2. Go to HACS → Integrations
3. Click the three dots in the top right corner and select "Custom repositories"
4. Add this repository URL and select "Integration" as the category
5. Click "Install"
6. Restart Home Assistant

### Manual Installation

1. Copy the `custom_components/homeassistant_template` folder to your Home Assistant `custom_components` directory
2. Restart Home Assistant

## Configuration

1. Go to Settings → Devices & Services → Add Integration
2. Search for "SeaQuaComp" and select it
3. Enter your device configuration:
   - **Host**: IP address or domain name of your device (e.g., `192.168.1.100` or `device.local`)
   - **PIN**: Your 4-digit authentication PIN

## API Endpoints

The integration expects your device to expose the following REST API endpoints:

- `GET /api/status` - Device status check
- `GET /api/sensors` - Sensor data retrieval

### Expected API Response Format

The `/api/sensors` endpoint should return JSON data in the following format:

```json
{
  "temperature": 23.5,
  "humidity": 65.0,
  "status": "ok"
}
```

## Sensors

The integration creates the following sensors:

- **Temperature Sensor**: Device temperature in Celsius
- **Humidity Sensor**: Relative humidity percentage
- **Status Sensor**: Online/offline status with additional attributes

## Development

To modify this integration for your specific API:

1. Update the API endpoints in `const.py`
2. Modify the data fetching logic in `coordinator.py`
3. Adjust sensor parsing in `sensor.py` to match your API response format
4. Add additional sensors by creating new sensor classes in `sensor.py`

## Authentication

The integration uses Bearer token authentication with your PIN:

```
Authorization: Bearer {your_4_digit_pin}
```

Make sure your device API supports this authentication method.

## Troubleshooting

- Check Home Assistant logs for connection errors
- Verify your device is accessible from Home Assistant
- Ensure the PIN is exactly 4 digits
- Confirm your device API endpoints are responding correctly

## License

This project is licensed under the MIT License.
