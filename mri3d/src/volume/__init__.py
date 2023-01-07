'''
volume storage and operations with numpy
'''

from __future__ import annotations
from pathlib import Path
import numpy as np
from numba import njit


@njit(fastmath=True)
def trilinear_interpolation(volume: np.ndarray, sample: np.ndarray) -> float:
    '''
    TODO

    https://en.wikipedia.org/wiki/Trilinear_interpolation
    '''

    bl = np.floor(sample).astype(np.uint)
    tr = bl + np.array([1, 1, 1])
    xd, yd, zd = sample % 1

    c00 = volume[bl[0], bl[1], bl[2]] * \
        (1 - xd) + volume[tr[0], bl[1], bl[2]] * xd
    c01 = volume[bl[0], bl[1], tr[2]] * \
        (1 - xd) + volume[tr[0], bl[1], tr[2]] * xd
    c10 = volume[bl[0], tr[1], bl[2]] * \
        (1 - xd) + volume[tr[0], tr[1], bl[2]] * xd
    c11 = volume[bl[0], tr[1], tr[2]] * \
        (1 - xd) + volume[tr[0], tr[1], tr[2]] * xd

    c0 = c00 * (1 - yd) + c10 * yd
    c1 = c01 * (1 - yd) + c11 * yd

    c = c0 * (1 - zd) + c1 * zd

    return c


def interpolate_volume_data(volume: np.ndarray, factor: np.ndarray):
    '''
    TODO
    '''

    interpolated_data = np.empty(np.ceil(
        np.array(volume.data.shape) * factor).astype(np.uint), dtype=volume.dtype)

    # TODO pad with zeroes

    for x in range(0, interpolated_data.shape[0]):
        for y in range(0, interpolated_data.shape[1]):
            for z in range(0, interpolated_data.shape[2]):
                # TODO this shouldnt work
                # if (np.array((x, y, z)) == np.array(interpolated_data.shape) - (1, 1, 1)).any():
                #     continue
                interpolated_data[x, y, z] = trilinear_interpolation(
                    volume, np.array((x, y, z)) / factor)

    return interpolated_data


class Volume:
    '''
    holds volume in a numpy array

    spacing is in mm
    '''

    def __init__(self, data: np.ndarray, spacing: tuple[float], bits_per_sample: int):
        self.data = data
        self.spacing = spacing
        self.bits_per_sample = bits_per_sample
        # TODO uint assumed
        self.value_range = (0, 2 ** self.bits_per_sample - 1)

    @staticmethod
    def rotate90(volume: Volume, axis: int, k: int = 1) -> Volume:
        '''
        rotate volume 90 degrees around axis k times, applies the right hand rule
        '''

        axes = ((1, 2), (2, 0), (0, 1))[axis]
        data = np.rot90(volume.data, k=k, axes=axes)

        new_spacing = list(volume.spacing)
        if k % 2 == 1:
            new_spacing[axes[0]], new_spacing[axes[1]
                                              ] = new_spacing[axes[1]], new_spacing[axes[0]]

        return Volume(data, tuple(new_spacing), volume.bits_per_sample)

    @staticmethod
    def halfsample(volume: Volume) -> Volume:
        '''
        TODO
        '''

        return Volume(volume.data[::2, ::2, ::2], volume.spacing, volume.bits_per_sample)

    @staticmethod
    def resample(volume: Volume, factor: float) -> Volume:
        '''
        TODO
        '''

        return Volume(interpolate_volume_data(volume.data, np.ones(3) * factor), volume.spacing, volume.bits_per_sample)

    @staticmethod
    def normalize_spacing(volume: Volume) -> Volume:
        '''
        TODO
        '''

        min_spacing = min(volume.spacing)
        max_spacing = max(volume.spacing)
        max_axis = volume.spacing.index(max_spacing)

        factor = np.ones(3)
        factor[max_axis] = max_spacing / min_spacing

        new_spacing = list(volume.spacing)
        new_spacing[max_axis] = min_spacing

        return Volume(interpolate_volume_data(volume.data, factor), tuple(new_spacing), volume.bits_per_sample)

    def save_to_tiff(self, filepath: Path) -> None:
        '''
        saves volume data to 3d tiff

        writes metadata to custom tags:
        - 2048, 3x FLOAT - spacingpy
        - 2049, 2x FLOAT - value_range

        requires tifffile to be installed
        '''

        import tifffile as tf
        tf.imwrite(filepath, data=self.data, compression=tf.COMPRESSION.NONE,  # bitspersample=self.bits_per_sample,  packints_encode is not implemented
                   resolution=self.spacing[0:2], resolutionunit=tf.RESUNIT.MILLIMETER, extratags=[(2048, tf.DATATYPE.FLOAT, 3, self.spacing, True), (2049, tf.DATATYPE.FLOAT, 2, self.value_range, True)])

    def save_to_vox(self, filepath: Path) -> None:
        '''
        saves volume data to Magica Voxel .vox

        - all axes must be less than 256 in length

        requires py-vox-io to be installed
        '''

        if (np.array(self.data.shape) > 256).any():
            raise OverflowError(
                ".vox format only supports coordinates up to 256")

        from pyvox.models import Vox, Color
        from pyvox.writer import VoxWriter

        # requires the data to be mapped to <0; 255>
        data_rounded = np.interp(
            self.data, self.value_range, (0, 255)).round().astype(np.uint8)

        vox = Vox.from_dense(data_rounded)
        vox.pallete = [Color(0, 0, 0, i) for i in range(256)]
        VoxWriter(filepath, vox).write()

    def __str__(self):
        return f'Volume{self.data.shape} with spacing {self.spacing}'
