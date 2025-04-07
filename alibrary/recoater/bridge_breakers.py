"""Module defining the bridge breakers of a recoater"""
from alibrary.electronics import Controllino
from alibrary.logger import logger


class BridgeBreakers:
    """Interface to control the bridge breakers of the recoater"""

    def __init__(self, plc: Controllino) -> None:
        self.plc = plc

    def get_state(self) -> dict[str,]:
        """Returns the state of the bridge breakers

        Returns:
            A JSON object describing the state of the bridge breakers

        Raises:
            InternalServerError: An error occurs in the process
        """
        state = self.plc.get_bridge_breakers_state()

        return {"state": state}

    def set_state(self, json: dict[str,]) -> None:
        """Sets the state of the bridge breakers

        Args:
            A JSON object describing the state of the bridge breakers

        Raises:
            InternalServerError: An error occurs in the process
        """
        if "state" in json:
            new_state = json["state"]

            self.plc.set_bridge_breakers_state(new_state)
            logger.debug("Bridge breakers set to %s", new_state)
