"""Module defining a pneumatic valve.

This kind of valve is used in the recoater to control the pressure in the drums
and in the leveler.
"""
from alibrary.electronics.controllino import (ControllinoError, Controllino)
from alibrary.electronics.pcb import PssPCB, PssPCBError
from alibrary.logger import logger
from alibrary.server import InternalServerError


class PneumaticValve:
    """A pneumatic valve controlled by a custom PCB.
    """

    N_MAX = 16384

    def __init__(self, control_index: int, sensor_index: int,
                 stepper_index: int, p_range: tuple[int, int], pcb: PssPCB,
                 plc: Controllino) -> None:
        self.control_index = control_index
        self.sensor_index = sensor_index
        self.stepper_index = stepper_index
        self.p_min = p_range[0]
        self.p_max = p_range[1]
        self.pcb = pcb
        self.plc = plc

    def __compute_pressure(self, data: int) -> float:
        """Converts a raw pressure measure in a correct pressure value.

        Args:
            data: The raw pressure measure

        Returns:
            A float representing the pressure value
        """
        return ((self.p_max - self.p_min) * (data - 0.1 * self.N_MAX) /
                (0.8 * self.N_MAX) + self.p_min)

    def __compute_data(self, pressure: float) -> int:
        """Converts a pressure value in a raw pressure setpoint.

        Args:
            data: The pressure value

        Returns:
            An int representing the raw pressure setpoint
        """
        return int((pressure - self.p_min) / (self.p_max - self.p_min) *
                   (0.8 * self.N_MAX) + 0.1 * self.N_MAX)

    def get_pressure(self) -> float:
        """Returns the current pressure measured at the valve.

        Returns:
            A float representing the measured pressure

        Raises:
            InternalServerError: An error occurs in th communication with the
            PCB
        """
        try:
            return self.__compute_pressure(
                self.pcb.get_raw_pressures()[self.sensor_index])
        except PssPCBError as error:
            logger.error(str(error))
            raise InternalServerError(str(error)) from error

    def set_pressure(self, pressure: float):
        """Sets the pressure that the valve should regulate.

        Args:
            pressure: The pressure that the valve must impose

        Raises:
            InternalServerError: An error occurs in th communication with the
            PCB
        """
        try:
            if pressure != 0:
                self.plc.activate_cyclone(self.control_index)
                self.activate_regulation(pressure)
            else:
                self.deactivate_regulation()
                self.plc.deactivate_cyclone(self.control_index)
                self.perform_homing()
        except PssPCBError as error:
            logger.error(str(error))
            raise InternalServerError(str(error)) from error
        except ControllinoError as error:
            logger.error(str(error))
            raise InternalServerError(str(error)) from error

    def activate_regulation(self, pressure):
        """Activates the pressure regulation of this valve."""
        self.pcb.start_pressure_control(self.control_index,
                                        self.__compute_data(pressure))

    def deactivate_regulation(self):
        """Deactivates the pressure regulation of this valve."""
        self.pcb.stop_pressure_control(self.control_index)

    def perform_homing(self):
        """Performs the homing procedure on this valve.

        Raises:
            InternalServerError: An error occurs in th communication with the
            PCB
        """
        try:
            self.pcb.perform_homing(self.stepper_index)
        except PssPCBError as error:
            logger.error(str(error))
            raise InternalServerError(str(error)) from error

    def is_homing_done(self) -> bool:
        """Checks if the homing of this valve has been done.

        Returns:
            A bool indicating if the homing is done or not

        Raises:
            InternalServerError: An error occurs in th communication with the
            PCB
        """
        try:
            return (self.pcb.check_homing_done() >> self.stepper_index) % 2 == 1
        except PssPCBError as error:
            logger.error(str(error))
            raise InternalServerError(str(error)) from error
