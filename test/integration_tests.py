"""Test file for Oxygen CS. Responsible for testing 
different temperature scenarios and actions taken by the system."""

import datetime
from dotenv import load_dotenv

load_dotenv()
from .mock_responses.sensor_mock_reponse import mock_response


def test_received_timestamp_format():
    """Test the received timestamp format from HVAC."""
    timestamp = mock_response["timestamp"]
    try:
        datetime.datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%f%z")
    except ValueError:
        assert False


def test_received_temperature_format():
    """Test the received timestamp format from HVAC."""
    temperature = mock_response["temperature"]
    try:
        # Verify that the temperature is a float with 2 decimal places
        assert isinstance(temperature, float)
        assert round(temperature, 2) == temperature
    except ValueError:
        assert False


def test_received_action():
    """Test the received action from the HVAC."""
    action = mock_response["action"]
    assert action in {"TurnOnAc", "TurnOnHeater"}
