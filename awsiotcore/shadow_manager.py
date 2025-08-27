import json
import time
from config import *

class ShadowManager:
    def __init__(self, mqtt_client, valve_controller):
        self.mqtt_client = mqtt_client
        self.valve_controller = valve_controller
        self.shadow_state = {
            "state": {
                "reported": {
                    "valves": {f"valve_{i+1}": "OFF" for i in range(NUM_VALVES)},
                    "timestamp": 0
                },
                "desired": {
                    "valves": {f"valve_{i+1}": "OFF" for i in range(NUM_VALVES)}
                }
            }
        }
        
    def update_reported_state(self, valve_states):
        """Update reported state in device shadow"""
        self.shadow_state["state"]["reported"]["valves"] = valve_states
        self.shadow_state["state"]["reported"]["timestamp"] = time.time()
        
        shadow_update = {
            "state": {
                "reported": self.shadow_state["state"]["reported"]
            }
        }
        
        success = self.mqtt_client.publish(SHADOW_UPDATE_TOPIC, shadow_update)
        if success:
            print("Shadow reported state updated")
        return success
    
    def get_shadow_state(self):
        """Request current shadow state from AWS"""
        empty_message = {}
        success = self.mqtt_client.publish(SHADOW_GET_TOPIC, empty_message)
        if success:
            print("Requested shadow state")
        return success
    
    def handle_desired_state_change(self, desired_state):
        """Handle desired state changes from shadow"""
        if "valves" not in desired_state:
            return
            
        desired_valves = desired_state["valves"]
        current_valves = self.valve_controller.get_valve_states()
        
        # Check for changes
        changes_needed = False
        for valve_name, desired_value in desired_valves.items():
            if valve_name in current_valves:
                if current_valves[valve_name] != desired_value:
                    changes_needed = True
                    break
        
        if not changes_needed:
            print("No valve state changes needed")
            return
        
        # Apply changes
        print(f"Applying desired valve states: {desired_valves}")
        
        # Turn off all valves first
        for i in range(NUM_VALVES):
            self.valve_controller.set_valve(i, False)
        
        # Turn on the desired valve (only one can be ON)
        valve_turned_on = False
        for valve_name, desired_value in desired_valves.items():
            if desired_value == "ON" and not valve_turned_on:
                valve_number = int(valve_name.split('_')[1]) - 1  # valve_1 -> 0
                if 0 <= valve_number < NUM_VALVES:
                    self.valve_controller.set_valve(valve_number, True)
                    valve_turned_on = True
                    print(f"Turned ON {valve_name}")
        
        # Update reported state
        new_valve_states = self.valve_controller.get_valve_states()
        self.update_reported_state(new_valve_states)
    
    def process_shadow_message(self, topic, message):
        """Process shadow-related MQTT messages"""
        try:
            if topic == SHADOW_GET_ACCEPTED_TOPIC:
                if "state" in message and "desired" in message["state"]:
                    self.handle_desired_state_change(message["state"]["desired"])
                    
            elif topic == SHADOW_UPDATE_ACCEPTED_TOPIC:
                print("Shadow update accepted")
                
            elif topic == SHADOW_UPDATE_REJECTED_TOPIC:
                print(f"Shadow update rejected: {message}")
                
        except Exception as e:
            print(f"Error processing shadow message: {e}")
    
    def sync_with_shadow(self):
        """Sync current device state with shadow"""
        # Update reported state
        current_valves = self.valve_controller.get_valve_states()
        self.update_reported_state(current_valves)
        
        # Get desired state
        self.get_shadow_state()