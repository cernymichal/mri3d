'''
volume storage and operations with numpy
'''

from __future__ import annotations
from pathlib import Path
import numpy as np
from numba import njit, prange


VOX_PALLETE_ALPHA = [(255, 255, 255, i) for i in range(256)]
VOX_PALLETE_GRAYSCALE = [(i, i, i, 255) for i in range(256)]


def value_range_bits(dtype: np.dtype, bits: int) -> tuple[float, float]:
    '''
    returns a value_range representable in dtype with bits
    '''

    if np.issubdtype(dtype, np.unsignedinteger):
        return (0, 2 ** bits - 1)

    if np.issubdtype(dtype, np.signedinteger):
        return (-2 ** (bits - 1), 2 ** (bits - 1) - 1)

    return (float('-inf'), float('inf'))


@njit()
def in_bounds(x: int, y: int, z: int, shape: tuple[int, int, int]) -> bool:
    '''
    check if index (x, y, z) is contained in an array
    '''

    return 0 <= x < shape[0] and 0 <= y < shape[1] and 0 <= z < shape[2]


@njit()
def read_array_zero_padded(array: np.ndarray, x: int, y: int, z: int):
    '''
    read from array is if it was zero padded infinitely
    '''
    return array[x, y, z] if in_bounds(x, y, z, array.shape) else 0


@njit(fastmath=True)
def trilinear_interpolation(volume: np.ndarray, sample: np.ndarray) -> float:
    '''
    get interpolated value at sample index from volume data

    - borders of the volume behave as if padded by zeroes
    - uniform point distribution in volume assumed

    https://en.wikipedia.org/wiki/Trilinear_interpolation
    '''

    bl = np.floor(sample).astype(np.uint)
    tr = bl + np.array([1, 1, 1])
    xd, yd, zd = sample % 1

    # zeroes if sample points are out of bounds
    c000 = read_array_zero_padded(volume, bl[0], bl[1], bl[2])
    c001 = read_array_zero_padded(volume, bl[0], bl[1], tr[2])
    c010 = read_array_zero_padded(volume, bl[0], tr[1], bl[2])
    c011 = read_array_zero_padded(volume, bl[0], tr[1], tr[2])
    c100 = read_array_zero_padded(volume, tr[0], bl[1], bl[2])
    c101 = read_array_zero_padded(volume, tr[0], bl[1], tr[2])
    c110 = read_array_zero_padded(volume, tr[0], tr[1], bl[2])
    c111 = read_array_zero_padded(volume, tr[0], tr[1], tr[2])

    # interpolate along x
    c00 = c000 * (1 - xd) + c100 * xd
    c01 = c001 * (1 - xd) + c101 * xd
    c10 = c010 * (1 - xd) + c110 * xd
    c11 = c011 * (1 - xd) + c111 * xd

    # interpolate along y
    c0 = c00 * (1 - yd) + c10 * yd
    c1 = c01 * (1 - yd) + c11 * yd

    # interpolate along z
    c = c0 * (1 - zd) + c1 * zd

    return c


@njit(parallel=True)
def interpolate_volume_data_parallel(volume: np.ndarray, target: np.ndarray, factor: np.ndarray) -> None:
    '''
    interpolates the whole volume into target with factor in parallel for the x axis
    '''

    for x in prange(target.shape[0]):  # pylint: disable=not-an-iterable
        for y in range(target.shape[1]):
            for z in range(target.shape[2]):
                target[x, y, z] = trilinear_interpolation(
                    volume, np.array((x, y, z)) / factor)


def interpolate_volume_data(volume: np.ndarray, factor: np.ndarray) -> np.ndarray:
    '''
    interpolates the whole volume with factor

    - wraps interpolate_volume_data_parallel for convenience
    '''
    # TODO interpolated values precision loss due to uint cast

    resulting_shape = np.ceil(
        np.array(volume.data.shape) * factor).astype(np.uint)
    interpolated_data = np.empty(resulting_shape, dtype=volume.dtype)

    interpolate_volume_data_parallel(volume, interpolated_data, factor)

    return interpolated_data


class Volume:
    '''
    holds volume in a numpy array

    - spacing is in mm
    - value_range is only really useful for intergral data types
    '''

    def __init__(self, data: np.ndarray, spacing: tuple[float] = (1, 1, 1), value_range: tuple[float, float] = None, bits_per_sample: int = 16):
        '''
        creates a new Volume

        - default value_range is (data.min(), data.max())
        '''

        self.data = data
        self.spacing = spacing
        self.value_range = value_range
        self.bits_per_sample = bits_per_sample

        if self.value_range is None:
            self.recalculate_value_range()

    @staticmethod
    def rotate90(volume: Volume, axis: int, k: int = 1) -> Volume:
        '''
        rotate volume 90 degrees around axis k times, applies the right hand rule

        returns the generated Volume
        '''

        axes = ((1, 2), (2, 0), (0, 1))[axis]
        data = np.rot90(volume.data, k=k, axes=axes)

        new_spacing = list(volume.spacing)
        if k % 2 == 1:
            new_spacing[axes[0]], new_spacing[axes[1]
                                              ] = new_spacing[axes[1]], new_spacing[axes[0]]

        return Volume(data, spacing=tuple(new_spacing), value_range=volume.value_range, bits_per_sample=volume.bits_per_sample)

    @staticmethod
    def halfsample(volume: Volume) -> Volume:
        '''
        downsample the volume data by 2

        returns the generated Volume
        '''

        return Volume(volume.data[::2, ::2, ::2], spacing=volume.spacing, value_range=volume.value_range, bits_per_sample=volume.bits_per_sample)

    @staticmethod
    def resample(volume: Volume, factor: float) -> Volume:
        '''
        resample the volume data by factor

        returns the generated Volume
        '''

        return Volume(interpolate_volume_data(volume.data, np.ones(3) * factor), spacing=volume.spacing, value_range=volume.value_range, bits_per_sample=volume.bits_per_sample)

    @staticmethod
    def normalize_spacing(volume: Volume) -> Volume:
        '''
        resample the volume data along one axis so that uniform spacing is achieved

        - multiple passes will be needed if volume is not uniform along any plane

        returns the generated Volume
        '''

        min_spacing = min(volume.spacing)
        max_spacing = max(volume.spacing)
        max_axis = volume.spacing.index(max_spacing)

        factor = np.ones(3)
        factor[max_axis] = max_spacing / min_spacing

        new_spacing = list(volume.spacing)
        new_spacing[max_axis] = min_spacing

        return Volume(interpolate_volume_data(volume.data, factor), spacing=tuple(new_spacing), value_range=volume.value_range, bits_per_sample=volume.bits_per_sample)

    @staticmethod
    def get_bottom_half(volume: Volume) -> Volume:
        '''
        returns the volume as if sliced in half
        '''

        sliced_data = np.copy(volume.data)
        sliced_data[:, :, sliced_data.shape[2] // 2:-1] = 0

        return Volume(sliced_data, spacing=volume.spacing, value_range=volume.value_range, bits_per_sample=volume.bits_per_sample)

    def recalculate_value_range(self) -> Volume:
        '''
        sets value_range to (data.min(), data.max())

        returns self
        '''

        self.value_range = (self.data.min(), self.data.max())
        return self

    def save_to_tiff(self, filepath: Path) -> None:
        '''
        saves volume data to 3d tiff

        writes metadata to custom tags:
        - 2048, 3x FLOAT - spacingpy
        - 2049, 2x FLOAT - value_range

        requires tifffile to be installed
        '''

        value_range_float = (
            float(self.value_range[0]), float(self.value_range[1]))

        import tifffile as tf
        tf.imwrite(filepath, data=self.data, compression=tf.COMPRESSION.NONE,  # bitspersample=self.bits_per_sample, packints_encode is not implemented
                   resolution=self.spacing[1:3], resolutionunit=tf.RESUNIT.MILLIMETER, extratags=[
                       (2048, tf.DATATYPE.FLOAT, 3, self.spacing, True), (2049, tf.DATATYPE.FLOAT, 2, value_range_float, True)])

    def save_to_vox(self, filepath: Path, with_alpha: bool = False) -> None:
        '''
        saves volume data to Magica Voxel .vox

        - all axes must be less than 256 in length
        - alpha doesn't seem to be supported by MagicaVoxel yet, but the option is there

        requires py-vox-io to be installed
        '''

        if (np.array(self.data.shape) > 256).any():
            raise OverflowError(
                ".vox format only supports coordinates up to 256")

        from pyvox.models import Vox
        from pyvox.writer import VoxWriter

        # requires the data to be mapped to <0; 255>
        data_rounded = np.interp(
            self.data, self.value_range, (0, 255)).round().astype(np.uint8)

        vox = Vox.from_dense(data_rounded)
        vox.pallete = VOX_PALLETE_ALPHA if with_alpha else VOX_PALLETE_GRAYSCALE
        VoxWriter(filepath, vox).write()

    def normalized(self) -> bool:
        '''
        checks if the volume's spacing is uniform
        '''

        return self.spacing[0] == self.spacing[1] and self.spacing[1] == self.spacing[2]

    def __str__(self) -> str:
        return f'Volume{self.data.shape} with spacing {self.spacing}'
