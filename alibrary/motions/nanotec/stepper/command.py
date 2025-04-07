"""Modules defining a Nanotec driver motion command for a stepper motor.

This is an implementation of the abstract MotionCommand for a Nanotec driver.

To handle the different kind of motors that we might use in the machines, an
abstract class is defined. This allows to have a template and to benefit from
OOP advantages for the motors and motions.
"""
from alibrary.motions.abstract.command import MotionCommand, MotionType


class NanotecStepperMotionCommand(MotionCommand):
    """Implementation of the MotionCommand class for a stepper motor connected
    to a Nanotec driver.


    Attributes:
        motion_type: The type of motion
        speed: A float representing the speed of the motion
        distance: A float representing the distance traveled in the motion
    """

    @classmethod
    def from_json(cls, json: dict[str,]) -> "NanotecStepperMotionCommand":
        """Returns a NanotecStepperMotionCommand from the given JSOn object.

        Args:
            json: A JSON object to deserialize

        Returns:
            A NanotecStepperMotionCommand
        """
        motion_type = MotionType[str(
            json["mode"]).upper()] if "mode" in json else MotionType.RELATIVE

        speed = float(json["speed"]) if "speed" in json else 0.0

        distance = float(json["distance"]) if "distance" in json else 0.0

        turns = float(json["turns"]) if "turns" in json else 0.0

        return cls(motion_type=motion_type,
                   speed=speed,
                   distance=distance,
                   turns=turns)

    def to_json(self) -> dict[str,]:
        """Returns a JSON representation of this command.

        Returns:
            A JSON object representing this NanotecStepperMotionCommand
        """
        json = {
            "mode": self.motion_type.name.lower(),
            "speed": self.speed,
            "distance": self.distance,
            "turns": self.turns
        }

        return json
