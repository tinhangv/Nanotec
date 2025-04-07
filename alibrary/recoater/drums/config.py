"""Module defining a configuration object for an Aerosint drum."""
from dataclasses import dataclass

@dataclass
class DrumConfig:
    """Dataclass with all the configuration variables of a drum.

    Attributes:
        circumference: The circumference of the drum [mm]
        max_suction_pressure: The maximum pressure for this drum suction [bar]
        max_ejection_pressure: The maximum pressure for this drum ejection [bar]
        pixel_size: The size of a pixel of this drum [mm]
        geometry_size: The size of this drum build space
        enhancement_factor: A dilatation factor that improves the CLI drawings
    """
    circumference: float = 0.0
    max_suction_pressure: float = 0
    max_ejection_pressure: float = 0
    pixel_size: int = 0
    geometry_size: tuple[int, int] = (192, 192)
    enhancement_factor: int = 10
