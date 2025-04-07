"""Module describing the different states of a Nanotec driver."""
from enum import Enum, auto


class NanotecDriverState(Enum):
    """Different states of the Nanotec driver"""
    NOT_READY_TO_SWITCH_ON = auto()
    SWITCH_ON_DISABLED = auto()
    READY_TO_SWITCH_ON = auto()
    SWITCHED_ON = auto()
    OPERATION_ENABLED = auto()
    QUICK_STOP_ACTIVE = auto()
    FAULT_REACTION_ACTIVE = auto()
    FAULT = auto()
    UNKNOWN = auto()

    @classmethod
    def from_status_word(cls, status_word: int) -> "NanotecDriverState":
        """Returns the NanotecDriverState associated with the given status word.

        Args:
            status_word: An integer representing the content of the status word
            of the driver

        Returns:
            A NanotecDriverState object
        """
        nanotec_driver_state = {
            0x0: {
                0: NanotecDriverState.NOT_READY_TO_SWITCH_ON,
                1: NanotecDriverState.SWITCH_ON_DISABLED
            },
            0x1: NanotecDriverState.READY_TO_SWITCH_ON,
            0x3: NanotecDriverState.SWITCHED_ON,
            0x7: {
                1: NanotecDriverState.OPERATION_ENABLED,
                0: NanotecDriverState.QUICK_STOP_ACTIVE
            },
            0xF: NanotecDriverState.FAULT_REACTION_ACTIVE,
            0x8: NanotecDriverState.FAULT
        }

        low_four_bits = status_word & 0xF

        if low_four_bits == 0:
            sod = (status_word & 0x40) >> 6

            return cls(nanotec_driver_state[low_four_bits][sod])
        if low_four_bits == 0x7:
            qs = (status_word & 0x20) >> 5

            return cls(nanotec_driver_state[low_four_bits][qs])
        if low_four_bits in nanotec_driver_state:
            return cls(nanotec_driver_state[low_four_bits])

        return NanotecDriverState.UNKNOWN
