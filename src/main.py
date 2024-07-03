"""Main App file for Oxygen CS. Responsible for handling sensor data events,
 taking actions based on the temperature, and saving the sensor data into the database."""

import os
import time
from datetime import datetime
import logging
import json

import requests
from sqlalchemy.sql import text
from signalrcore.hub_connection_builder import HubConnectionBuilder

from config import SessionLocal, engine, Base


# pylint: disable=too-many-instance-attributes
# Eight is reasonable in this case.
class App:
    """Main class for the Oxygen CS application"""

    def __init__(self):
        self._hub_connection = None
        self.ticks = 10

        # To be configured by your team
        self.host = os.getenv("HOST")
        self.token = os.getenv("TOKEN")
        self.t_max = os.getenv("T_MAX")
        self.t_min = os.getenv("T_MIN")
        self.database_url = os.getenv("DATABASE_URL")

        # Initialize a single session for database operations
        self.db_session = SessionLocal()

    def __del__(self):
        if self._hub_connection is not None:
            self._hub_connection.stop()
        # Close the connection to the database
        self.db_session.close()

    def start(self):
        """Start Oxygen CS."""
        self.setup_sensor_hub()
        self._hub_connection.start()
        print("Press CTRL+C to exit.")

        Base.metadata.create_all(bind=engine)

        while True:
            time.sleep(2)

    def setup_sensor_hub(self):
        """Configure hub connection and subscribe to sensor data events."""
        self._hub_connection = (
            HubConnectionBuilder()
            .with_url(f"{self.host}/SensorHub?token={self.token}")
            .configure_logging(logging.INFO)
            .with_automatic_reconnect(
                {
                    "type": "raw",
                    "keep_alive_interval": 10,
                    "reconnect_interval": 5,
                    "max_attempts": 999,
                }
            )
            .build()
        )
        self._hub_connection.on("ReceiveSensorData", self.on_sensor_data_received)
        self._hub_connection.on_open(lambda: print("||| Connection opened."))
        self._hub_connection.on_close(lambda: print("||| Connection closed."))
        self._hub_connection.on_error(lambda data: print(f"||| Exception thrown: {data.error}"))

    def on_sensor_data_received(self, data):
        """Callback method to handle sensor data on reception."""
        try:
            print(data[0]["date"] + " --> " + data[0]["data"], flush=True)
            timestamp = data[0]["date"]
            temperature = float(data[0]["data"])
            self.take_action(temperature)
            self.save_event_to_database(timestamp, temperature)
        # except the most common types of exceptions (but not using the generic Exception class)
        except (KeyError, TypeError, ValueError) as e:
            print(e)

    def take_action(self, temperature):
        """Take action to HVAC depending on current temperature."""
        if float(temperature) >= float(self.t_max):
            self.send_action_to_hvac("TurnOnAc")
        elif float(temperature) <= float(self.t_min):
            self.send_action_to_hvac("TurnOnHeater")

    def send_action_to_hvac(self, action):
        """Send action query to the HVAC service."""
        r = requests.get(f"{self.host}/api/hvac/{self.token}/{action}/{self.ticks}", timeout=10)
        details = json.loads(r.text)
        print(details, flush=True)

    def save_event_to_database(self, timestamp, temperature):
        """Save sensor data into database."""
        try:
            timestamp = datetime.utcnow()

            action = "None"
            if float(temperature) >= float(self.t_max):
                action = "TurnOnAc"
            elif float(temperature) <= float(self.t_min):
                action = "TurnOnHeater"

            # Utilisation de text pour encapsuler la requête SQL brute
            query = text(
                """
                INSERT INTO temperatures (timestamp, temperature, action)
                VALUES (:timestamp, :temperature, :action)
            """
            )

            self.db_session.execute(
                query,
                {
                    "timestamp": timestamp,
                    # Not sure about this cast
                    "temperature": float(temperature),
                    "action": action,
                },
            )
            self.db_session.commit()

        except requests.exceptions.RequestException as e:
            # To implement
            print(e)


if __name__ == "__main__":
    app = App()
    app.start()
