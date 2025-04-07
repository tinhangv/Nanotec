"""Module describing the parameters of a layer."""


class LayerParameters:
    """List of the parameters specific to each layer.

    Attributes:
        filling_drum_id: The id of the drum with the filling material
        speed: The speed of the patterning
        x_offset: The pattern offset along the X axis
        powder_saving: A flag indicating if the powder saving techniques should
        be apply
        max_x_offset
    """

    def __init__(self,
                 filling_drum_id: int = -1,
                 speed: float = 0,
                 x_offset: float = 0,
                 powder_saving: bool = False) -> None:
        self.filling_drum_id = filling_drum_id
        self.speed = speed
        self.x_offset = x_offset
        self.powder_saving = powder_saving

        # REVIEW: What value ? Where to initialize ? Is it really useful ?
        self.max_x_offset = 1000

    @classmethod
    def from_json(cls, json: dict[str,]) -> "LayerParameters":
        """Deserializes a JSON object.

        This method returns a LayerParameters object based on th given JSON.

        Args:
            json: The JSON object to deserialize

        Returns:
            A LayerParameters object
        """

        filling_id = int(json["filling_id"]) if "filling_id" in json else 0

        speed = float(json["speed"]) if "speed" in json else 0.0

        x_offset = float(json["x_offset"]) if "x_offset" in json else 0.0

        powder_saving = bool(
            json["powder_saving"]) if "powder_saving" in json else False

        return cls(filling_drum_id=filling_id,
                   speed=speed,
                   x_offset=x_offset,
                   powder_saving=powder_saving)

    def to_json(self) -> dict[str,]:
        """Returns a JSON representation of this LayerParameters.

        Returns:
            A JSON dictionary
        """
        json = {
            "filling_id": self.filling_drum_id,
            "speed": self.speed,
            "x_offset": self.x_offset,
            "max_x_offset": self.max_x_offset,
            "powder_saving": self.powder_saving,
        }

        return json
