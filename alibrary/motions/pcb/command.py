"""Modules defining a differential screw motion command for a PssPCB stepper.

This is an implementation of the abstract MotionCommand for a PssPCB stepper.

To handle the different kind of motors that we might use in the machines, an
abstract class is defined. This allows to have a template and to benefit from
OOP advantages for the motors and motions.
"""
from alibrary.motions.abstract.command import MotionCommand, MotionType


class PCBScrewMotionCommand(MotionCommand):
    """Implementation of the MotionCommand class for a differential screw
    connected to the PssPCB.

    Attributes:
        motion_type: The type of motion
        distance: A float representing the distance traveled in the motion
    """

    @classmethod
    def from_json(cls, json: dict[str,]) -> "PCBScrewMotionCommand":
        """Returns a PCBScrewMotionCommand from the given JSOn object.

        Args:
            json: A JSON object to deserialize

        Returns:
            A PCBScrewMotionCommand
        """

        motion_type = MotionType[str(
            json["mode"]).upper()] if "mode" in json else MotionType.RELATIVE

        distance = float(json["distance"]) if "distance" in json else 0.0

        return cls(motion_type=motion_type, distance=distance)

    def to_json(self) -> dict[str,]:
        """Returns a JSON representation of this command.

        Returns:
            A JSON object representing this PCBScrewMotionCommand
        """
        json = {
            "mode": self.motion_type.name.lower(),
            "distance": self.distance,
        }

        return json
