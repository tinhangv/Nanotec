"""Module defining a subclass of Drum that integrates a powder collector.
"""

from alibrary.recoater.drums.decorators.decorator import DrumDecorator
from alibrary.recoater.drums.interface import DrumInterface
from alibrary.electronics.controllino.controllino import Controllino
from alibrary import logger


class CollectorDecorator(DrumDecorator):
    """Drum equipped with a powder collector.
    """

    def __init__(self, drum: DrumInterface, controllino: Controllino) -> None:
        super().__init__(drum)
        self._controllino = controllino

    @property
    def collector(self) -> dict[str,]:
        """Returns the current state of the powder collector.

        Returns:
            A JSON object describing the collector's state
        """
        return {"state": self._controllino.get_collectors(self._drum.index)}

    @collector.setter
    def collector(self, state: dict[str,]) -> None:
        """Sets the state of the powder collector.

        Args:
            A JSON object describing the collector state
        """
        state = state["state"]
        self._controllino.set_collectors(self._drum.index, state)
        logger.info("Drum %d powder collector set to %s", self._drum.index,
                    state)
