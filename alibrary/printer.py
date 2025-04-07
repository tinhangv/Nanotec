"""Module defining a printer class responsible for handling multiple layers."""
import pycli
from alibrary.print.parameters import PrintParameters
from alibrary.recoater.layer.parameters import LayerParameters
from alibrary.server import BadRequestError


class Printer:
    """Printer class responsible for handling multiple layers."""

    def __init__(self) -> None:
        self.clis: dict[int, pycli.CLI] = {}
        self.current_layer_index: int = 0
        self.parameters: PrintParameters = PrintParameters()

    def get_info(self) -> dict[str,]:
        n_layers = 0
        for cli in self.clis.values():
            if len(cli.geometry.layers) > n_layers:
                n_layers = len(cli.geometry.layers)

        return {
            "n_layers": n_layers,
            "crt_layer": self.current_layer_index,
        }

    def set_drum_cli(self, drum_id: int, cli_file: bytes):
        try:
            self.clis[drum_id] = pycli.parse(cli_file)
        except pycli.ParsingError as error:
            raise BadRequestError(
                f"Error with CLI file: {str(error)}") from error

    def get_layer_for_drum(self, layer_id: int, drum_id: int):
        if not drum_id in self.clis:
            return None
        return self.clis[drum_id].sub_cli(layer_id, layer_id +
                                          1).to_ascii().encode("ascii")

    def get_layer_parameters(self) -> LayerParameters:
        return LayerParameters(
            filling_drum_id=self.parameters.filling_drum_id,
            speed=self.parameters.patterning_speed,
            x_offset=self.parameters.x_offset,
            powder_saving=self.parameters.powder_saving,
        )
