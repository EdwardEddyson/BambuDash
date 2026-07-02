# backend/app/services/mqtt_service.py
import json
import paho.mqtt.client as mqtt
import time
import threading
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import SessionLocal
from app.crud import crud_filament

class MQTTClient:
    """Handles the connection and message processing for the MQTT broker."""
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
            print(f"Failed to connect, return code {rc}")

    def on_message(self, client, userdata, msg):
        """
        Handles incoming MQTT messages. This is a core part of the auto-discovery.
        It parses Bambu Lab AMS data, and then creates or updates a filament spool.
        """
        try:
            payload_str = msg.payload.decode()
            print(f"Received `{payload_str}` from `{msg.topic}` topic")
            data = json.loads(payload_str)

            # This is a simplified data structure based on what Bambu printers might send.
            # We are interested in the AMS data.
            ams_data = data.get("print", {}).get("ams", {})
            if not ams_data:
                return # Not a message we are interested in

            # A single message can contain updates for multiple trays
            trays = ams_data.get("ams", [])
            db: Session = SessionLocal()
            try:
                for tray in trays:
                    tray_id = tray.get("id") # This is the tray's UID, e.g., "00"
                    if not tray_id:
                        continue
                    
                    # In a real scenario, you'd map the filament `type` (e.g., "PLA") and `sub` brands
                    # to get the correct material_type and color_hex.
                    mqtt_data = {
                        "tray_id": tray_id,
                        "material": tray.get("type", "unknown"),
                        "color": tray.get("color", "FFFFFFFF")[:6], # Taking the first 6 chars of the hex code
                        "weight": tray.get("remain", 0.0)
                    }
                    crud_filament.get_or_create_from_mqtt(db=db, mqtt_data=mqtt_data)
            finally:
                db.close()

        except json.JSONDecodeError:
            print(f"Error decoding JSON from topic {msg.topic}")
        except Exception as e:
            print(f"An error occurred in on_message: {e}")

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
