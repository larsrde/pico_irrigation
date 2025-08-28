# Configuration file for Pico Irrigation System

# WiFi Configuration
WIFI_SSID = "YOUR_WIFI_SSID"
WIFI_PASSWORD = "YOUR_WIFI_PASSWORD"

# AWS IoT Core Configuration
AWS_IOT_ENDPOINT = "your-endpoint.iot.region.amazonaws.com"
AWS_IOT_PORT = 8883
DEVICE_ID = "iot_device_id"

# Certificate file paths
DEVICE_CERT_PATH = "/certs/device-certificate.pem.crt"
DEVICE_KEY_PATH = "/certs/device-private.pem.key"
ROOT_CA_PATH = "/certs/amazon-root-ca-1.pem"

# MQTT Topics
SHADOW_UPDATE_TOPIC = f"$aws/things/{DEVICE_ID}/shadow/update"
SHADOW_GET_TOPIC = f"$aws/things/{DEVICE_ID}/shadow/get"
SHADOW_UPDATE_ACCEPTED_TOPIC = f"$aws/things/{DEVICE_ID}/shadow/update/accepted"
SHADOW_UPDATE_REJECTED_TOPIC = f"$aws/things/{DEVICE_ID}/shadow/update/rejected"
SHADOW_GET_ACCEPTED_TOPIC = f"$aws/things/{DEVICE_ID}/shadow/get/accepted"

# Hardware Configuration
VALVE_PINS = [2, 3, 4, 5, 6, 7, 8, 9]  # GPIO pins for 8 valves
NUM_VALVES = 8

# Time sync configuration
NTP_SERVER = "pool.ntp.org"
TIME_SYNC_INTERVAL_HOURS = 3