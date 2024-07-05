"""Test file for Oxygen CS. Responsible for testing 
different temperature scenarios and actions taken by the system."""

from unittest.mock import MagicMock
from dotenv import load_dotenv

load_dotenv()
from src.main import App


def test_received_temperature_format():
    """Test the format of the first received temperature."""
    app = App()
    # Wait for the first temperature to be received from the on_sensor_data_received callback function
    app.on_sensor_data_received = MagicMock()
    app.start()
    assert app.on_sensor_data_received.call_count == 1
    # Assert that the timestamp is in the correct format
    # assert app.on_sensor_data_received.call_args[0]["date"] is not None


# def test_received_action():
#     """Test the received action from the HVAC."""
#     app = App()
#
