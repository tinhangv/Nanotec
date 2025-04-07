"""Module defining the shovels of a recoater"""
from enum import Enum
from alibrary.electronics import Controllino
from alibrary.logger import logger


class ShovelState(Enum):
    """Types of motion"""
    DISABLED = 0
    OPEN = 1
    CLOSE = 2


class Shovels:
    """Interface to control the shovels of the recoater"""

    def __init__(self, plc: Controllino) -> None:
        self.plc = plc

    def get_state(self) -> dict[str,]:
        """Returns the state of the shovels

        Returns:
            A JSON object describing the state of the shovels

        Raises:
            InternalServerError: An error occurs in the process
        """
        state = ShovelState(self.plc.get_shovels_state())

        return {
            "state": state.name.lower(),
        }

    def set_state(self, json: dict[str,]) -> None:
        """Sets the state of the shovels

        Args:
            A JSON object describing the state of the shovels

        Raises:
            InternalServerError: An error occurs in the process
        """
        if "state" in json:
            state = ShovelState[str(json["state"]).upper(
            )] if "state" in json else ShovelState.DISABLED

            self.plc.set_shovels_state(state.value)
            logger.debug("shovels set to %s", state)
