"""Module describing the parameters of a print job."""


class PrintParameters:
    """List of the parameters specific to a print job.

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
                 patterning_speed: float = 0,
                 travel_speed: float = 0,
                 z_speed: float = 0,
                 x_offset: float = 0,
                 z_offset: float = 0,
                 layer_thickness: float = 0,
                 collectors_delay: int = 0,
                 layer_start: int = 0,
                 layer_end: int = 0,
                 powder_saving: bool = False) -> None:
        self.filling_drum_id = filling_drum_id
        self.patterning_speed = patterning_speed
        self.travel_speed = travel_speed
        self.z_speed = z_speed
        self.x_offset = x_offset
        self.z_offset = z_offset
        self.layer_thickness = layer_thickness
        self.powder_saving = powder_saving
        self.collectors_delay = collectors_delay
        self.layer_start = layer_start
        self.layer_end = layer_end

        # REVIEW: What value ? Where to initialize ? Is it really useful ?
        self.max_x_offset = 1000

    @classmethod
    def from_json(cls, json: dict[str,]) -> "PrintParameters":
        """Deserializes a JSON object.

        This method returns a PrintParameters object based on th given JSON.

        Args:
            json: The JSON object to deserialize

        Returns:
            A PrintParameters object
        """

        filling_id = int(json["filling_id"]) if "filling_id" in json else 0

        patterning_speed = float(
            json["patterning_speed"]) if "patterning_speed" in json else 0.0

        travel_speed = float(
            json["travel_speed"]) if "travel_speed" in json else 0.0

        z_speed = float(json["z_speed"]) if "z_speed" in json else 0.0

        x_offset = float(json["x_offset"]) if "x_offset" in json else 0.0

        z_offset = float(json["z_offset"]) if "z_offset" in json else 0.0

        layer_thickness = float(
            json["layer_thickness"]) if "layer_thickness" in json else 0.0

        collectors_delay = int(
            json["collectors_delay"]) if "collectors_delay" in json else 0

        layer_start = int(json["layer_start"]) if "layer_start" in json else 0

        layer_end = int(json["layer_end"]) if "layer_end" in json else 0

        powder_saving = bool(
            json["powder_saving"]) if "powder_saving" in json else False

        return cls(filling_drum_id=filling_id,
                   patterning_speed=patterning_speed,
                   travel_speed=travel_speed,
                   z_speed=z_speed,
                   x_offset=x_offset,
                   z_offset=z_offset,
                   layer_thickness=layer_thickness,
                   collectors_delay=collectors_delay,
                   layer_start=layer_start,
                   layer_end=layer_end,
                   powder_saving=powder_saving)

    def to_json(self) -> dict[str,]:
        """Returns a JSON representation of this PrintParameters.

        Returns:
            A JSON dictionary
        """
        json = {
            "filling_id": self.filling_drum_id,
            "patterning_speed": self.patterning_speed,
            "travel_speed": self.travel_speed,
            "z_speed": self.z_speed,
            "x_offset": self.x_offset,
            "z_offset": self.z_offset,
            "max_x_offset": self.max_x_offset,
            "layer_thickness": self.layer_thickness,
            "collectors_delay": self.collectors_delay,
            "layer_start": self.layer_start,
            "layer_end": self.layer_end,
            "powder_saving": self.powder_saving,
        }

        return json
