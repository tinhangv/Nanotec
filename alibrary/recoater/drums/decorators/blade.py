"""Module defining a subclass of Drum that integrates a motorized scraping
blade.
"""
from alibrary.motions.abstract.command import MotionCommand
from alibrary.recoater.drums.blade import Blade
from alibrary.recoater.drums.interface import DrumInterface
from alibrary.recoater.drums.decorators.decorator import DrumDecorator
from alibrary.server import ConflictError


class BladeDecorator(DrumDecorator):
    """Decorator class for a drum that adds the scraping blade features."""
    def __init__(self, drum: DrumInterface, blade: Blade) -> None:
        super().__init__(drum)

        self._blade: Blade = blade

    @property
    def blade(self) -> Blade:
        """The blade added to this decorated drum."""
        return self._blade

    def start_motion(self, command: MotionCommand):
        """Starts a motion following the given motion command.

        This override first checks if the blade is above a given threshold
        before starting the motion.

        Raises:
            InternalServerError: An error occurs in the process
            BadRequestError: The given command is not valid
            ConflictError: The motor is busy with another motion
        """
        if not self.blade.is_above_threshold():
            raise ConflictError("Scraping blade to low to start a drum motion")
        return super().start_motion(command)
