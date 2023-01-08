"""
Test mri3d.src.volume
"""

# pylint: disable=redefined-outer-name

import os
import filecmp
import pytest
import numpy as np
from mri3d.src import volume
from mri3d.src.volume import Volume


# TODO numba fails in test environment
IN_CI = 'IN_CI' in os.environ


@pytest.fixture
def test_array():
    """np.arange(27).reshape((3,3,3))"""

    return np.arange(27).reshape((3, 3, 3))


@pytest.fixture
def test_volume(test_array: np.ndarray):
    """Volume for testing"""

    return Volume(test_array, (1, .5, .5), (-1, 50))


@pytest.fixture
def test_volume_half(test_volume: Volume):
    """downsampled Volume for testing"""

    return Volume.halfsample(test_volume)


@pytest.mark.parametrize(
    "idx, shape, expected",
    [
        ((0, 0, 0), (0, 0, 0), False),
        ((0, 0, 0), (1, 1, 1), True),
        ((-1, -1, -1), (10, 10, 10), False),
        ((1000, 0, 0), (1000, 1, 1), False),
        ((1000, 0, 0), (1001, 1, 1), True),
    ])
def test_in_bounds(idx: tuple[int, int, int], shape: tuple[int, int, int], expected: bool) -> None:
    """
    test in_bounds
    """
    assert expected == volume.in_bounds(*idx, shape)


@pytest.mark.parametrize(
    "idx, expected",
    [
        ((0, 0, 0), 0),
        ((0, 0, 1), 1),
        ((-1, 0, 0), 0),
        ((30, 30, 30), 0),
    ])
def test_read_array_zero_padded(test_array: np.ndarray, idx: tuple[int, int, int], expected: int) -> None:
    """
    test read_array_zero_padded
    """
    assert expected == volume.read_array_zero_padded(test_array, *idx)


@pytest.mark.skipif(IN_CI, reason="numba fails in test environment")
@pytest.mark.parametrize(
    "idx, expected",
    [
        ((0, 0, 0), 0),
        ((0, 0, 1), 1),
        ((-1, 0, 0), 0),
        ((2.5, 1, .3), 10.65),
    ])
def test_trilinear_interpolation(test_volume: Volume, idx: tuple[float, float, float], expected: float) -> None:
    """
    test trilinear_interpolation
    """
    assert expected == volume.trilinear_interpolation(
        test_volume.data, np.array(idx))


@pytest.mark.skipif(IN_CI, reason="numba fails in test environment")
def test_interpolate_volume_data_parallel(test_volume: Volume) -> None:
    """
    test interpolate_volume_data_parallel
    """

    factor = 1.2

    expected = np.array([[[0, 0, 1, 1],
                          [2, 3, 4, 2],
                          [5, 5, 6, 3],
                          [3, 3, 3, 2]],
                         [[7, 8, 9, 4],
                          [10, 10, 11, 6],
                          [12, 13, 14, 7],
                          [6, 7, 7, 3]],
                         [[15, 15, 16, 8],
                          [17, 18, 19, 9],
                          [20, 20, 21, 11],
                          [10, 10, 11, 5]],
                         [[9, 9, 9, 5],
                          [10, 10, 11, 5],
                          [11, 11, 12, 6],
                          [6, 6, 6, 3]]])

    result_shape = np.ceil(
        np.array(test_volume.data.shape) * factor).astype(np.uint)
    result = np.empty(result_shape, dtype=test_volume.data.dtype)

    volume.interpolate_volume_data_parallel(test_volume.data, result, factor)

    assert (expected == result).all()


@pytest.mark.skipif(IN_CI, reason="numba fails in test environment")
def test_interpolate_volume_data(test_volume: Volume) -> None:
    """
    test interpolate_volume_data
    """

    factor = 1.2

    expected = np.array([[[0, 0, 1, 1],
                          [2, 3, 4, 2],
                          [5, 5, 6, 3],
                          [3, 3, 3, 2]],
                         [[7, 8, 9, 4],
                          [10, 10, 11, 6],
                          [12, 13, 14, 7],
                          [6, 7, 7, 3]],
                         [[15, 15, 16, 8],
                          [17, 18, 19, 9],
                          [20, 20, 21, 11],
                          [10, 10, 11, 5]],
                         [[9, 9, 9, 5],
                          [10, 10, 11, 5],
                          [11, 11, 12, 6],
                          [6, 6, 6, 3]]], dtype=test_volume.data.dtype)

    result = volume.interpolate_volume_data(test_volume.data, factor)

    assert (expected == result).all()


@pytest.mark.parametrize(
    "axis, k, expected",
    [
        (0, 1, np.array([[[2, 5, 8],
                          [1, 4, 7],
                          [0, 3, 6]],
                         [[11, 14, 17],
                          [10, 13, 16],
                          [9, 12, 15]],
                         [[20, 23, 26],
                          [19, 22, 25],
                          [18, 21, 24]]])),
        (1, 4, np.arange(27).reshape((3, 3, 3))),
        (2, -3, np.array([[[6, 7, 8],
                           [15, 16, 17],
                           [24, 25, 26]],
                          [[3, 4, 5],
                           [12, 13, 14],
                           [21, 22, 23]],
                          [[0, 1, 2],
                           [9, 10, 11],
                           [18, 19, 20]]])),
    ])
def test_rotate90(test_volume: Volume, axis: int, k: int, expected: np.ndarray) -> None:
    """
    test rotate90
    """

    assert (expected == Volume.rotate90(test_volume, axis, k=k).data).all()


def test_halfsample(test_volume: Volume) -> None:
    """
    test halfsample
    """

    expected = np.array([[[0, 2],
                          [6, 8]],
                         [[18, 20],
                          [24, 26]]])

    assert (expected == Volume.halfsample(test_volume).data).all()


@pytest.mark.skipif(IN_CI, reason="numba fails in test environment")
@pytest.mark.parametrize(
    "factor, expected",
    [
        (1.2, np.array([[[0, 0, 1, 1],
                         [2, 3, 4, 2],
                         [5, 5, 6, 3],
                         [3, 3, 3, 2]],
                        [[7, 8, 9, 4],
                         [10, 10, 11, 6],
                         [12, 13, 14, 7],
                         [6, 7, 7, 3]],
                        [[15, 15, 16, 8],
                         [17, 18, 19, 9],
                         [20, 20, 21, 11],
                         [10, 10, 11, 5]],
                        [[9, 9, 9, 5],
                         [10, 10, 11, 5],
                         [11, 11, 12, 6],
                         [6, 6, 6, 3]]])),
        (.5, np.array([[[0, 2],
                        [6, 8]],
                       [[18, 20],
                        [24, 26]]]))
    ])
def test_resample(test_volume: Volume, factor: float, expected: np.ndarray) -> None:
    """
    test resample
    """

    assert (expected == Volume.resample(test_volume, factor).data).all()


@pytest.mark.skipif(IN_CI, reason="numba fails in test environment")
def test_normalize_spacing(test_volume: Volume) -> None:
    """
    test normalize_spacing
    """

    expected_spacing = (0.5, 0.5, 0.5)
    expected_data = np.array([[[0, 1, 2],
                               [3, 4, 5],
                               [6, 7, 8]],
                              [[4, 5, 6],
                               [7, 8, 9],
                               [10, 11, 12]],
                              [[9, 10, 11],
                               [12, 13, 14],
                               [15, 16, 17]],
                              [[13, 14, 15],
                               [16, 17, 18],
                               [19, 20, 21]],
                              [[18, 19, 20],
                               [21, 22, 23],
                               [24, 25, 26]],
                              [[9, 9, 10],
                               [10, 11, 11],
                               [12, 12, 13]]])

    normalized = Volume.normalize_spacing(test_volume)

    assert expected_spacing == normalized.spacing
    assert (expected_data == normalized.data).all()


@pytest.mark.skipif(IN_CI, reason="numba fails in test environment")
def test_normalized(test_volume: Volume) -> None:
    """
    test normalized
    """

    normalized = Volume.normalize_spacing(test_volume)

    assert not test_volume.normalized()
    assert normalized.normalized()


TEST_DIR = os.path.dirname(__file__)
TIFF_TEMP_PATH = os.path.join(TEST_DIR, 'tiff.temp')
TIFF_TEST_PATH = os.path.join(TEST_DIR, 'test.tiff')
VOX_TEMP_PATH = os.path.join(TEST_DIR, 'vox.temp')
VOX_TEST_PATH = os.path.join(TEST_DIR, 'test.vox')


@pytest.fixture(scope="session", autouse=True)
def delete_temp_files():
    """
    delete temp files after tests
    """

    yield 1

    if os.path.exists(TIFF_TEMP_PATH):
        os.remove(TIFF_TEMP_PATH)

    if os.path.exists(VOX_TEMP_PATH):
        os.remove(VOX_TEMP_PATH)


# TODO TIFF test fails in test environment
@pytest.mark.skipif(IN_CI, reason="maybe crlf x lf?")
def test_save_to_tiff(test_volume_half: Volume) -> None:
    """
    test save_to_tiff
    """

    test_volume_half.save_to_tiff(TIFF_TEMP_PATH)

    assert filecmp.cmp(TIFF_TEST_PATH, TIFF_TEMP_PATH)


def test_save_to_vox(test_volume_half: Volume) -> None:
    """
    test save_to_vox
    """

    test_volume_half.save_to_vox(VOX_TEMP_PATH)

    assert filecmp.cmp(VOX_TEST_PATH, VOX_TEMP_PATH)
