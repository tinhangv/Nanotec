"""Modules defining an abstract motion command.

This can be used to start a motion on a motor.

To handle the different kind of motors that we might use in the machines, an
abstract class is used. This allows to have a template and to benefit from OOP
advantages for the motors and motions.
"""
from abc import ABC, abstractmethod
from enum import Enum, auto


class MotionType(Enum):
    """Types of motion"""
    ABSOLUTE = auto()
    RELATIVE = auto()
    TURNS = auto()
    HOMING = auto()
    SPEED = auto()


class MotionCommand(ABC):
    """Abstract class representing a motion command.

    This command can be given to an Actuator to start a motion.
    """

    def __init__(self,
                 motion_type: MotionType = MotionType.RELATIVE,
                 speed: float = 0.0,
                 distance: float = 0.0,
                 turns: float = 0.0) -> None:
        self.motion_type = motion_type
        self.speed = speed
        self.distance = distance
        self.turns = turns

    @classmethod
    @abstractmethod
    def from_json(cls, json: dict[str,]) -> "MotionCommand":
        """Deserializes a JSON object.

        This method returns a MotionCommand object based on the given JSON.

        Args:
            json: The JSON object to deserialize

        Returns:
            A MotionCommand object
        """

    @abstractmethod
    def to_json(self) -> dict[str,]:
        """Returns a JSON representation of this MotionCommand.

        Returns:
            A JSON dictionary
        """
