"""Module defining a drum decorator."""
import numpy as np

from alibrary.recoater.drums.interface import DrumInterface
from alibrary.motions.abstract.command import MotionCommand
from alibrary.motions.abstract.motor import Motor

class DrumDecorator(DrumInterface):
    """The base decorator class for a drum."""
    _drum: DrumInterface = None

    def __init__(self, drum: DrumInterface) -> None:
        self._drum = drum

    @property
    def drum(self) -> DrumInterface:
        """The drum decorated by this class."""
        return self._drum

    @property
    def geometry(self) -> np.ndarray:
        """Returns the geometry of this drum."""
        return self._drum.geometry

    @geometry.setter
    def geometry(self, geometry: np.ndarray) -> None:
        """Sets the geometry of this drum."""
        self._drum.geometry = geometry

    @property
    def theta_offset(self) -> float:
        """Returns the theta offset of this drum."""
        return self._drum.theta_offset

    @theta_offset.setter
    def theta_offset(self, offset: float) -> None:
        """Sets the theta offset of this drum."""
        self._drum.theta_offset = offset

    @property
    def powder_offset(self) -> float:
        """Returns the powder offset of this drum."""
        return self._drum.powder_offset

    @powder_offset.setter
    def powder_offset(self, offset: float) -> None:
        """Sets the powder offset of this drum."""
        self._drum.powder_offset = offset

    @property
    def motor(self) -> Motor:
        """Returns a JSON representation of this drum config.

        Returns:
            A JSON object describing the drum config
        """
        return self._drum.motor

    def get_info(self) -> dict[str,]:
        """Returns information about this drum.

        It gets the information of the motor and append drum specific info.

        Returns:
            A JSON object describing this drum

        Raises:
            InternalServerError: An error occurs in the process
        """
        return self._drum.get_info()

    @property
    def config(self) -> dict[str,]:
        """Returns a JSON representation of this drum config.

        Returns:
            A JSON object describing the drum config
        """
        return self._drum.config

    @config.setter
    def config(self, config: dict[str,]) -> None:
        """Sets configuration variables of this drum.

        Args:
            A JSON abject with the configuration variables
        """
        self._drum.config = config

    @property
    def ejection(self) -> dict[str,]:
        """Returns the current, target and max values of this drum ejection.

        Returns:
            A JSON object describing the different ejection values

        Raises:
            InternalServerError: An error occurs in the process
        """
        return self._drum.ejection

    @ejection.setter
    def ejection(self, pressure: dict[str,]) -> None:
        """Sets the requested ejection pressure.

        Args:
            A JSON object describing the target ejection pressure

        Raises:
            InternalServerError: An error occurs in the process
            BadRequestError: The request pressure is invalid
        """
        self._drum.ejection = pressure

    @property
    def suction(self) -> dict[str,]:
        """Returns the current, target and max values of this drum suction.

        Returns:
            A JSON object describing the different suction values

        Raises:
            InternalServerError: An error occurs in the process
        """
        return self._drum.suction

    @suction.setter
    def suction(self, pressure: dict[str,]) -> None:
        """Sets the requested suction pressure.

        Args:
            A JSON object describing the target suction pressure

        Raises:
            InternalServerError: An error occurs in the process
            BadRequestError: The request pressure is invalid
        """
        self._drum.suction = pressure

    def get_motion_command(self) -> dict[str,]:
        """Returns the current motion command or None if there is no current
        command.

        Returns:
            A JSON object representing the current command or None
        """
        return self._drum.get_motion_command()

    def start_motion(self, command: MotionCommand):
        """Starts a motion following the given motion command.

        Raises:
            InternalServerError: An error occurs in the process
            BadRequestError: The given command is not valid
            ConflictError: The motor is busy with another motion
        """
        self._drum.start_motion(command)

    def stop_motion(self):
        """Stops any running motion on this motor.

        Raises:
            InternalServerError: An error occurs in the process
        """
        self._drum.stop_motion()

    def get_geometry(self) -> bytes:
        """Returns a PNG image with the current geometry of this drum.

        Returns:
            A bytes object representing the PNG image;
        """
        return self._drum.get_geometry()

    def set_geometry_png(self, png: bytes) -> None:
        """Defines the geometry of this drum based on the given PNG image.

        Args:
            png: A bytes object representing the PNG image
        """
        self._drum.set_geometry_png(png)

    def set_geometry_cli(self, cli_file: bytes) -> None:
        """Defines the geometry of this drum based on the given CLI file.

        Args:
            cli_file: A bytes object representing the CLI file
        """
        self._drum.set_geometry_cli(cli_file)
