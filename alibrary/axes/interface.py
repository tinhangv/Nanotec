"""Module defining an abstract axis interface.
"""
from abc import ABC
from alibrary.motions.abstract.command import MotionCommand
from alibrary.motions.abstract.motor import Motor

class AxisInterface(ABC):
    """Generic interface of an axis."""
    motor: Motor

    def get_info(self) -> dict[str,]:
        """Returns infos about this axis.

        Returns:
            A JSON representation of the axis infos.
        """
        return self.motor.get_info()

    def get_command(self) -> dict[str,]:
        """Returns the infos of this axis motor.

        Returns:
            A JSON representation of the motor infos.
        """
        return self.motor.get_command()

    def start_motion(self, command: MotionCommand) -> None:
        """Starts a motion on this axis.

        Args:
            command: A MotionCommand object that will be send to this axis
            motor.
        """
        self.motor.start(command)

    def stop_motion(self) -> None:
        """Stops any currently running motion on this axis motor."""
        self.motor.stop()
