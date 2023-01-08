"""
Test mri3d.src.parsedicom
"""

from mri3d.src import parsedicom
import pytest


# @pytest.mark.parametrize(
#    "x , expected",
#    [
#        (3, 3),
#        (6, 6),
#        (1, 1),
#        (10, 10),
#        (15, 15),
#    ])
# def test_test_func(x: int, expected: int) -> None:
#    """
#    Test test_func
#    """
#    assert expected == parsedicom.test_func(x)

# TODO get_tag_value, sex is missing
# TODO has_any_series
# TODO create_volume

# TODO Patient.from_dicom
# TODO Series.from_dicom
