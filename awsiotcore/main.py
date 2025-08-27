"""
Pico 2W Irrigation Controller
Main program for controlling irrigation valves via AWS IoT Core
"""

import time
import gc
from machine import Pin, reset
import sys

# Import our modules
from wifi_manager import WiFiManager
from mqtt_client import AWSIoTClient
from valve_controller import ValveController
from shadow_manager import ShadowManager
from time_sync import TimeSync
from config import DEVICE_ID

class IrrigationController:
    def __init__(self):
        self.wifi = WiFiManager()
        self.mqtt_client = AWSIoTClient()
        self.valve_controller = ValveController()
        self.time_sync = TimeSync()
        self.shadow_manager = None
        self.running = True
        self.last_heartbeat = 0
        self.heartbeat_interval = 60  # Send heartbeat every 60 seconds
        
        # Setup onboard LED for status indication
        self.status_led = Pin("LED", Pin.OUT)
        self.status_led.value(0)
        
        print(f"Irrigation Controller initialized for device: {DEVICE_ID}")
    
    def setup(self):
        """Initialize all components"""
        print("=== Pico 2W Irrigation Controller Starting ===")
        
        # Connect to WiFi
        if not self.wifi.connect():
            print("Failed to connect to WiFi")
            return False
        
        # Initial time sync
        print("Performing initial time synchronization...")
        if not self.time_sync.sync_time():
            print("Warning: Initial time sync failed")
        
        # Connect to AWS IoT Core
        if not self.mqtt_client.connect():
            print("Failed to connect to AWS IoT Core")
            return False
        
        # Initialize shadow manager
        self.shadow_manager = ShadowManager(self.mqtt_client, self.valve_controller)
        
        # Setup MQTT message callback to include shadow processing
        original_callback = self.mqtt_client._message_callback
        
        def enhanced_callback(topic, msg):
            original_callback(topic, msg)
            # Also process shadow messages
            try:
                import json
                topic_str = topic.decode('utf-8')
                message = json.loads(msg.decode('utf-8'))
                self.shadow_manager.process_shadow_message(topic_str, message)
            except Exception as e:
                print(f"Error in enhanced callback: {e}")
        
        self.mqtt_client._message_callback = enhanced_callback
        
        # Sync initial state with shadow
        self.shadow_manager.sync_with_shadow()
        
        # Turn on status LED to indicate ready
        self.status_led.value(1)
        
        print("=== System Ready ===")
        return True
    
    def run(self):
        """Main program loop"""
        if not self.setup():
            print("Setup failed, restarting in 10 seconds...")
            time.sleep(10)
            reset()
            return
        
        print("Starting main loop...")
        
        while self.running:
            try:
                # Check WiFi connection
                if not self.wifi.is_connected():
                    print("WiFi disconnected, attempting reconnection...")
                    self.status_led.value(0)
                    if not self.wifi.connect():
                        print("WiFi reconnection failed")
                        time.sleep(5)
                        continue
                    self.status_led.value(1)
                
                # Check MQTT connection
                if not self.mqtt_client.is_connected():
                    print("MQTT disconnected, attempting reconnection...")
                    self.status_led.value(0)
                    if not self.mqtt_client.connect():
                        print("MQTT reconnection failed")
                        time.sleep(5)
                        continue
                    self.status_led.value(1)
                
                # Process MQTT messages
                self.mqtt_client.check_messages()
                
                # Auto-sync time if needed (every 3 hours)
                self.time_sync.auto_sync_if_needed()
                
                # Send periodic status/heartbeat
                current_time = time.time()
                if current_time - self.last_heartbeat >= self.heartbeat_interval:
                    self.send_heartbeat()
                    self.last_heartbeat = current_time
                
                # Small delay to prevent busy waiting
                time.sleep(0.1)
                
                # Periodic garbage collection
                if time.ticks_ms() % 10000 < 100:
                    gc.collect()
                
            except KeyboardInterrupt:
                print("Received keyboard interrupt")
                self.shutdown()
                break
            except Exception as e:
                print(f"Error in main loop: {e}")
                self.status_led.value(0)
                time.sleep(1)
                self.status_led.value(1)
    
    def send_heartbeat(self):
        """Send periodic heartbeat/status message"""
        try:
            status = {
                "device_id": DEVICE_ID,
                "timestamp": self.time_sync.get_timestamp(),
                "uptime_seconds": time.ticks_ms() // 1000,
                "wifi_status": self.wifi.get_status(),
                "valve_status": self.valve_controller.get_status(),
                "time_sync_status": self.time_sync.get_status(),
                "free_memory": gc.mem_free()
            }
            
            # Update reported state in shadow
            valve_states = self.valve_controller.get_valve_states()
            self.shadow_manager.update_reported_state(valve_states)
            
        except Exception as e:
            print(f"Error sending heartbeat: {e}")
    
    def shutdown(self):
        """Graceful shutdown"""
        print("Shutting down...")
        self.running = False
        
        # Turn off all valves
        self.valve_controller.emergency_stop()
        
        # Disconnect from services
        if self.mqtt_client:
            self.mqtt_client.disconnect()
        
        if self.wifi:
            self.wifi.disconnect()
        
        # Turn off status LED
        self.status_led.value(0)
        
        print("Shutdown complete")

def main():
    """Main entry point"""
    try:
        controller = IrrigationController()
        controller.run()
    except Exception as e:
        print(f"Fatal error: {e}")
        # Turn off all valves in case of error
        try:
            valve_controller = ValveController()
            valve_controller.emergency_stop()
        except:
            pass
        # Restart after delay
        print("Restarting in 10 seconds...")
        time.sleep(10)
        reset()

if __name__ == "__main__":
    main()