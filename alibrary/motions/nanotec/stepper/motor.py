"""Defines a class that controls a stepper motor connected to a NanotecDriver.

This class implements the NanotecDriver class. Thus it is a subclass of both
ModbusComponent and Motor. It has to define the Motor methods and can use the
ones in ModbusComponent to do so.
"""
import time
from dataclasses import dataclass

from alibrary.electronics.modbus import ModbusError
from alibrary.logger import logger
from alibrary.motions.nanotec.stepper.command import (
    MotionType, NanotecStepperMotionCommand)
from alibrary.motions.nanotec.driver import NanotecDriver
from alibrary.motions.nanotec.state import NanotecDriverState
from alibrary.server import BadRequestError, InternalServerError, ConflictError


@dataclass
class NanotecStepperConfig:
    """Configuration variables of a Nanotec stepper motor.

    Attributes:
        max_speed: The maximum speed allowed by the motor
        min_abs_distance: The minimum absolute distance that the motor can reach
        max_abs_distance: The maximum absolute distance that the motor can reach
    """
    max_speed: float = 0.0
    min_abs_distance: float = 0.0
    max_abs_distance: float = 0.0


class NanotecStepper(NanotecDriver):
    """Implementation of the NanotecDriver class for a driver connected to a
    stepper motor.
    """

    # Address of the information out register
    READ_INFORMATION_ADDRESS = 2014
    # Address of the information in register
    WRITE_INFORMATION_ADDRESS = 3014

    # Address of the current position register
    ACTUAL_POSITION_ADDRESS = 2008
    # Address of the current speed register
    ACTUAL_SPEED_ADDRESS = 2010

    # Address of the speed register when searching the zero
    SEARCH_ZERO_SPEED_ADDRESS = 3016
    # Speed when searching the zero [µm/s]
    SEARCH_ZERO_SPEED = 3000

    # Address of the target position register
    TARGET_POSITION_ADDRESS = 3006
    # Address of the target speed register
    TARGET_SPEED_ADDRESS = 3008
    # Address of the target acceleration register
    TARGET_ACCELERATION_ADDRESS = 3010
    # Address of the target deceleration register
    TARGET_DECELERATION_ADDRESS = 3012

    # Homing speed [µm/s]
    HOMING_SPEED = 15000
    # Homing acceleration [µm/s²]
    HOMING_ACCELERATION = 50000

    # Default acceleration [µm/s²]
    DEFAULT_ACCELERATION = 250000
    # Default deceleration [µm/s²]
    DEFAULT_DECELERATION = 250000
    # Default deceleration when stopping the motion [µm/s²]
    DEFAULT_STOP_DECELERATION = 1000000

    # Drum seam sensor address
    SENSOR_ADDRESS = 2012
    # Sensor threshold
    SENSOR_THRESHOLD = 600

    def __init__(
        self,
        config: NanotecStepperConfig,
        ip: str,
        port: int = 502,
        timeout: int = 2,
        offline: bool = False,
    ) -> None:
        super().__init__(ip, port, timeout, offline)

        self.config = config

    def is_busy(self) -> bool:
        """Returns the running status of the motor.

        Returns:
            True if a motion is running on the motor, false otherwise

        Raises:
            InternalServerError: An error occurs in the process
        """
        try:
            info_word = self.read_registers(self.READ_INFORMATION_ADDRESS)
            return info_word % 2 == 1
        except ModbusError as error:
            logger.error(str(error))
            raise InternalServerError(str(error)) from error

    def is_homed(self) -> bool:
        """Returns the running status of the motor.

        Returns:
            True if a motion is running on the motor, false otherwise

        Raises:
            InternalServerError: An error occurs in the process
        """
        try:
            info_word = self.read_registers(self.READ_INFORMATION_ADDRESS)
            return (info_word / 2) % 2 == 1
        except ModbusError as error:
            logger.error(str(error))
            raise InternalServerError(str(error)) from error

    def get_position(self) -> float:
        """Gets the current position of the Nanotec driver.

        Returns:
            A float representing the position in mm

        Raises:
            InternalServerError: An error occurs in the process
        """
        try:
            position = self.read_registers(self.ACTUAL_POSITION_ADDRESS)
            return position / 1000
        except ModbusError as error:
            logger.error(str(error))
            raise InternalServerError(str(error)) from error

    def get_speed(self) -> float:
        """Gets the current speed of the Nanotec driver.

        Returns:
            A float representing the speed in mm/s

        Raises:
            InternalServerError: An error occurs in the process
        """
        try:
            speed = self.read_registers(self.ACTUAL_SPEED_ADDRESS)
            return speed / 1000
        except ModbusError as error:
            logger.error(str(error))
            raise InternalServerError(str(error)) from error

    def validate_command(self, command: NanotecStepperMotionCommand,
                         min_abs_distance: float, max_abs_distance: float):
        """Checks if the command is valid regarding to the motor current state
        and parameters.

        In addition of its parent class validation, it also checks if the given
        speed is valid

        Raises:
            BadRequestError: The given command is not valid
            InternalServerError: An error occurs in the process
        """
        # Speed must be in ]0; max_speed]
        if command.speed <= 0 or command.speed > self.config.max_speed:
            raise BadRequestError("Wrong speed value, must be below "
                                  f"{self.config.max_speed} mm/s")

        super().validate_command(command, min_abs_distance, max_abs_distance)

    def __perform_homing(self):
        """Runs a homing motion.

        Raises:
            InternalServerError: An error occurs in the process
        """
        try:
            self.write_registers(self.SEARCH_ZERO_SPEED_ADDRESS,
                                 self.SEARCH_ZERO_SPEED)
            self.write_registers(self.TARGET_SPEED_ADDRESS, self.HOMING_SPEED)
            self.write_registers(self.TARGET_ACCELERATION_ADDRESS,
                                 self.HOMING_ACCELERATION)
        except ModbusError as error:
            logger.error(str(error))
            raise InternalServerError(str(error)) from error

        # Starts homing motion
        self._set_operation_mode(6)
        self._set_control_word(0xF)
        self._set_control_word(0x1F)

    def __perform_speed_motion(self,
                               speed: float,
                               acceleration: float = DEFAULT_ACCELERATION):
        """Runs a speed motion.

        Args:
            speed: The speed of the motion in mm/s

        Raises:
            InternalServerError: An error occurs in the process
        """
        # Writes homing parameters
        try:
            self.write_registers(self.TARGET_SPEED_ADDRESS, int(speed * 1000))
            self.write_registers(self.TARGET_ACCELERATION_ADDRESS, acceleration)
        except ModbusError as error:
            logger.error(str(error))
            raise InternalServerError(str(error)) from error

        # Starts homing motion
        self._set_operation_mode(3)
        self._set_control_word(0x0F)

    def __perform_position_motion(self,
                                  distance: float,
                                  speed: float,
                                  is_relative: bool = True):
        """Runs a position motion, this can be absolute or relative motion.

        Args:
            distance: The absolute or relative distance to travel in mm
            speed: The speed of the motion in mm/s
            is_relative: A boolean indicating if the motion is relative

        Raises:
            InternalServerError: An error occurs in the process
        """
        # Writes homing parameters
        try:
            self.write_registers(self.TARGET_POSITION_ADDRESS,
                                 int(distance * 1000))
            self.write_registers(self.TARGET_SPEED_ADDRESS, int(speed * 1000))
            self.write_registers(self.TARGET_ACCELERATION_ADDRESS,
                                 self.DEFAULT_ACCELERATION)
            self.write_registers(self.TARGET_DECELERATION_ADDRESS,
                                 self.DEFAULT_DECELERATION)
        except ModbusError as error:
            logger.error(str(error))
            raise InternalServerError(str(error)) from error

        # Starts homing motion
        self._set_operation_mode(1)
        self._set_control_word(0xF)

        oms = 0b111 if is_relative else 0b011
        control_word = oms * 16 + 0xF
        self._set_control_word(control_word)

        # Waits for set-point to be validated
        while not self._check_bit_of_status_word(12):
            time.sleep(0.1)

        # Resets control word
        control_word -= 16
        self._set_control_word(control_word)

    def start(self, command: NanotecStepperMotionCommand):
        """Starts a motion following the given motion command.

        It will first call the parent method to check if there is no motion
        currently running. Then it checks if the command is valid before
        starting the motion.

        Raises:
            InternalServerError: An error occurs in the process
            BadRequestError: The given command is not valid
            ConflictError: The motor is busy with another motion
        """
        super().start(command)

        # Validates motion command
        self.validate_command(command, self.config.min_abs_distance,
                              self.config.max_abs_distance)

        if not self.is_homed() and command.motion_type != MotionType.HOMING:
            raise ConflictError("Homing not donee")

        # Check if the driver is in the right state
        state = self._get_state()
        if state not in (NanotecDriverState.SWITCHED_ON,
                         NanotecDriverState.OPERATION_ENABLED):
            logger.error("Impossible to perform Nanotec motion from state %s",
                         state)
            raise InternalServerError(
                f"Impossible to perform Nanotec motion from state {state}")

        self.current_command = command

        # Calls the correct procedure
        if command.motion_type == MotionType.HOMING:
            self.__perform_homing()
        elif command.motion_type == MotionType.SPEED:
            self.__perform_speed_motion(command.speed)
        else:
            is_relative = command.motion_type == MotionType.RELATIVE
            self.__perform_position_motion(command.distance, command.speed,
                                           is_relative)

    def stop(self):
        """Stops any running motion on this motor.

        It also delete the registered current command.

        Raises:
            InternalServerError: An error occurs in the process
        """
        # try:
        #     # Trigger HALT mode
        #     self._set_control_word(0x10F)

        #     # Wait for speed to reach 0
        #     while self.get_speed() != 0:
        #         time.sleep(0.1)

        #     # Erase target position
        #     self.write_registers(self.TARGET_POSITION_ADDRESS, 0)
        #     self._set_control_word(0x17F)

        #     # Waits for set-point to be validated
        #     while not self._check_bit_of_status_word(12):
        #         time.sleep(0.1)

        #     self._set_control_word(0xF)
        # except ModbusError as error:
        #     logger.error(str(error))
        #     raise InternalServerError(str(error)) from error

        # self.__perform_position_motion(10, self.HOMING_SPEED, True)

        if self.current_command is not None:
            self._set_control_word(0x10F)

            while self.get_speed() != 0:
                time.sleep(0.1)

            self.__perform_position_motion(0, 0, True)

            self.current_command = None
