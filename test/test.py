"""Test file for Oxygen CS. Responsible for testing 
different temperature scenarios and actions taken by the system."""

import os

from unittest.mock import MagicMock
from dotenv import load_dotenv

load_dotenv()

from src.main import App


## To Implement
# Mocker les données reçues par le serveur
# Test: Actions prises par le système en fonction de la température


def test_take_action_too_hot():
    """Test the take_action method when the temperature is too hot."""
    app = App()
    app.t_max = os.getenv("T_MAX")

    # We mock the send_action_to_hvac method
    app.send_action_to_hvac = MagicMock()

    # Test: Température supérieure à t_max
    app.take_action(int(app.t_max) + 1)
    app.send_action_to_hvac.assert_called_with("TurnOnAc")


def test_take_action_too_cold():
    """Test the take_action method when the temperature is too cold."""
    app = App()
    app.t_min = os.getenv("T_MIN")

    # We mock the send_action_to_hvac method
    app.send_action_to_hvac = MagicMock()

    # Test: Température inférieure à t_min
    app.take_action(int(app.t_min) - 1)
    app.send_action_to_hvac.assert_called_with("TurnOnHeater")
