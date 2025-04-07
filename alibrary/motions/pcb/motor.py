"""Modules defining a differential screw stepper motor class.

This is an implementation of the abstract Motor for a PssPCB stepper.

To handle the different kind of motors that we might use in the machines, an
abstract class is used. This allows to have a template and to benefit from OOP
advantages for the motors and motions.
"""
import os
import pickle
from dataclasses import dataclass

from alibrary.electronics.pcb import PssPCB
from alibrary.motions.abstract.motor import Motor
from alibrary.motions.pcb.command import MotionType, PCBScrewMotionCommand
from alibrary.server import ConflictError


@dataclass
class PCBScrewConfig:
    """Dataclass with the configuration parameters of a scraping blade screw
    stepper.

    Attributes:
        steps_per_rev: The number of steps per revolution of the stepper
        microsteps_per_step: The number of microsteps per step of the stepper
        micron_per_rev: The number of micron traveled by revolution
        min_abs_distance: The minimum absolute distance of the stepper range
        max_abs_distance: The maximum absolute distance of the stepper range
    """
    steps_per_rev: int
    microsteps_per_step: int
    micron_per_rev: int
    min_abs_distance: float = 0.0
    max_abs_distance: float = 0.0


class PCBScrewMotor(Motor):
    """Implementation of the Motor class for a stepper connected to the PssPCB.
    """

    def __init__(self, index: int, pcb: PssPCB, config: PCBScrewConfig) -> None:
        self.index = index
        self.config = config
        self.pcb = pcb
        self.position = 0
        self.file_name = f"./logs/screw_stepper_{index}_position"

        self.__load_position()

    def __save_position(self):
        """Saves the current position into a json object in a file.

        If the file doesn't exist, it will be created
        """
        if not os.path.exists("./logs"):
            os.makedirs("./logs")
        with open(self.file_name, "wb") as f:
            steppers_position = {}
            steppers_position[self.index] = self.position
            pickle.dump(steppers_position, f)

    def __load_position(self):
        """Loads the current position from a json object in a file.
        """
        if self.pcb.offline:
            self.position = 300
            return

        if os.path.exists(self.file_name):
            with open(self.file_name, "rb") as f:
                steppers_position = pickle.load(f)
                self.position = steppers_position[self.index]

                raw_position = int(self.position * self.config.steps_per_rev *
                                   self.config.microsteps_per_step /
                                   self.config.micron_per_rev)

                self.pcb.set_actual_position(self.index, raw_position)

    def is_busy(self) -> bool:
        """Checks if this screw is busy.

        Returns:
            A bool indicating if it is busy or not

        Raises:
            PssPCBError: An error occurs in th communication with the PCB
        """
        return (self.pcb.check_busy() >> self.index) % 2 == 1
        # return (self.pcb.check_busy() >> self.index) % 2 != 1

    def get_position(self) -> float:
        """Returns the current position of the screw.

        Returns:
            A float indicating the current position

        Raises:
            PssPCBError: An error occurs in th communication with the PCB
        """
        # FIXME: Do I keep this ? Should it be used by the server ?
        # raw_position = self.pcb.get_actual_position(self.index)
        # position = -int(
        #     raw_position / self.config.steps_per_rev /
        #     self.config.microsteps_per_step * self.config.micron_per_rev)
        # logger.warning("Stepper %s: actual target position %s", self.index,
        #                position)
        # self.pcb.check_driver_communication()
        return self.position

    def __is_homing_done(self) -> bool:
        """Checks if the homing of this screw has been done.

        Returns:
            A bool indicating if the homing is done or not

        Raises:
            PssPCBError: An error occurs in th communication with the PCB
        """
        return (self.pcb.check_homing_done() >> self.index) % 2 == 1

    def __perform_homing(self):
        """Performs the homing procedure on this screw.

        Raises:
            PssPCBError: An error occurs in th communication with the PCB
        """
        self.pcb.perform_homing(self.index)

        self.position = 0
        self.__save_position()

    def __perform_distance_motion(self, distance: float):
        """Performs an absolute distance motion on this screw.

        Args:
            distance: The absolute distance to traveled

        Raises:
            PssPCBError: An error occurs in th communication with the PCB
        """
        raw_distance = int(distance * self.config.steps_per_rev *
                           self.config.microsteps_per_step /
                           self.config.micron_per_rev)

        self.pcb.perform_distance_motion(self.index, raw_distance)

        self.position = distance
        self.__save_position()

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

        if not self.__is_homing_done(
        ) and command.motion_type != MotionType.HOMING:
            raise ConflictError("Perform the homing before moving the blade")

        self.validate_command(command, self.config.min_abs_distance,
                              self.config.max_abs_distance)

        self.current_command = command
        if command.motion_type == MotionType.HOMING:
            self.__perform_homing()
        elif command.motion_type == MotionType.ABSOLUTE:
            self.__perform_distance_motion(command.distance)
        else:  #if command.motion_type == PCBScrewMotionType.RELATIVE:
            crt_position = self.get_position()
            self.__perform_distance_motion(command.distance + crt_position)

    def stop(self):
        """Deletes the registered current command."""
        self.current_command = None
