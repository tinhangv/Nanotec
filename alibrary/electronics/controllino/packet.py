"""Module defining a custom format packet used to communicate the depositions
matrices to the Controllino. It contains the matrices along some metadata that
will be send in a header.
"""
from dataclasses import dataclass

import numpy as np


@dataclass
class ControllinoPacket:
    """A custom format packet to communicate the deposition matrices to the
    Controllino PLC.

    One packet can hold the deposition matrix of multiple drums.
    """
    pixel_size: int
    speed: float
    offset: float = 0
    data: np.ndarray | None = None

    @property
    def line_duration(self) -> int:
        """The time between two pixel lines in µs."""
        return int(1 / (self.speed * 1000 / self.pixel_size) * 1000000)

    @property
    def n_blank_lines(self) -> int:
        """The number of blank lines before the print, the x offset in pixel"""
        return round(self.offset * 1000 / self.pixel_size)

    @property
    def n_bytes(self) -> int:
        """The number of bytes inside the data matrix of this packet."""
        if self.data is not None:
            return self.data.size
        return 0

    def __concatenate_depositions(self, d1: np.ndarray, d2: np.ndarray,
                                  offset: float) -> np.ndarray:
        """Concatenate two deposition matrices.

        The matrices are shifted by the given offset.

        Args:
            d1: The first deposition matrix
            d2: The second deposition matrix
            offset: The offset between the two deposition matrices [mm]

        Returns:
            A matrix with the result of the concatenation
        """
        offset_rows = round(offset * 1000 / self.pixel_size)

        d1o = np.pad(d1, ((0, offset_rows), (0, 0)))
        d2o = np.pad(d2, ((offset_rows, 0), (0, 0)))

        return np.concatenate((d1o, d2o), axis=1)

    @staticmethod
    def __shift_data(data: np.ndarray):
        """Shifts the given matrix to fit the valves layout."""

        shifted_data: np.ndarray = np.pad(data, ((0, 12), (0, 0)))
        shifted_data[:, 0::4] = np.roll(shifted_data[:, 0::4], 0, axis=0)
        shifted_data[:, 1::4] = np.roll(shifted_data[:, 1::4], 8, axis=0)
        shifted_data[:, 2::4] = np.roll(shifted_data[:, 2::4], 4, axis=0)
        shifted_data[:, 3::4] = np.roll(shifted_data[:, 3::4], 12, axis=0)

        return shifted_data.astype(int)

    def build_data(self, depositions: np.ndarray, gap: float):
        """Constructs the payload of this packet.

        The `data` and `n_bytes` fields will be computed and filled based on
        the given depositions matrices and gap. This can manage both single and
        double depositions.

        Args:
            depositions: An ndarray containing the depositions to send to the
            Controllino
            gap: A float describing the gap between the depositions
        """
        depositions = np.squeeze(depositions)

        if depositions.ndim == 2:
            data = np.flip(np.transpose(depositions, (1, 0)), axis=(0, 1))

            offset_rows = round(gap * 1000 / self.pixel_size)
            data = np.pad(data, ((offset_rows, 0), (0, 0)))
        elif depositions.ndim == 3 and depositions.shape[0] == 2:
            data = np.flip(np.transpose(depositions, (0, 2, 1)), axis=(1, 2))

            data = self.__concatenate_depositions(data[0], data[1], gap)
        else:
            raise ValueError("Wrong dimensions")

        # Compensate valves shifts
        data = self.__shift_data(data)

        # Convert to bytes
        self.data = np.packbits(data, axis=1, bitorder="little")
