"""Module describing the set of drums of a recoater."""
import numpy as np

from alibrary.recoater.drums.interface import DrumInterface
from alibrary.server import NotFoundError


class Drums(list[DrumInterface]):
    """Set of drums on an Aerosint recoater."""

    def __getitem__(self, index):
        try:
            return super().__getitem__(index)
        except IndexError as error:
            raise NotFoundError(str(error)) from error

    def get_info(self) -> list[dict[str,]]:
        """Returns the list of the drums info.

        Returns:
            A list of the drums'info

        Raises:
            InternalServerError: An error occurs in the process
        """
        return [drum.get_info() for drum in self]

    def get_geometries(self) -> np.ndarray:
        """Returns all the geometries of its children

        Returns:
            An ndarray containing the geometry of each children drum
        """
        return np.array([drum.geometry for drum in self])
