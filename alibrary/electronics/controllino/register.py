"""Module defining a ControllinoRegister class and an enumeration of all defined
registers.
"""
from dataclasses import dataclass


@dataclass
class ControllinoRegister:
    """A fake register implemented in the Controllino layer.

    The parameters are isolated and consider like registers on the PLCs.
    A register is identify by a controllino id and a register id.

    For each register, this class specifies the number of bytes and if an
    acknowledgement is sent.
    """
    controllino_id: int
    register_id: int
    ack: bool
    n_bytes: int


@dataclass
class ControllinoRegisters:
    """List of Controllino registers"""
    SAFETY_STATUS = ControllinoRegister(0, 0, False, 1)
    EJECTION_PRESSURE_DRUM_1 = ControllinoRegister(0, 1, False, 1)
    EJECTION_PRESSURE_DRUM_2 = ControllinoRegister(0, 2, False, 1)
    EJECTION_PRESSURE_DRUM_3 = ControllinoRegister(1, 1, False, 1)
    FREQUENCY_VARIATOR = ControllinoRegister(0, 3, True, 2)
    SPARE = ControllinoRegister(0, 4, True, 2)
    ELECTRICAL_BRIDGE_BREAKER_1 = ControllinoRegister(0, 5, True, 2)
    ELECTRICAL_BRIDGE_BREAKER_2 = ControllinoRegister(0, 6, True, 2)
    ELECTRICAL_BRIDGE_BREAKER_3 = ControllinoRegister(1, 5, True, 2)
    POWDER_COLLECTOR_DRUM_1 = ControllinoRegister(0, 7, False, 1)
    POWDER_COLLECTOR_DRUM_2 = ControllinoRegister(0, 8, False, 1)
    POWDER_COLLECTOR_DRUM_3 = ControllinoRegister(0, 9, False, 1)
    SHOVELS = ControllinoRegister(0, 10, False, 1)
    MESH_CLEANER = ControllinoRegister(0, 11, False, 1)
    PNEUMATIC_BRIDGE_BREAKER = ControllinoRegister(0, 12, False, 1)
    GRIPPER_Z = ControllinoRegister(0, 13, False, 1)


EJECTION_REGISTERS = [
    ControllinoRegisters.EJECTION_PRESSURE_DRUM_1,
    ControllinoRegisters.EJECTION_PRESSURE_DRUM_2,
    ControllinoRegisters.EJECTION_PRESSURE_DRUM_3,
]

POWDER_COLLECTORS_REGISTERS = [
    ControllinoRegisters.POWDER_COLLECTOR_DRUM_1,
    ControllinoRegisters.POWDER_COLLECTOR_DRUM_2,
    ControllinoRegisters.POWDER_COLLECTOR_DRUM_3,
]

ELECTRICAL_BRIDGE_BREAKERS = [
    ControllinoRegisters.ELECTRICAL_BRIDGE_BREAKER_1,
    ControllinoRegisters.ELECTRICAL_BRIDGE_BREAKER_2,
    ControllinoRegisters.ELECTRICAL_BRIDGE_BREAKER_3,
]
