import machine
import time
from config import VALVE_PINS, NUM_VALVES

class ValveController:
    def __init__(self):
        self.valves = []
        self.valve_states = {}
        self.active_valve = None
        
        # Initialize GPIO pins for valves
        for i, pin_num in enumerate(VALVE_PINS[:NUM_VALVES]):
            valve_pin = machine.Pin(pin_num, machine.Pin.OUT)
            valve_pin.value(0)  # Start with valve OFF
            self.valves.append(valve_pin)
            self.valve_states[f"valve_{i+1}"] = "OFF"
        
        print(f"Initialized {len(self.valves)} valves on pins: {VALVE_PINS[:NUM_VALVES]}")
    
    def set_valve(self, valve_index, state):
        """Set valve state (True=ON, False=OFF)"""
        if not 0 <= valve_index < len(self.valves):
            print(f"Invalid valve index: {valve_index}")
            return False
        
        valve_name = f"valve_{valve_index + 1}"
        
        if state:  # Turn valve ON
            # First turn off all other valves (only one can be ON)
            self._turn_off_all_valves()
            
            # Turn on the requested valve
            self.valves[valve_index].value(1)
            self.valve_states[valve_name] = "ON"
            self.active_valve = valve_index
            print(f"Valve {valve_index + 1} turned ON")
            
        else:  # Turn valve OFF
            self.valves[valve_index].value(0)
            self.valve_states[valve_name] = "OFF"
            if self.active_valve == valve_index:
                self.active_valve = None
            print(f"Valve {valve_index + 1} turned OFF")
        
        return True
    
    def _turn_off_all_valves(self):
        """Turn off all valves"""
        for i, valve in enumerate(self.valves):
            valve.value(0)
            self.valve_states[f"valve_{i+1}"] = "OFF"
        self.active_valve = None
    
    def turn_off_all_valves(self):
        """Public method to turn off all valves"""
        self._turn_off_all_valves()
        print("All valves turned OFF")
    
    def get_valve_states(self):
        """Get current state of all valves"""
        return self.valve_states.copy()
    
    def get_active_valve(self):
        """Get currently active valve (if any)"""
        return self.active_valve
    
    def set_valve_by_name(self, valve_name, state):
        """Set valve state by name (valve_1, valve_2, etc.)"""
        try:
            valve_number = int(valve_name.split('_')[1]) - 1
            return self.set_valve(valve_number, state == "ON")
        except (IndexError, ValueError):
            print(f"Invalid valve name: {valve_name}")
            return False
    
    def emergency_stop(self):
        """Emergency stop - turn off all valves immediately"""
        print("EMERGENCY STOP - Turning off all valves")
        self._turn_off_all_valves()
    
    def test_valves(self, test_duration_seconds=2):
        """Test each valve sequentially"""
        print("Starting valve test...")
        
        for i in range(len(self.valves)):
            print(f"Testing valve {i+1}")
            self.set_valve(i, True)
            time.sleep(test_duration_seconds)
            self.set_valve(i, False)
            time.sleep(0.5)
        
        print("Valve test completed")
    
    def get_status(self):
        """Get detailed status of valve controller"""
        return {
            'total_valves': len(self.valves),
            'valve_states': self.valve_states,
            'active_valve': self.active_valve,
            'pins': VALVE_PINS[:NUM_VALVES]
        }