import ssl
import time
from umqtt.simple import MQTTClient
from config import *
import json

class AWSIoTClient:
    def __init__(self):
        self.client = None
        self.connected = False
        
    def read_file(self, path):
        """Read certificate/key files"""
        try:
            with open(path, 'r') as f:
                return f.read()
        except Exception as e:
            print(f"Error reading {path}: {e}")
            return None
    
    def connect(self):
        """Connect to AWS IoT Core with SSL/TLS"""
        try:
            # Read certificates
            device_cert = self.read_file(DEVICE_CERT_PATH)
            device_key = self.read_file(DEVICE_KEY_PATH)
            root_ca = self.read_file(ROOT_CA_PATH)
            
            if not all([device_cert, device_key, root_ca]):
                print("Missing certificate files")
                return False
            
            # Create SSL context
            context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
            context.check_hostname = False
            context.verify_mode = ssl.CERT_REQUIRED
            
            # Load certificates
            context.load_cert_chain(DEVICE_CERT_PATH, DEVICE_KEY_PATH)
            context.load_verify_locations(ROOT_CA_PATH)
            
            # Create MQTT client
            self.client = MQTTClient(
                client_id=DEVICE_ID,
                server=AWS_IOT_ENDPOINT,
                port=AWS_IOT_PORT,
                ssl=context,
                keepalive=60
            )
            
            self.client.set_callback(self._message_callback)
            self.client.connect()
            self.connected = True
            print(f"Connected to AWS IoT Core: {AWS_IOT_ENDPOINT}")
            
            # Subscribe to shadow topics
            self.client.subscribe(SHADOW_UPDATE_ACCEPTED_TOPIC)
            self.client.subscribe(SHADOW_UPDATE_REJECTED_TOPIC)
            self.client.subscribe(SHADOW_GET_ACCEPTED_TOPIC)
            
            return True
            
        except Exception as e:
            print(f"MQTT connection error: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from AWS IoT Core"""
        if self.client and self.connected:
            try:
                self.client.disconnect()
                self.connected = False
                print("Disconnected from AWS IoT Core")
            except Exception as e:
                print(f"Disconnect error: {e}")
    
    def publish(self, topic, message):
        """Publish message to topic"""
        if not self.connected:
            print("Not connected to MQTT broker")
            return False
            
        try:
            if isinstance(message, dict):
                message = json.dumps(message)
            self.client.publish(topic, message)
            return True
        except Exception as e:
            print(f"Publish error: {e}")
            return False
    
    def check_messages(self):
        """Check for incoming messages"""
        if self.client and self.connected:
            try:
                self.client.check_msg()
            except Exception as e:
                print(f"Message check error: {e}")
                self.connected = False
    
    def _message_callback(self, topic, msg):
        """Handle incoming MQTT messages"""
        try:
            topic_str = topic.decode('utf-8')
            message = json.loads(msg.decode('utf-8'))
            print(f"Received message on {topic_str}: {message}")
            
            # Handle shadow responses
            if topic_str == SHADOW_UPDATE_ACCEPTED_TOPIC:
                self._handle_shadow_update_accepted(message)
            elif topic_str == SHADOW_UPDATE_REJECTED_TOPIC:
                self._handle_shadow_update_rejected(message)
            elif topic_str == SHADOW_GET_ACCEPTED_TOPIC:
                self._handle_shadow_get_accepted(message)
                
        except Exception as e:
            print(f"Message callback error: {e}")
    
    def _handle_shadow_update_accepted(self, message):
        """Handle shadow update accepted"""
        print("Shadow update accepted")
    
    def _handle_shadow_update_rejected(self, message):
        """Handle shadow update rejected"""
        print(f"Shadow update rejected: {message}")
    
    def _handle_shadow_get_accepted(self, message):
        """Handle shadow get accepted"""
        print("Shadow get accepted")
        # This will be handled by the shadow manager
    
    def is_connected(self):
        """Check if connected to MQTT broker"""
        return self.connected