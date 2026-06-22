# backend/app/services/mqtt_service.py
import paho.mqtt.client as mqtt
import time
import threading
from app.core.config import settings

class MQTTClient:
    def __init__(self):
        self.client = mqtt.Client()
        self.client.username_pw_set(settings.MQTT_USERNAME, settings.MQTT_PASSWORD)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
            # Subscribe to the relevant Bambu Lab topics
            # This topic path is an example, you need to find the correct one for your printer
            client.subscribe("device/+/report")
        else:
            print(f"Failed to connect, return code {rc}
")

    def on_message(self, client, userdata, msg):
        """
        Handles incoming MQTT messages. This is a core part of the auto-discovery.
        """
        print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")
        # 1. Parse the JSON payload from the message
        # 2. Extract tray_id, material, color, weight etc.
        # 3. Get a DB session
        # 4. Call `crud_filament.get_by_tray_id()`
        # 5. If it exists, update weight.
        # 6. If it does not exist, call `crud_filament.create_from_mqtt()`
        pass # Implement the logic described above

    def run(self):
        """
        Connects to the broker and starts the client loop in a separate thread.
        """
        print("Starting MQTT client...")
        self.client.connect(settings.MQTT_BROKER_HOST, settings.MQTT_BROKER_PORT, 60)
        
        # Run the client loop in a non-blocking way
        thread = threading.Thread(target=self.client.loop_forever)
        thread.daemon = True
        thread.start()

mqtt_client = MQTTClient()
