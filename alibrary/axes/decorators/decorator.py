"""Module defining an axis decorator."""
from alibrary.axes.interface import AxisInterface
from alibrary.motions.abstract.command import MotionCommand
from alibrary.motions.abstract.motor import Motor

class AxisDecorator(AxisInterface):
    """The base decorator class for an axis."""
    _axis: AxisInterface = None

    def __init__(self, axis: AxisInterface) -> None:
        self._axis = axis

    @property
    def axis(self) -> AxisInterface:
        """Returns this axis."""
        return self._axis

    @property
    def motor(self) -> Motor:
        """Returns the axis motor"""
        return self._axis.motor

    def get_info(self) -> dict[str,]:
        return self._axis.get_info()

    def get_command(self) -> dict[str,]:
        """Returns this axis infos."""
        return self._axis.get_command()

    def start_motion(self, command: MotionCommand) -> None:
        """STarts a motion on this axis."""
        self._axis.start_motion(command)

    def stop_motion(self) -> None:
        """Stops a motion on this axis."""
        self._axis.stop_motion()
