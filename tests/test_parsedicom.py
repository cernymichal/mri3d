"""
Test mri3d.src.parsedicom
"""

# pylint: disable=redefined-outer-name

from typing import Any
import os
import pytest
import pydicom
import numpy as np
from mri3d.src import parsedicom
from mri3d.src.parsedicom import Dataset


TEST_DIR = os.path.dirname(__file__)
TEST_DATASET_PATH = os.path.join(TEST_DIR, 'test-dataset', 'DICOMDIR')
TEST_VOLUME_PATH = os.path.join(TEST_DIR, 'test-volume.npy')


@pytest.fixture(scope='session')
def testing_dataset():
    """
    loaded ./test-dataset
    """

    return Dataset(TEST_DATASET_PATH)


@pytest.fixture(scope='session')
def testing_patient_ds(testing_dataset: Dataset):
    """
    first patient from testing_dataset
    """

    return testing_dataset.ds.patient_records[0]


@pytest.fixture(scope='session')
def testing_study_ds(testing_patient_ds: pydicom.Dataset):
    """
    first study from testing_dataset
    """

    return parsedicom.get_studies(testing_patient_ds)[0]


@pytest.fixture(scope='session')
def testing_series_ds(testing_study_ds: pydicom.Dataset):
    """
    first series from testing_dataset
    """

    return parsedicom.get_series(testing_study_ds)[0]


@pytest.fixture(scope='session')
def testing_images(testing_series_ds: pydicom.Dataset):
    """
    first imageset from testing_dataset
    """

    return parsedicom.get_images(testing_series_ds)


@pytest.mark.parametrize(
    "tag, expected",
    [
        (parsedicom.dicom_indices.PATIENT_NAME_INDEX, 'NAME^NONE'),
        (parsedicom.dicom_indices.PATIENT_SEX_INDEX, parsedicom.UNKNOWN_VALUE)
    ])
def test_get_tag_value(testing_patient_ds: pydicom.Dataset, tag: tuple, expected: Any):
    """
    test get_tag_value
    """

    assert expected == parsedicom.get_tag_value(testing_patient_ds, tag)


def test_has_any_series(testing_dataset: Dataset):
    """
    test has_any_series
    """

    assert testing_dataset.has_any_series()


def test_create_volume(testing_dataset: Dataset, testing_images: list[pydicom.Dataset]):
    """
    test create_volume
    """

    volume = parsedicom.create_volume(testing_images, testing_dataset)

    assert volume.spacing == (8.0, 0.683594, 0.683594)
    assert volume.value_range == (0, 4095)
    assert volume.bits_per_sample == 12
    assert (volume.data == np.load(TEST_VOLUME_PATH)).all()


def test_patient_from_dicom(testing_patient_ds: pydicom.Dataset):
    """
    test patient_from_dicom
    """

    patient = parsedicom.Patient.from_dicom(testing_patient_ds)
    assert patient == parsedicom.Patient(
        name='NAME^NONE', sex='UNKNOWN', identification='NOID')


def test_series_from_dicom(testing_study_ds: pydicom.Dataset, testing_series_ds: pydicom.Dataset):
    """
    test series_from_dicom
    """

    series = parsedicom.Series.from_dicom(testing_study_ds, testing_series_ds)
    assert series == parsedicom.Series(
        number='1002', study='DCMTKSTUDY000000', study_description='hlava mozek')
