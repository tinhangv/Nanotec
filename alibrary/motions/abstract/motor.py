"""Modules defining an abstract motor class.

This receives motion command and communicate with the underlying PLC.

To handle the different kind of motors that we might use in the machines, an
abstract class is used. This allows to have a template and to benefit from OOP
advantages for the motors and motions.
"""
import math
from abc import ABC, abstractmethod

from alibrary.motions.abstract.command import MotionCommand, MotionType
from alibrary.server import BadRequestError, ConflictError


class Motor(ABC):
    """Abstract class representing an motor.

    This class should represent every kind of motors that could be used in the
    machine. It takes MotionCommand to update its parameters and communicate
    with the underlying hardware.
    """
    current_command: MotionCommand | None = None

    @abstractmethod
    def is_busy(self) -> bool:
        """Checks if this motor is busy, i.e. if there is a running motion.

        Raises:
            InternalServerError: An error occurs in the process
        """

    @abstractmethod
    def get_position(self) -> float:
        """Returns the current position

        Returns:
            A float representing the current position

        Raises:
            InternalServerError: An error occurs in the process
        """

    def validate_command(self, command: MotionCommand, min_abs_distance: float,
                         max_abs_distance: float):
        """Checks if the command is valid regarding to the motor current state
        and parameters.

        Raises:
            BadRequestError: The given command is not valid
            InternalServerError: An error occurs in the process
        """
        # Distance must be in the good range
        if command.motion_type == MotionType.RELATIVE:
            crt_position = self.get_position()
            min_distance = min_abs_distance - crt_position
            max_distance = max_abs_distance - crt_position
        elif command.motion_type == MotionType.ABSOLUTE:
            min_distance = min_abs_distance
            max_distance = max_abs_distance
        else:
            min_distance = -math.inf
            max_distance = math.inf

        if not min_distance <= command.distance <= max_distance:
            raise BadRequestError("Wrong distance value, must be between "
                                  f"{min_distance} and {max_distance} mm")

    @abstractmethod
    def start(self, command: MotionCommand):
        """Starts a motion following the given motion command.

        Raises:
            InternalServerError: An error occurs in the process
            BadRequestError: The given command is not valid
            ConflictError: The motor is busy with another motion
        """
        # If there is already a motion running
        if self.is_busy():
            raise ConflictError("There is already a motion running. Stop it "
                                "before starting a new one.")

    @abstractmethod
    def stop(self):
        """Stops any running motion on this motor.

        Raises:
            InternalServerError: An error occurs in the process
        """

    def get_info(self) -> dict[str,]:
        """Returns information about this motor and its current motion.

        This returns a JSON object describing the different information.

        Raises:
            InternalServerError: An error occurs in the process
        """
        is_running = self.is_busy()
        position = self.get_position()

        return {
            "running": is_running,
            "position": position,
        }

    def get_command(self) -> dict[str,]:
        """Returns the current motion command or None if there is no current
        command.

        Returns:
            A JSON object representing the current command or None
        """
        if self.current_command:
            return self.current_command.to_json()
        return None
