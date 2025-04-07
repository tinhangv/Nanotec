"""Module defining an axis equipped with a gripper."""
from alibrary.axes.decorators.decorator import AxisDecorator
from alibrary.axes.interface import AxisInterface
from alibrary.electronics.controllino import Controllino
from alibrary.logger import logger

class AxisWithGripper(AxisDecorator):
    """Decorated axis equipped with a gripper."""
    def __init__(self, axis: AxisInterface, controllino: Controllino) -> None:
        super().__init__(axis)
        self._controllino = controllino

    @property
    def gripper(self) -> dict[str,]:
        """Returns the current state of the gripper.

        Returns:
            A JSON object describing the gripper's state
        """
        return {"state": self._controllino.get_gripper_state()}

    @gripper.setter
    def gripper(self, state: dict[str,]) -> None:
        """Sets the state of the gripper.

        Args:
            A JSON object describing the gripper state
        """
        state = state["state"]
        self._controllino.set_gripper_state(state)
        logger.info("Gripper set to %s", state)
