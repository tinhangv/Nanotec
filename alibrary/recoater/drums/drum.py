"""Module describing a drum of an Aerosint recoater."""
import cv2
import numpy as np
import pycli
from pycli.models import CLI

from alibrary.electronics import ControllinoError, Controllino
from alibrary.logger import logger
from alibrary.motions.abstract.command import MotionCommand, MotionType
from alibrary.motions.abstract.motor import Motor
from alibrary.pneumatic.valve import PneumaticValve
from alibrary.server import BadRequestError, InternalServerError
from alibrary.recoater.drums.config import DrumConfig
from alibrary.recoater.drums.interface import DrumInterface


class Drum(DrumInterface):
    """Drum of an Aerosint recoater.

    Attributes:
        index: This drum index
        valve: The pneumatic valve responsible for the suction of the drum
        motor: The motor responsible for the theta motion of this drum
        controllino: The PLC responsible for the ejection pressure of this drum
        config: The configuration of this drum
        geometry: Tis drum powder geometry, stored as a deposition matrix
        theta_offset: The offset to apply along the theta axis of this drum
        powder_offset: The powder offset to apply on this drum geometry
        target_suction_pressure: The target suction pressure of this drum
    """

    def __init__(
            self,
            index: int,
            valve: PneumaticValve,
            motor: Motor,
            controllino: Controllino,
            config: DrumConfig = DrumConfig(),
    ) -> None:
        super().__init__()
        self._index: int = index
        self._valve: PneumaticValve = valve
        self._motor: Motor = motor
        self._controllino: Controllino = controllino
        self._config: DrumConfig = config

        self.geometry: np.ndarray = np.zeros(config.geometry_size, dtype=np.uint8)

        self.theta_offset: float = 0.0
        self.powder_offset: int = 0
        self._target_suction_pressure = 0.0

    @property
    def index(self) -> int:
        """Returns this drum motor"""
        return self._index

    @property
    def motor(self) -> Motor:
        """Returns this drum motor"""
        return self._motor


    def get_info(self) -> dict[str,]:
        """Returns information about this drum.

        It gets the information of the motor and append drum specific info.

        Returns:
            A JSON object describing this drum

        Raises:
            InternalServerError: An error occurs in the process
        """
        # Get motor info
        info = self._motor.get_info()

        # Add drum info
        info["circumference"] = self._config.circumference
        info["index"] = self.index

        return info

    @property
    def config(self) -> dict[str,]:
        """Returns a JSON representation of this drum config.

        Returns:
            A JSON object describing the drum config
        """
        config = {
            "theta_offset": self.theta_offset,
            "powder_offset": self.powder_offset
        }

        return config

    @config.setter
    def config(self, config: dict[str,]) -> None:
        """Sets configuration variables of this drum.

        Args:
            A JSON abject with the configuration variables
        """
        # Theta offset
        if "theta_offset" in config:
            self.theta_offset = config["theta_offset"]

        # Powder offset
        if "powder_offset" in config:
            self.powder_offset = config["powder_offset"]

    @property
    def ejection(self) -> dict[str,]:
        """Returns the current, target and max values of this drum ejection.

        Returns:
            A JSON object describing the different ejection values

        Raises:
            InternalServerError: An error occurs in the process
        """
        current = self._controllino.get_ejection(self.index)

        rescaled_value = (current -
                          51) / 204 * self._config.max_ejection_pressure

        values = {
            "maximum": self._config.max_ejection_pressure,
            "pressure": rescaled_value
        }

        return values

    @ejection.setter
    def ejection(self, pressure: dict[str,]) -> None:
        """Sets the requested ejection pressure.

        Args:
            A JSON object describing the target ejection pressure

        Raises:
            InternalServerError: An error occurs in the process
            BadRequestError: The request pressure is invalid
        """
        pressure = pressure["pressure"]
        # Validation
        if not 0 <= pressure <= self._config.max_ejection_pressure:
            raise BadRequestError(
                f"(drum) The ejection pressure of the drum {self.index + 1}"
                f" should be between 0 and {self._config.max_ejection_pressure}"
                f" but received {pressure}")

        # Application
        rescaled_value = (pressure * 204 / self._config.max_ejection_pressure +
                          51)

        try:
            self._controllino.set_ejection(self.index, rescaled_value)
        except ControllinoError as error:
            logger.error(str(error))
            raise InternalServerError(str(error)) from error

        logger.info("Drum %d ejection pressure set to %f", self.index, pressure)

    @property
    def suction(self) -> dict[str,]:
        """Returns the current, target and max values of this drum suction.

        Returns:
            A JSON object describing the different suction values

        Raises:
            InternalServerError: An error occurs in the process
        """
        current = self._valve.get_pressure()

        values = {
            "target": self._target_suction_pressure,
            "maximum": self._config.max_suction_pressure,
            "value": current
        }

        return values

    @suction.setter
    def suction(self, pressure: dict[str,]) -> None:
        """Sets the requested suction pressure.

        Args:
            A JSON object describing the target suction pressure

        Raises:
            InternalServerError: An error occurs in the process
            BadRequestError: The request pressure is invalid
        """
        pressure = pressure["target"]

        # Validation
        if not 0 <= pressure <= self._config.max_suction_pressure:
            raise BadRequestError("(drum) The suction target pressure of the "
                                  f"drum {self.index + 1} should be between 0 "
                                  f"and {self._config.max_suction_pressure} "
                                  f"but received {pressure}")

        # Application
        self._valve.set_pressure(pressure)
        self._target_suction_pressure = pressure
        logger.info("Drum %d suction target pressure set to %f", self.index,
                    pressure)

    def get_motion_command(self) -> dict[str,]:
        """Returns the current motion command or None if there is no current
        command.

        Returns:
            A JSON object representing the current command or None
        """
        return self._motor.get_command()

    def start_motion(self, command: MotionCommand):
        """Starts a motion following the given motion command.

        Raises:
            InternalServerError: An error occurs in the process
            BadRequestError: The given command is not valid
            ConflictError: The motor is busy with another motion
        """
        if command.motion_type == MotionType.TURNS:
            command.motion_type = MotionType.RELATIVE
            command.distance = command.turns * self._config.circumference
        if command.motion_type == MotionType.ABSOLUTE:
            crt_pos = self._motor.get_position()
            if command.distance < crt_pos:
                command.distance += self._config.circumference
        self._motor.start(command)

    def stop_motion(self):
        """Stops any running motion on this motor.

        Raises:
            InternalServerError: An error occurs in the process
        """
        self._motor.stop()

    def get_geometry(self) -> bytes:
        """Returns a PNG image with the current geometry of this drum.

        Returns:
            A bytes object representing the PNG image;
        """
        # Build BGR PNG image from the 2D binary matrix of this drum's geometry
        kernel = np.ones((3, 3), np.uint8)
        geo = cv2.dilate(self.geometry, kernel, iterations=self.powder_offset)
        image = 1 - np.tile(geo, (3, 1, 1))
        image *= 255
        image = np.moveaxis(image, 0, -1)

        # Converts numpy array into PNG bytes string
        png = cv2.imencode(".png", image)[1].tobytes()

        return png

    def set_geometry_png(self, png: bytes) -> None:
        """Defines the geometry of this drum based on the given PNG image.

        Args:
            png: A bytes object representing the PNG image
        """
        # Decode PNG into numpy array
        image: np.ndarray = cv2.imdecode(np.frombuffer(png, np.uint8), -1)

        # Convert partial transparency to either opaque or fully transparent
        if image.shape[2] == 4:
            image[:, :, 3] = np.floor(image[:, :, 3] / 255 + 0.5) * 255

        # List unique colors
        unique_colors = np.unique(image.reshape(-1, image.shape[2]), axis=0)

        # Remove transparent colors
        if unique_colors.shape[1] == 4:
            unique_colors = unique_colors[np.where(unique_colors[:, 3] != 0)]

        # Remove pure white
        unique_colors = unique_colors[np.any(unique_colors != 255, axis=1)]

        # Check the number of colors detected in the image
        if unique_colors.shape[0] > 1:
            raise BadRequestError("The image should be monochromatic.")

        color = unique_colors[0]

        # Select all pixels of the detected color
        layer: np.ndarray = np.all(image == color, axis=-1) * 1

        # self.geometry = self.__resize_canvas(layer)
        self.geometry = self.__resize_layer(layer).astype(np.uint8)

    def set_geometry_cli(self, cli_file: bytes) -> None:
        """Defines the geometry of this drum based on the given CLI file.

        Args:
            cli_file: A bytes object representing the CLI file
        """
        if cli_file == b"":
            self.geometry = np.zeros(self.geometry.shape, dtype=np.uint8)
        else:
            try:
                cli = pycli.parse(cli_file)
            except pycli.ParsingError as error:
                raise BadRequestError(
                    f"Error with CLI file: {str(error)}") from error

            self.geometry = self.__resize_canvas(self.__draw_cli(cli))

    def __draw_cli(self, cli: CLI) -> np.ndarray:
        """Draws the CLI onto the given canvas.

        This function will only draw the first non empty layer of the CLI. An
        empty layer is a layer with no polylines. This function modify the
        coordinates'axes. The origin is translated from the bottom left corner
        to the center of the build space. The Y axis is also flipped to better
        suit the way data is represented inside a Numpy array.

        Args:
            cli: The CLI object to draw
        """
        canvas = np.zeros(
            tuple(e * self._config.enhancement_factor
                  for e in self.geometry.shape))
        pixel_size = self._config.pixel_size / self._config.enhancement_factor

        # Loop through the polylines
        for polyline in cli.geometry.layers[0].polylines:
            if polyline.orientation == 1:
                fill = 1
            else:
                fill = -1

            poly_canvas = np.zeros(canvas.shape, dtype=np.int32)

            points = np.array(polyline)

            # Center coordinates
            points *= cli.header.units / pixel_size
            points[:, 0] = +points[:, 0] + canvas.shape[1] / 2
            points[:, 1] = -points[:, 1] + canvas.shape[0] / 2

            # Round to get int32 data
            points = points.round().astype(np.int32)

            # Draw filled polygon
            cv2.fillPoly(poly_canvas, [points], fill)
            canvas += poly_canvas

        canvas = np.clip(canvas, 0, 1)

        return canvas

    def __resize_canvas(self, canvas: np.ndarray) -> np.ndarray:
        """Resizes the given canvas

        Args:
            canvas: The canvas to resize

        Returns:
            A resized ndarray
        """
        return cv2.resize(canvas,
                          dsize=tuple(reversed(self.geometry.shape)),
                          interpolation=cv2.INTER_NEAREST).astype(np.uint8)

    def __resize_layer(self, layer: np.ndarray) -> np.ndarray:
        """Resizes the given layer to fit the build space dimensions set
        in the configuration. It will cut off the pattern if it is too large or
        it will pad it if it is too small.
        """
        # Loaded image siz
        img_height, img_width = layer.shape

        # Build space size
        bs_height = self.geometry.shape[0]
        bs_width = self.geometry.shape[1]

        # Scaling factors
        scale_height = bs_height / img_height
        scale_width = bs_width / img_width

        # Repeat factors
        if scale_height <= 1:
            pad_height = 0
        else:
            pad_height = bs_height - img_height

        if scale_width <= 1:
            pad_width = 1
        else:
            pad_width = bs_width - img_width

        repeated_layer = np.pad(layer, ((0, pad_height), (pad_width, 0)))
        resized_layer = repeated_layer[:bs_height, :bs_width]

        return resized_layer
