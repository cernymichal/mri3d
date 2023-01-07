'''
dicom dataset navigator
'''

from __future__ import annotations
from typing import Any
from dataclasses import dataclass
from pathlib import Path
import numpy as np
import pydicom
from ..volume import Volume
from .dicom_indices import *


UNKNOWN_VALUE = 'UNKNOWN'


def get_tag_value(dataset: pydicom.dataset.Dataset, tag: Any) -> Any:
    '''
    safely get value from dataset, returns UNKNOWN_VALUE if dataset doesnt contain tag
    '''

    if tag not in dataset:
        return UNKNOWN_VALUE

    return dataset[tag].value


class Dataset:
    '''
    holds the pydicom Dataset together with filesystem information
    '''

    def __init__(self, path: Path):
        self.base_dir = path
        self.ds = pydicom.dcmread(self.base_dir)
        self.root_dir = Path(self.ds.filename).resolve().parent

    def has_any_series(self) -> bool:
        '''
        returns if dataset contains any series
        '''

        for patient in self.ds.patient_records:
            for study in get_studies(patient):
                if get_series(study):
                    return True

        return False

    def __str__(self) -> str:
        return str(self.ds)


def get_studies(patient: pydicom.dataset.Dataset) -> list[pydicom.dataset.Dataset]:
    '''
    returns all studies from a patient's pydicom Dataset
    '''

    return [child for child in patient.children if child.DirectoryRecordType == "STUDY"]


def get_series(study: pydicom.dataset.Dataset) -> list[pydicom.dataset.Dataset]:
    '''
    returns all series from a study's pydicom Dataset
    '''

    return [child for child in study.children if child.DirectoryRecordType == "SERIES"]


def get_images(series: pydicom.dataset.Dataset) -> list[pydicom.dataset.Dataset]:
    '''
    returns all images from a series' pydicom Dataset
    '''

    return [child for child in series.children if child.DirectoryRecordType == "IMAGE"]


def create_volume(images: list[pydicom.dataset.Dataset], ds: Dataset) -> Volume:
    '''
    returns a Volume composited from DICOM slice images
    '''

    paths = [image["ReferencedFileID"] for image in images]
    # relative path to list of str
    paths = [[path.value] if path.VM == 1 else path.value for path in paths]
    # finally to Paths
    paths = [Path(*p) for p in paths]

    # read images
    slices = [pydicom.dcmread(Path(ds.root_dir) / p) for p in paths]
    # sort to physical order
    slices.sort(key=lambda s: float(s.SliceLocation), reverse=True)

    if slices[0][IMAGE_SAMPLES_PER_PIXEL_INDEX].value != 1:
        raise RuntimeError("Color data not supported")  # TODO

    pixel_data = np.array([slice.pixel_array for slice in slices])
    spacing = (slices[0].SliceThickness, *slices[0].PixelSpacing)

    return Volume(pixel_data, spacing, slices[0][IMAGE_BITS_STORED_INDEX].value)


@dataclass
class Patient:
    '''
    holds relevant parsed patient information
    '''

    name: str
    sex: str
    identification: str

    @classmethod
    def from_dicom(cls, patient: pydicom.dataset.Dataset) -> Patient:
        '''
        returns a Patient parsed from a paydicom Dataset
        '''

        return cls(
            name=get_tag_value(patient, PATIENT_NAME_INDEX),
            identification=get_tag_value(patient, PATIENT_ID_INDEX),
            sex=get_tag_value(patient, PATIENT_SEX_INDEX)
        )


@dataclass
class Series:
    '''
    holds relevant parsed series information
    '''

    number: str
    study: str
    study_description: str

    @classmethod
    def from_dicom(cls, study: pydicom.dataset.Dataset, series: pydicom.dataset.Dataset) -> Series:
        '''
        returns a Series parsed from a paydicom Dataset
        '''

        return cls(
            number=get_tag_value(series, SERIES_NUMBER_INDEX),
            study=get_tag_value(study, STUDY_ID_INDEX),
            study_description=get_tag_value(study, STUDY_DESCRIPTION_INDEX)
        )
