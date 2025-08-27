# Pico 2W Irrigation Controller

A MicroPython-based irrigation system that controls up to 8 valves using a Raspberry Pi Pico 2W, with AWS IoT Core integration for remote monitoring and control.

## Features

- Controls up to 8 irrigation valves (only one can be ON at a time)
- AWS IoT Core integration with Device Shadow support
- WiFi connectivity with automatic reconnection
- NTP time synchronization every 3 hours
- Real-time valve control via AWS IoT Shadow
- Automatic status reporting and heartbeat messages
- Emergency stop functionality
- Status LED indication

## Hardware Requirements

- Raspberry Pi Pico 2W
- 8x Relay modules (for valve control)
- 8x Solenoid valves
- Power supply suitable for your valves
- Breadboard or PCB for connections

## Pin Configuration

Default GPIO pins for valves (configurable in `config.py`):
- Valve 1: GPIO 2
- Valve 2: GPIO 3
- Valve 3: GPIO 4
- Valve 4: GPIO 5
- Valve 5: GPIO 6
- Valve 6: GPIO 7
- Valve 7: GPIO 8
- Valve 8: GPIO 9

## Setup Instructions

### 1. AWS IoT Core Setup

1. Create a new Thing in AWS IoT Core
2. Generate device certificates and keys
3. Download the certificates and note your IoT endpoint

### 2. Certificate Installation

Replace the placeholder content in these files with your actual certificates:

- `certs/device-certificate.pem.crt` - Your device certificate
- `certs/device-private.pem.key` - Your device private key
- `certs/amazon-root-ca-1.pem` - Amazon Root CA certificate

### 3. Configuration

Edit `config.py` and update:

```python
# WiFi Configuration
WIFI_SSID = "your_wifi_network"
WIFI_PASSWORD = "your_wifi_password"

# AWS IoT Core Configuration
AWS_IOT_ENDPOINT = "your-endpoint.iot.region.amazonaws.com"
DEVICE_ID = "your-unique-device-id"
```

### 4. Installation

1. Install MicroPython on your Pico 2W
2. Copy all Python files to the Pico's filesystem
3. Ensure the `certs/` directory structure is maintained

### 5. Required MicroPython Libraries

Make sure these libraries are available:
- `umqtt.simple` - MQTT client
- `ntptime` - NTP time synchronization
- Standard libraries: `machine`, `network`, `ssl`, `json`, `time`, `gc`

## Usage

### Running the System

1. Power on the Pico 2W
2. The system will automatically:
   - Connect to WiFi
   - Sync time with NTP server
   - Connect to AWS IoT Core
   - Begin monitoring for shadow updates

### Controlling Valves

Send desired state updates to the AWS IoT Device Shadow:

```json
{
  "state": {
    "desired": {
      "valves": {
        "valve_1": "ON",
        "valve_2": "OFF",
        "valve_3": "OFF",
        "valve_4": "OFF",
        "valve_5": "OFF",
        "valve_6": "OFF",
        "valve_7": "OFF",
        "valve_8": "OFF"
      }
    }
  }
}
```

**Important**: Only one valve can be "ON" at a time. If multiple valves are set to "ON", only the first one will be activated.

### Monitoring Status

The device reports its status through the shadow's reported state:

```json
{
  "state": {
    "reported": {
      "valves": {
        "valve_1": "ON",
        "valve_2": "OFF",
        ...
      },
      "timestamp": 1234567890
    }
  }
}
```

## File Structure

```
pico-irrigation/
├── main.py                 # Main application entry point
├── config.py               # Configuration settings
├── wifi_manager.py         # WiFi connection management
├── mqtt_client.py          # AWS IoT Core MQTT client
├── shadow_manager.py       # AWS IoT Shadow integration
├── valve_controller.py     # Valve control logic
├── time_sync.py            # NTP time synchronization
├── certs/                  # Certificate directory
│   ├── device-certificate.pem.crt
│   ├── device-private.pem.key
│   └── amazon-root-ca-1.pem
└── README.md
```

## Troubleshooting

### Common Issues

1. **WiFi Connection Failed**
   - Verify SSID and password in `config.py`
   - Check WiFi signal strength
   - Ensure 2.4GHz network (Pico W doesn't support 5GHz)

2. **MQTT Connection Failed**
   - Verify AWS IoT endpoint is correct
   - Check certificate files are properly formatted
   - Ensure device is registered in AWS IoT Core
   - Verify security policies allow connection

3. **Time Sync Issues**
   - Check internet connectivity
   - Verify NTP server accessibility
   - Ensure firewall allows NTP traffic (port 123)

4. **Valve Not Responding**
   - Check GPIO pin connections
   - Verify relay module power supply
   - Test valve manually
   - Check pin configuration in `config.py`

### Status LED Indicators

- **OFF**: System starting up or error condition
- **ON**: System running normally
- **Blinking**: Connection issues (WiFi or MQTT)

### Emergency Stop

The system includes an emergency stop feature that turns off all valves:
- Automatically triggered on system errors
- Can be called programmatically via `valve_controller.emergency_stop()`

## Safety Considerations

- Always test the system thoroughly before deploying
- Implement appropriate fail-safes for your specific irrigation setup
- Consider adding moisture sensors to prevent overwatering
- Ensure proper electrical isolation between control circuits and valve power
- Regular monitoring and maintenance recommended

## License

This project is provided as-is for educational and personal use.