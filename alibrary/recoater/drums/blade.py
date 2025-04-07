"""Module describing a scraping blade screw"""
from dataclasses import dataclass

from alibrary.motions.pcb.command import PCBScrewMotionCommand
from alibrary.motions.pcb.motor import PCBScrewMotor


@dataclass
class Screw:
    """Differential screw of a scraping blade."""
    index: int
    motor: PCBScrewMotor

    def get_info(self):
        """Returns information about this screw.

        It gets the information of the motor and append screw specific info.

        Returns:
            A JSON object describing this screw

        Raises:
            InternalServerError: An error occurs in the process
        """
        # Get motor info
        info = self.motor.get_info()

        # Add screw info
        info["id"] = self.index

        return info

    def get_command(self) -> dict[str,]:
        """Returns the current motion command or None if there is no current
        command.

        Returns:
            A JSON object representing the current command or None
        """
        return self.motor.get_command()

    def start_motion(self, command: PCBScrewMotionCommand):
        """Starts a motion following the given motion command.

        Raises:
            InternalServerError: An error occurs in the process
            BadRequestError: The given command is not valid
            ConflictError: The motor is busy with another motion
        """
        self.motor.start(command)

    def stop_motion(self):
        """Stops any running motion on this motor.

        Raises:
            InternalServerError: An error occurs in the process
        """
        self.motor.stop()


class Blade(list[Screw]):
    """A scaping blade with two differential screws"""

    def get_info(self) -> list[dict[str,]]:
        """Returns the list of the drums info.

        Returns:
            A list of the drums'info

        Raises:
            InternalServerError: An error occurs in the process
        """
        return [screw.get_info() for screw in self]

    def start_motion(self, command: PCBScrewMotionCommand):
        """Starts a blade motion.

        This will executes the given command on this blade's both screws.

        Args:
            command: A PssPCBMotionCommand representing the motion to execute

        Raises:
            InternalServerError: An error occurs in the process
            BadRequestError: The given command is not valid
            MotorBusyError: The motor is busy with another motion
        """
        for screw in self:
            screw.motor.start(command)

    def stop_motion(self):
        """Stops a blade motion.

        This will stops any motion on this blade's both screws.

        Raises:
            InternalServerError: An error occurs in the process
        """
        for screw in self:
            screw.motor.stop()

    def get_motion_info(self):
        """Returns the current motion command of this blade.

        Raises:
            InternalServerError: An error occurs in the process
        """
        return self[0].motor.get_command()

    def is_above_threshold(self) -> bool:
        """Checks if both screws of this blade are above a given threshold
        """
        threshold = 100
        for screw in self:
            if screw.motor.get_position() < threshold:
                return False
        return True
