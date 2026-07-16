# backend/app/services/mqtt_service.py
import json
import ssl
from datetime import datetime
import paho.mqtt.client as mqtt
import time
import threading
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import SessionLocal
from app.crud import crud_filament
from app.models.base_models import Printer, PrintJob, PrintProject, ProjectStatus, FilamentSpool

class MQTTClient:
    """Handles the connection and message processing for the MQTT broker."""
    def __init__(self, host: str, port: int, username: str = "", password: str = "", is_cloud: bool = False):
        self.client = mqtt.Client()
        if username and password:
            self.client.username_pw_set(username, password)

        self.host = host
        self.port = port
        self.is_cloud = is_cloud
        self.active_jobs_tracking = {}
        self.active_trays = {}

        # Configure SSL/TLS
        if port == 8883:
            if is_cloud:
                # Cloud broker uses standard certificates signed by a public CA
                self.client.tls_set()
            else:
                # Local printer broker uses self-signed certificates
                self.client.tls_set(cert_reqs=ssl.CERT_NONE)
                self.client.tls_insecure_set(True)

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

            print_data = data.get("print", {})
            if not print_data:
                return

            # Extract printer serial number from topic (device/+/report)
            parts = msg.topic.split('/')
            serial_number = parts[1] if len(parts) > 1 else "unknown"

            db: Session = SessionLocal()
            try:
                # 1. Parse AMS tray messages if present
                ams_data = print_data.get("ams", {})
                if ams_data:
                    ams_list = ams_data.get("ams", [])
                    current_tray_ids = set()

                    for ams_unit in ams_list:
                        ams_id = ams_unit.get("id", "0")
                        trays = ams_unit.get("tray", [])
                        for tray in trays:
                            slot_id = tray.get("id")  # slot index, e.g., "0", "1", "2", "3"
                            if slot_id is None:
                                continue

                            is_empty = False
                            if "tray_type" in tray and tray["tray_type"] == "":
                                is_empty = True
                            elif not tray.get("tray_type") and not tray.get("tray_color"):
                                is_empty = True
                            elif tray.get("empty") is True:
                                is_empty = True

                            # Use tray_uuid if valid/RFID spool, else fallback to composite key
                            tray_uuid = tray.get("tray_uuid")
                            if not tray_uuid or tray_uuid == "0000000000000000" or len(tray_uuid) < 4:
                                tray_uuid = f"{serial_number}_ams{ams_id}_slot{slot_id}"

                            if is_empty:
                                fallback_id = f"{serial_number}_ams{ams_id}_slot{slot_id}"
                                fallback_spool = db.query(FilamentSpool).filter(FilamentSpool.bambu_tray_id == fallback_id).first()
                                if fallback_spool:
                                    fallback_spool.bambu_tray_id = None
                                    db.add(fallback_spool)
                                continue

                            current_tray_ids.add(tray_uuid)

                            # Color format is "RRGGBBAA" hex code
                            color_rgba = tray.get("tray_color", "FFFFFFFF")
                            color_hex = f"#{color_rgba[:6]}"

                            material = tray.get("tray_type", "PLA")

                            # Remain is percentage (0-100). Default to 0 if negative.
                            remain_pct = tray.get("remain", 0.0)
                            if remain_pct < 0:
                                remain_pct = 0.0
                            weight_g = remain_pct * 10.0  # Convert to grams (100% = 1000g)

                            mqtt_data = {
                                "tray_id": tray_uuid,
                                "material": material,
                                "color": color_hex,
                                "weight": weight_g
                            }
                            crud_filament.get_or_create_from_mqtt(db=db, mqtt_data=mqtt_data)

                    if serial_number in self.active_trays:
                        removed_tray_ids = self.active_trays[serial_number] - current_tray_ids
                        for r_tray_id in removed_tray_ids:
                            spool = db.query(FilamentSpool).filter(FilamentSpool.bambu_tray_id == r_tray_id).first()
                            if spool:
                                spool.bambu_tray_id = None
                                db.add(spool)
                    
                    self.active_trays[serial_number] = current_tray_ids

                # 2. Print status updates (gcode_state)
                gcode_state = print_data.get("gcode_state")
                if gcode_state:
                    # Look up printer in DB
                    db_printer = db.query(Printer).filter(Printer.connection_info == serial_number).first()
                    if db_printer:
                        # Find active print job (end_time is None)
                        active_job = db.query(PrintJob).filter(
                            PrintJob.printer_id == db_printer.id,
                            PrintJob.end_time == None
                        ).first()

                        if active_job:
                            project = active_job.project
                            spool = active_job.filament_spool_used
                            tracking_key = f"job_{active_job.id}"

                            # Initialize tracking if not already tracked
                            if tracking_key not in self.active_jobs_tracking:
                                self.active_jobs_tracking[tracking_key] = spool.remaining_weight_g

                            if gcode_state == "RUNNING":
                                if project and project.status != ProjectStatus.PRINTING:
                                    project.status = ProjectStatus.PRINTING
                                    db.add(project)

                            elif gcode_state in ["FINISH", "FAILED", "CANCELLED"]:
                                # Close the print job
                                active_job.end_time = datetime.utcnow()

                                start_weight = self.active_jobs_tracking.pop(tracking_key, spool.remaining_weight_g)
                                # Spool weight should have been updated by AMS loop above or in previous packets
                                current_weight = spool.remaining_weight_g
                                consumption = max(0.0, start_weight - current_weight)
                                active_job.actual_consumption_g = consumption

                                # Update project status
                                if project:
                                    if gcode_state == "FINISH":
                                        project.status = ProjectStatus.COMPLETED
                                    else:
                                        project.status = ProjectStatus.PLANNED
                                    db.add(project)

                                db.add(active_job)

                            db.commit()

            finally:
                db.close()

        except json.JSONDecodeError:
            print(f"Error decoding JSON from topic {msg.topic}")
        except Exception as e:
            print(f"An error occurred in on_message: {e}")

    def run(self):
        """
        Connects to the broker and starts the client loop in a separate background thread.
        """
        broker_type = "Cloud" if self.is_cloud else "Local"
        print(f"Starting {broker_type} MQTT client (connecting to {self.host}:{self.port})...")
        try:
            self.client.connect(self.host, self.port, 60)
            self.client.loop_start()
            print(f"{broker_type} MQTT client loop started successfully.")
        except Exception as e:
            print(f"Error starting {broker_type} MQTT client: {e}")

    def stop(self):
        """
        Stops the MQTT client loop and disconnects from the broker.
        """
        broker_type = "Cloud" if self.is_cloud else "Local"
        print(f"Stopping {broker_type} MQTT client...")
        try:
            self.client.loop_stop()
            self.client.disconnect()
            print(f"{broker_type} MQTT client stopped and disconnected.")
        except Exception as e:
            print(f"Error stopping {broker_type} MQTT client: {e}")

# Instantiate the clients
local_mqtt_client = MQTTClient(
    host=settings.MQTT_BROKER_HOST,
    port=settings.MQTT_BROKER_PORT,
    username=settings.MQTT_USERNAME,
    password=settings.MQTT_PASSWORD,
    is_cloud=False
)

cloud_mqtt_client = None
if settings.BAMBU_CLOUD_USERNAME and settings.BAMBU_CLOUD_PASSWORD:
    cloud_mqtt_client = MQTTClient(
        host=settings.BAMBU_CLOUD_HOST,
        port=settings.BAMBU_CLOUD_PORT,
        username=settings.BAMBU_CLOUD_USERNAME,
        password=settings.BAMBU_CLOUD_PASSWORD,
        is_cloud=True
    )

# Wrapper class to maintain backward compatibility with main.py calls
class MQTTServiceManager:
    def run(self):
        local_mqtt_client.run()
        if cloud_mqtt_client:
            cloud_mqtt_client.run()

    def stop(self):
        local_mqtt_client.stop()
        if cloud_mqtt_client:
            cloud_mqtt_client.stop()

mqtt_client = MQTTServiceManager()
