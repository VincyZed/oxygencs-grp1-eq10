from signalrcore.hub_connection_builder import HubConnectionBuilder
import logging
import requests
import json
import time

import os
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import Session
import model
from config import SessionLocal, engine
from contextlib import contextmanager

from fastapi import Depends


class App:
    def __init__(self):
        self._hub_connection = None
        self.TICKS = 10

        # To be configured by your team
        self.HOST = os.getenv("HOST")
        self.TOKEN = os.getenv("TOKEN")
        self.T_MAX = os.getenv("T_MAX")
        self.T_MIN = os.getenv("T_MIN")
        self.DATABASE_URL = os.getenv("DATABASE_URL")

        # Initialize a single session for database operations
        self.db_session = SessionLocal()

    def __del__(self):
        if self._hub_connection != None:
            self._hub_connection.stop()
        # Close the connection to the database
        self.db_session.close()

    def start(self):
        """Start Oxygen CS."""
        self.setup_sensor_hub()
        self._hub_connection.start()
        print("Press CTRL+C to exit.")

        model.Base.metadata.create_all(bind=engine)

        while True:
            time.sleep(2)

    def setup_sensor_hub(self):
        """Configure hub connection and subscribe to sensor data events."""
        self._hub_connection = (
            HubConnectionBuilder()
            .with_url(f"{self.HOST}/SensorHub?token={self.TOKEN}")
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
        self._hub_connection.on_error(
            lambda data: print(f"||| An exception was thrown closed: {data.error}")
        )

    def on_sensor_data_received(self, data):
        """Callback method to handle sensor data on reception."""
        try:
            print(data[0]["date"] + " --> " + data[0]["data"], flush=True)
            timestamp = data[0]["date"]
            temperature = float(data[0]["data"])
            self.take_action(temperature)
            self.save_event_to_database(timestamp, temperature)
        except Exception as err:
            print(err)

    def take_action(self, temperature):
        """Take action to HVAC depending on current temperature."""
        if float(temperature) >= float(self.T_MAX):
            self.send_action_to_hvac("TurnOnAc")
        elif float(temperature) <= float(self.T_MIN):
            self.send_action_to_hvac("TurnOnHeater")

    def send_action_to_hvac(self, action):
        """Send action query to the HVAC service."""
        r = requests.get(f"{self.HOST}/api/hvac/{self.TOKEN}/{action}/{self.TICKS}")
        details = json.loads(r.text)
        print(details, flush=True)

    # ========================
    # Session de base de données
    # ========================
    # def get_db():
    #     db = SessionLocal()
    #     try:
    #         yield db
    #     finally:
    #         print("Closing database connection...")
    #         db.close()

    def save_event_to_database(self, timestamp, temperature):
        
        """Save sensor data into database."""
        try:
            timestamp = datetime.utcnow()
            
            action = "None"
            if float(temperature) >= float(self.T_MAX):
                action = "TurnOnAc"
            elif float(temperature) <= float(self.T_MIN):
                action = "TurnOnHeater"

            # Utilisation de text pour encapsuler la requête SQL brute
            query = text("""
                INSERT INTO temperatures (timestamp, temperature, action)
                VALUES (:timestamp, :temperature, :action)
            """)

            self.db_session.execute(
                query,
                {
                    "timestamp": timestamp,
                    # Not sure about this cast
                    "temperature": float(temperature),
                    "action": action,
                }
            )
            self.db_session.commit()

        except requests.exceptions.RequestException as e:
            # To implement
            print(e) 
            pass


if __name__ == "__main__":
    app = App()
    app.start()
