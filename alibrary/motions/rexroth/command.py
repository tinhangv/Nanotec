"""Modules defining a Rexroth motion command.

This is an implementation of the abstract MotionCommand for a Rexroth axis.

To handle the different kind of motors that we might use in the machines, an
abstract class is defined. This allows to have a template and to benefit from
OOP advantages for the motors and motions.
"""
from alibrary.motions.abstract.command import MotionCommand, MotionType


class RexrothMotionCommand(MotionCommand):
    """Implementation of the MotionCommand class for a Rexroth motor.

    Attributes:
        motion_type: The type of motion
        distance: A float representing the distance traveled in the motion
    """

    @classmethod
    def from_json(cls, json: dict[str,]) -> "RexrothMotionCommand":
        """Returns a RexrothMotionCommand from the given JSOn object.

        Args:
            json: A JSON object to deserialize

        Returns:
            A RexrothMotionCommand
        """

        motion_type = MotionType[str(
            json["mode"]).upper()] if "mode" in json else MotionType.RELATIVE

        distance = float(json["distance"]) if "distance" in json else 0.0

        speed = float(json["speed"]) if "speed" in json else 0.0

        return cls(motion_type=motion_type, distance=distance, speed=speed)

    def to_json(self) -> dict[str,]:
        """Returns a JSON representation of this command.

        Returns:
            A JSON object representing this RexrothMotionCommand
        """
        json = {
            "mode": self.motion_type.name.lower(),
            "distance": self.distance,
            "speed": self.speed,
        }

        return json
