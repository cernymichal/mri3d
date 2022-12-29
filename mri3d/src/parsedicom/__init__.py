'''
TODO
'''

from pathlib import Path
import numpy as np
import pydicom
from ..volume import Volume


class Dataset:
    def __init__(self, path: Path):
        self.base_dir = path
        self.ds = pydicom.dcmread(self.base_dir)
        self.root_dir = Path(self.ds.filename).resolve().parent

    def has_any_series(self) -> bool:
        for patient in self.ds.patient_records:
            for study in get_studies(patient):
                if get_series(study):
                    return True

        return False

    def __str__(self) -> str:
        return str(self.ds)


def get_studies(patient: pydicom.dataset.Dataset) -> list[pydicom.dataset.Dataset]:
    # TODO generators?
    return [child for child in patient.children if child.DirectoryRecordType == "STUDY"]


def get_series(study: pydicom.dataset.Dataset) -> list[pydicom.dataset.Dataset]:
    return [child for child in study.children if child.DirectoryRecordType == "SERIES"]


def get_images(series: pydicom.dataset.Dataset) -> list[pydicom.dataset.Dataset]:
    return [child for child in series.children if child.DirectoryRecordType == "IMAGE"]


def get_volume(images: list[pydicom.dataset.Dataset], ds: Dataset) -> Volume:
    paths = [image["ReferencedFileID"] for image in images]
    # relative path to list of str
    paths = [[path.value] if path.VM == 1 else path.value for path in paths]
    # finally to Paths
    paths = [Path(*p) for p in paths]

    # read images
    slices = [pydicom.dcmread(Path(ds.root_dir) / p) for p in paths]
    # sort to physical order
    slices.sort(key=lambda s: float(s.SliceLocation), reverse=True)

    pixel_data = np.array([slice.pixel_array for slice in slices])
    spacing = (slices[0].SliceThickness, *slices[0].PixelSpacing)

    return Volume(pixel_data, spacing)


def test_func(x: int) -> int:
    return x
