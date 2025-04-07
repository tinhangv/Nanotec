"""Module describing a Layer class containing the parameters and preview of the
current layer.
"""
import cv2
import matplotlib.colors as mc
import numpy as np

from alibrary.recoater.config import RecoaterConfig
from alibrary.recoater.layer.parameters import LayerParameters


class Layer:
    """Class containing the current layer parameters and able to generate a
    preview from drum's geometries.
    """

    def __init__(self) -> None:
        self.parameters = LayerParameters()
        self.odd_lines = False

    # @staticmethod
    # def __process_powders(geometries: np.ndarray):
    #     """Constructs new geometries by dilating the current ones and by
    #     assigning each pixel to only one powder.

    #     Args:
    #         geometries: A 3D array containing the geometry of each drum

    #     Returns:
    #         A ndarray with the new geometries
    #     """
    #     # Build mask
    #     mask = np.clip(np.sum(geometries, axis=0), 0, 1, dtype=np.uint8)
    #     kernel = np.ones((3, 3), np.uint8)
    #     mask = cv2.dilate(mask, kernel, iterations=3)

    #     # Compute distance of every pixel to the nearest non-zero one
    #     distance_maps = np.zeros(geometries.shape)
    #     for i, geo in enumerate(geometries):
    #         distance_maps[i] = cv2.distanceTransform(
    #             1 - geo, cv2.DIST_L2, maskSize=cv2.DIST_MASK_PRECISE)

    #     # Assign powder
    #     argmin_of_distance = distance_maps.argmin(axis=0)
    #     for i in range(geometries.shape[0]):
    #         geometries[i] = (argmin_of_distance == i) * mask

    def __fill_build_space(self, geometries: np.ndarray):
        """Constructs new geometries taking the filling into account.

        This will add the filling pixel to the corresponding drum.

        Args:
            geometries: A 3D array containing the geometry of each drum

        Returns:
            A ndarray with the new geometries
        """
        mask = np.sum(geometries, axis=0).astype(np.uint8).clip(0, 1)

        kernel = np.ones((3, 3), np.uint8)
        mask = cv2.dilate(mask, kernel, iterations=3)

        # Compute distance of every pixel to the nearest non-zero one
        distance_maps = np.zeros(geometries.shape)
        for i, geo in enumerate(geometries):
            distance_maps[i] = cv2.distanceTransform(
                1 - geo, cv2.DIST_L2, maskSize=cv2.DIST_MASK_PRECISE)

        # Assign powder
        argmin_of_distance = distance_maps.argmin(axis=0)
        for i in range(geometries.shape[0]):
            geometries[i] = (argmin_of_distance == i) * mask

        filling = 1 - mask
        if self.parameters.powder_saving:
            start = 1 if self.odd_lines else 0
            filling[start::2, :] = 0
            self.odd_lines = not self.odd_lines

        geometries[self.parameters.filling_drum_id] += filling

    @staticmethod
    def __apply_powder_offsets(geometries: np.ndarray,
                               powder_offsets: list[int]):
        """Applies the powder offsets on each drum deposition matrix.
        """
        kernel = np.ones((1, 3), np.uint8)
        for i in range(geometries.shape[0]):
            geometries[i] = cv2.dilate(geometries[i],
                                       kernel,
                                       iterations=powder_offsets[i])

    @staticmethod
    def apply_build_space_dimensions(geometries: np.ndarray,
                                     config: RecoaterConfig):
        """Applies a mask on the given geometries to make them fit the build
        space size.

        Args:
            geometries: The geometries to modify
            config: The recoater configuration containing the build space
            dimensions
        """
        gw, gl = geometries[0].shape
        if config.build_space.has_length_and_width():
            bw = int(config.build_space.width * 1000 / config.resolution)
            bl = int(config.build_space.length * 1000 / config.resolution)

            mw = (gw - bw) // 2
            ml = (gl - bl) // 2

            mask = np.zeros((gw, gl))
            mask[mw:mw + bw, ml:ml + bl] = 1
            mask = mask == 1
        elif config.build_space.has_diameter():
            # Circular mask
            cw, cl = gw // 2, gl // 2
            y, x = np.ogrid[:gw, :gl]
            dist_from_center = np.sqrt((y - cw)**2 + (x - cl)**2)
            mask = dist_from_center <= config.build_space.diameter
        else:
            mask = np.ones((gw, gl))
            mask = mask == 1
        geometries[:, ~mask] = 0

    def get_depositions(self, geometries: np.ndarray, config: RecoaterConfig,
                        powder_offsets: list[int]) -> np.ndarray:
        """Returns the powder depositions matrices.

        It compiled all the drum geometries and add the filling powder. It then
        resizes the depositions using the size of the build space.

        Args:
            geometries: An array of drum geometry
            config: The recoater config providing the build space size and the
            resolution
            powder_offsets: A list of powder offsets to apply to the drums
            geometries

        Returns:
            A powder deposition matrix of 3 dimensions with all the individual
            drum deposition
        """
        new_geometries = np.copy(geometries)

        # Add filling and shell
        if self.parameters.filling_drum_id != -1:
            self.__fill_build_space(geometries=new_geometries)

        # Add powder offsets
        self.__apply_powder_offsets(geometries=new_geometries,
                                    powder_offsets=powder_offsets)

        # Apply build space size
        self.apply_build_space_dimensions(new_geometries, config)

        return new_geometries

    @staticmethod
    def get_preview(depositions: np.ndarray) -> bytes:
        """Generates and returns a BGR image representing the given depositions
        matrix.

        Args:
            depositions: A matrix with all the drum powder deposition

        Returns:
            A bytes object representing the BGR PNG image
        """
        # Build image canvas
        n_drums = depositions.shape[0]
        width = depositions.shape[1]
        length = depositions.shape[2]
        image = np.zeros((width, length, 4))

        # Copy colors from Matplotlib tableau colors
        preview_colors = np.array(
            [[e * 255 for e in c] for c in map(mc.to_rgba, mc.TABLEAU_COLORS)],
            dtype=np.uint8)

        # RGBA to BGRA conversion
        preview_colors[:, [0, 2]] = preview_colors[:, [2, 0]]

        # Apply colors
        for index in range(n_drums):
            for channel in range(4):
                image[:, :, channel] += depositions[index] * preview_colors[
                    index][channel]

        # Converts numpy array into PNG bytes string
        png = cv2.imencode(".png", image)[1].tobytes()

        return png
