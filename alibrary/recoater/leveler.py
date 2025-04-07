"""Module describing a class to control the leveler."""
from alibrary.logger import logger
from alibrary.pneumatic.valve import PneumaticValve
from alibrary.server import BadRequestError
from alibrary.recoater.drums import Blade


class Leveler:
    """Interface to read and control every aspect of the recoater leveler.

    Attributes:
        max_pressure: The maximum pressure that can be set to the leveler
        target_pressure: The target pressure of this leveler
        pcb: The interface to the underlying pcb
    """

    def __init__(self, valve: PneumaticValve, max_pressure: float = 5) -> None:
        self._max_pressure = max_pressure
        self._target_pressure: float = 0.0

        self.valve = valve

        self.valve.perform_homing()

    @property
    def pressure(self) -> dict[str,]:
        """Returns the current, target and max pressure values of the leveler.

        Returns:
            A JSON object describing the different pressure values

        Raises:
            InternalServerError: An error occurs in the process
        """
        current = self.valve.get_pressure()

        values = {
            "target": self._target_pressure,
            "maximum": self._max_pressure,
            "value": current
        }

        return values

    @pressure.setter
    def pressure(self, pressure: dict[str,]) -> None:
        """Sets the requested pressure.

        Args:
            A JSON object describing the target pressure

        Raises:
            InternalServerError: An error occurs in the process
            BadRequestError: The request pressure is invalid
        """
        pressure = pressure["target"]

        # Validation
        if not 0 <= pressure < self._max_pressure:
            raise BadRequestError(
                f"(leveler) The pressure should be between 0 and"
                f" {self._max_pressure} but received {pressure}")

        # Application
        self.valve.set_pressure(pressure)

        self._target_pressure = pressure
        logger.info("Leveler suction target pressure set to %f", pressure)

    @staticmethod
    def get_sensor_info() -> dict[str,]:
        """Returns the state of the leveler blade sensor.

        Returns:
            The state of the blade ensor

        Raises:
            InternalServerError: An error occurs in the process
        """

        json = {"state": True}

        return json

    def activate_regulation(self):
        """Activates the pressure regulation of the valve."""
        self.valve.activate_regulation(self._target_pressure)

    def deactivate_regulation(self):
        """Deactivates the pressure regulation of the valve."""
        self.valve.deactivate_regulation()


class LevelerWithBlade(Leveler):
    """Leveler equipped with a motorized blade."""
    def __init__(
        self,
        valve: PneumaticValve,
        blade: Blade,
        max_pressure: float = 5,
    ) -> None:
        self._blade: Blade = blade
        super().__init__(valve, max_pressure)

    @property
    def blade(self) -> Blade:
        """The blade added to this leveler."""
        return self._blade
