"""Module describing a recoater configuration class"""
from dataclasses import dataclass


@dataclass
class BuildSpace:
    """Dimensions of the build space

    Attributes:
        diameter: The diameter of a circular build space
        length: The length of a rectangular build space
        width: The width of a rectangular build space
    """
    diameter: float | None = None
    length: float | None = None
    width: float | None = None

    def has_length_and_width(self) -> bool:
        """Checks if this build space has a length and a width defined

        Returns:
            True if both length and width are defined, false otherwise
        """
        return self.length is not None and self.width is not None

    def has_diameter(self) -> bool:
        """Checks if this build space has a diameter defined

        Returns:
            True if diameter is defined, false otherwise
        """
        return self.diameter is not None


class RecoaterConfig:
    """A recoater configuration

    Attributes:
        resolution: The size of a pixel in this recoater deposition [µm]
        gaps: A list of float representing the gaps between the drums
        build_space: A BuildSpace definition
    """

    def __init__(
            self,
            resolution: int,
            ejection_matrix_size: int,
            gaps: list[float],
            build_space: BuildSpace = BuildSpace(),
    ) -> None:
        self.resolution = resolution
        self.ejection_matrix_size = ejection_matrix_size
        self.gaps = gaps
        self.build_space = build_space

    @classmethod
    def from_json(cls, json: dict[str,]) -> "RecoaterConfig":
        """Deserializes a JSON object.

        This method returns a RecoaterConfig object based on th given JSON.

        Args:
            json: The JSON object to deserialize

        Returns:
            A RecoaterConfig object
        """
        resolution = int(json["resolution"]) if "resolution" in json else 0

        ejection_matrix_size = int(json["ejection_matrix_size"]
                                  ) if "ejection_matrix_size" in json else 0

        gaps = json["gaps"] if "gaps" in json else [0.0]

        diameter = float(json["build_space_diameter"]
                        ) if "build_space_diameter" in json else None

        length = None
        width = None
        if "build_space_dimensions" in json:
            dimensions = json["build_space_dimensions"]
            length = float(
                dimensions["length"]) if "length" in dimensions else None
            width = float(
                dimensions["width"]) if "width" in dimensions else None

        build_space = BuildSpace(diameter=diameter, length=length, width=width)

        return cls(resolution=resolution,
                   ejection_matrix_size=ejection_matrix_size,
                   gaps=gaps,
                   build_space=build_space)

    def to_json(self) -> dict[str,]:
        """Returns a JSON representation of this RecoaterConfig.

        Returns:
            A JSON dictionary
        """
        json = {
            "resolution": self.resolution,
            "ejection_matrix_size": self.ejection_matrix_size,
            "gaps": self.gaps,
        }

        if self.build_space.has_length_and_width():
            json["build_space_dimensions"] = {
                "length": self.build_space.length,
                "width": self.build_space.width
            }

        if self.build_space.has_diameter():
            json["build_space_diameter"] = self.build_space.diameter

        return json
