"""Module defining the hood valve.
"""
import time

from alibrary.electronics.pcb import PssPCB, PssPCBError
from alibrary.logger import logger
from alibrary.pneumatic.valve import PneumaticValve
from alibrary.server import InternalServerError


class HoodValve(PneumaticValve):
    """A valve controlled by a custom PCB"""

    def __init__(
        self,
        sensor_index: int,
        stepper_index: int,
        p_range: tuple[int, int],
        pcb: PssPCB,
    ) -> None:
        super().__init__(control_index=None,
                         sensor_index=sensor_index,
                         stepper_index=stepper_index,
                         p_range=p_range,
                         pcb=pcb,
                         plc=None)

        self.perform_homing()
        self.position = 0

    def set_initial_position(self, initial_position: int):
        """Waits for the valve to be homed before setting the initial position.

        Args:
            initial_position: The initial position of the valve
        """
        while not self.is_homing_done():
            time.sleep(0.1)
        logger.debug("Homing of the hood valve done")

        try:
            self.pcb.perform_distance_motion(self.stepper_index,
                                             initial_position)
            self.position = initial_position
        except PssPCBError as error:
            logger.error(str(error))
            raise InternalServerError(str(error)) from error

    def set_position(self, json: dict[str,]):
        """
        Sets position in microsteps
        """
        try:
            position = json["position"] if "position" in json else 0
            self.pcb.perform_distance_motion(self.stepper_index, position)
            self.position = position
        except PssPCBError as error:
            logger.error(str(error))
            raise InternalServerError(str(error)) from error

    def get_position(self) -> dict[str,]:
        """
        Returns the position
        """
        return {
            "position": self.position
        }
