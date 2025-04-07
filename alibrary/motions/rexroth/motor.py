"""Modules defining a differential screw stepper motor class.

This is an implementation of the abstract Motor for a PssPCB stepper.

To handle the different kind of motors that we might use in the machines, an
abstract class is used. This allows to have a template and to benefit from OOP
advantages for the motors and motions.
"""
from alibrary.electronics.rexroth import RexrothDotNetDriver
from alibrary.motions.abstract.motor import Motor
from alibrary.motions.pcb.command import MotionType, PCBScrewMotionCommand


class RexrothMotor(Motor):
    """Implementation of the Motor class for a stepper connected to the PssPCB.
    """

    def __init__(
        self,
        driver: RexrothDotNetDriver,
        min_abs_distance: float = 0.0,
        max_abs_distance: float = 0.0,
    ) -> None:
        self.driver = driver
        self.min_abs_distance = min_abs_distance
        self.max_abs_distance = max_abs_distance

    def is_busy(self) -> bool:
        """Checks if this motor is busy.

        Returns:
            A bool indicating if it is busy or not

        Raises:
            RexrothError: An error occurs with the Rexroth driver
        """
        return self.driver.check_busy()

    def get_position(self) -> float:
        """Returns the current position of the motor.

        Returns:
            A float indicating the current position

        Raises:
            RexrothError: An error occurs with the Rexroth driver
        """
        return self.driver.get_position()

    def start(self, command: PCBScrewMotionCommand):
        """Starts a motion following the given motion command.

        It will first call the parent method to check if there is no motion
        currently running. Then it checks if the homing of the screw was done
        and if the command is valid before starting the motion.

        Raises:
            InternalServerError: An error occurs in the process
            BadRequestError: The given command is not valid
            ConflictError: The motor is busy with another motion
        """
        super().start(command)

        self.validate_command(command, self.min_abs_distance,
                              self.max_abs_distance)

        self.current_command = command
        if command.motion_type == MotionType.ABSOLUTE:
            self.driver.perform_absolute_motion(command.distance, command.speed)
        elif command.motion_type == MotionType.RELATIVE:
            self.driver.perform_relative_motion(command.distance, command.speed)

    def stop(self):
        """Deletes the registered current command."""
        self.current_command = None
