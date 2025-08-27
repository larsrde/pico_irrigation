import network
import time
from config import WIFI_SSID, WIFI_PASSWORD

class WiFiManager:
    def __init__(self):
        self.wlan = network.WLAN(network.STA_IF)
        
    def connect(self, timeout=30):
        """Connect to WiFi network"""
        if self.wlan.isconnected():
            print("Already connected to WiFi")
            return True
            
        self.wlan.active(True)
        self.wlan.connect(WIFI_SSID, WIFI_PASSWORD)
        
        print(f"Connecting to {WIFI_SSID}...")
        start_time = time.time()
        
        while not self.wlan.isconnected():
            if time.time() - start_time > timeout:
                print("WiFi connection timeout")
                return False
            time.sleep(0.5)
            
        print(f"Connected to WiFi: {self.wlan.ifconfig()}")
        return True
    
    def disconnect(self):
        """Disconnect from WiFi"""
        if self.wlan.isconnected():
            self.wlan.disconnect()
            print("Disconnected from WiFi")
    
    def is_connected(self):
        """Check if connected to WiFi"""
        return self.wlan.isconnected()
    
    def get_status(self):
        """Get WiFi connection status"""
        return {
            'connected': self.wlan.isconnected(),
            'ip': self.wlan.ifconfig()[0] if self.wlan.isconnected() else None,
            'ssid': WIFI_SSID
        }