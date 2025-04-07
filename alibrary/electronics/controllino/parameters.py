"""Module defining the parameters controlled by the Controllino PLC.

In the V2, the Controllino is responsible for the valves and some other
parameters. This module defines a class that gathers those parameters.
"""

from dataclasses import dataclass


# @dataclass
# class ControllinoParameters:
#     """List of parameters controlled by the Controllino on the recoater."""
#     ejection_pressures: list[float]
#     variable_frequency_drive: int = 0
#     bridge_breakers_state: bool = False

#     @classmethod
#     def from_n_drums(cls, n_drums: int) -> "ControllinoParameters":
#         return cls(ejection_pressures=[0.0] * n_drums)


@dataclass
class ControllinoParameters:
    """List of parameters controlled by the Controllino on the recoater."""
    ejection_pressures: list[float]
    powder_collectors_state: list[bool]
    variable_frequency_drive: int = 0
    bridge_breakers_state: bool = False
    shovels_state: int = 0
    gripper_state: bool = False
    n_drums: int = 0

    @classmethod
    def from_n_drums(cls, n_drums: int) -> "ControllinoParameters":
        """Factory method building a ControllinoParameters object based on the
        given number of drums.
        """
        return cls(ejection_pressures=[0.0] * n_drums,
                   powder_collectors_state=[False] * n_drums,
                   n_drums=n_drums)
