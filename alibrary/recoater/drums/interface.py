"""Module defining a drum interface"""
from abc import ABC, abstractmethod
import numpy as np
from alibrary.electronics.controllino import Controllino
from alibrary.motions.abstract.command import MotionCommand
from alibrary.motions.abstract.motor import Motor
from alibrary.pneumatic.valve import PneumaticValve
from alibrary.recoater.drums.config import DrumConfig


class DrumInterface(ABC):
    """Abstract interface of a drum of an Aerosint recoater.
    """
    # def __init__(self) -> None:
    index: int = 0
    _valve: PneumaticValve = None
    _motor: Motor = None
    _controllino: Controllino = None
    _config: DrumConfig = DrumConfig()

    geometry: np.ndarray = None

    theta_offset: float = 0.0
    powder_offset: int = 0

    _target_suction_pressure = 0.0

    # @property
    # def index(self) -> int:
    #     """Returns this drum index"""

    @property
    def motor(self) -> Motor:
        """Returns this drum motor"""
        return self._motor

    # @property
    # def theta_offset(self) -> float:
    #     """Returns this drum theta offset"""

    # @property
    # def powder_offset(self) -> int:
    #     """Returns this drum theta offset"""

    @abstractmethod
    def get_info(self) -> dict[str,]:
        """Returns information about this drum.

        It gets the information of the motor and append drum specific info.

        Returns:
            A JSON object describing this drum

        Raises:
            InternalServerError: An error occurs in the process
        """

    @property
    @abstractmethod
    def config(self) -> dict[str,]:
        """Returns a JSON representation of this drum config.

        Returns:
            A JSON object describing the drum config
        """

    @config.setter
    @abstractmethod
    def config(self, config: dict[str,]) -> None:
        """Sets configuration variables of this drum.

        Args:
            A JSON abject with the configuration variables
        """

    @property
    @abstractmethod
    def ejection(self) -> dict[str,]:
        """Returns the current, target and max values of this drum ejection.

        Returns:
            A JSON object describing the different ejection values

        Raises:
            InternalServerError: An error occurs in the process
        """

    @ejection.setter
    @abstractmethod
    def ejection(self, pressure: dict[str,]) -> None:
        """Sets the requested ejection pressure.

        Args:
            A JSON object describing the target ejection pressure

        Raises:
            InternalServerError: An error occurs in the process
            BadRequestError: The request pressure is invalid
        """

    @property
    @abstractmethod
    def suction(self) -> dict[str,]:
        """Returns the current, target and max values of this drum suction.

        Returns:
            A JSON object describing the different suction values

        Raises:
            InternalServerError: An error occurs in the process
        """

    @suction.setter
    @abstractmethod
    def suction(self, pressure: dict[str,]) -> None:
        """Sets the requested suction pressure.

        Args:
            A JSON object describing the target suction pressure

        Raises:
            InternalServerError: An error occurs in the process
            BadRequestError: The request pressure is invalid
        """

    @abstractmethod
    def get_motion_command(self) -> dict[str,]:
        """Returns the current motion command or None if there is no current
        command.

        Returns:
            A JSON object representing the current command or None
        """

    @abstractmethod
    def start_motion(self, command: MotionCommand):
        """Starts a motion following the given motion command.

        Raises:
            InternalServerError: An error occurs in the process
            BadRequestError: The given command is not valid
            ConflictError: The motor is busy with another motion
        """

    @abstractmethod
    def stop_motion(self):
        """Stops any running motion on this motor.

        Raises:
            InternalServerError: An error occurs in the process
        """

    @abstractmethod
    def get_geometry(self) -> bytes:
        """Returns a PNG image with the current geometry of this drum.

        Returns:
            A bytes object representing the PNG image;
        """

    @abstractmethod
    def set_geometry_png(self, png: bytes) -> None:
        """Defines the geometry of this drum based on the given PNG image.

        Args:
            png: A bytes object representing the PNG image
        """

    @abstractmethod
    def set_geometry_cli(self, cli_file: bytes) -> None:
        """Defines the geometry of this drum based on the given CLI file.

        Args:
            cli_file: A bytes object representing the CLI file
        """
