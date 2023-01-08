"""
Test mri3d.gui
"""

# pylint: disable=redefined-outer-name

import os
import pytest
from mri3d.src.gui.dicomdir import ChooseSeriesView
from mri3d.src.gui.exporter import MainView
from mri3d.src import parsedicom
from mri3d.src import ApplicationState


TEST_DIR = os.path.dirname(__file__)
TEST_DATASET_PATH = os.path.join(TEST_DIR, 'test-dataset', 'DICOMDIR')


@pytest.fixture(scope='session')
def testing_dataset():
    """
    loaded ./test-dataset
    """

    return parsedicom.Dataset(TEST_DATASET_PATH)


# ======== dicomdir.py


@pytest.fixture(scope='session')
def testing_choose_series_view(testing_dataset: parsedicom.Dataset):
    """
    mock ChooseSeriesView

    __init__ is not called !!
    """

    # instantiating without calling __init__ !!
    # https://stackoverflow.com/questions/6383914/is-there-a-way-to-instantiate-a-class-without-calling-init
    view = ChooseSeriesView.__new__(ChooseSeriesView)
    view.ds = testing_dataset
    view.ok = False
    view.indices = (0, 0, 0)

    return view


def test_choose_series_view_get_options(testing_choose_series_view: ChooseSeriesView):
    """
    test choose_series_view_get_options
    """

    assert testing_choose_series_view._get_options() == (
        ['NAME^NONE - NOID'], ['DCMTKSTUDY000000 - hlava mozek'], ['1002'])


@pytest.mark.parametrize(
    "ok, indices, expected",
    [
        (True, (0, 0, 0), 1),
        (False, (0, 0, 0), None),
        (True, (0, 0, 1), None)
    ])
def test_choose_series_view_get_chosen_values(testing_choose_series_view: ChooseSeriesView, ok: bool, indices: tuple[int, int, int], expected):
    """
    test choose_series_view_get_chosen_values
    """

    testing_choose_series_view.ok = ok
    testing_choose_series_view.indices = indices

    if expected is None:
        assert testing_choose_series_view.get_chosen_values() == (None, None, None)
    else:
        output = testing_choose_series_view.get_chosen_values()
        assert output[0] is not None and output[1] is not None and output[2] is not None


# ======== exporter.py


@ pytest.fixture(scope='session')
def testing_main_view(testing_dataset: parsedicom.Dataset):
    """
    mock MainView

    __init__ is not called !!
    """

    patient = testing_dataset.ds.patient_records[0]
    study = parsedicom.get_studies(patient)[0]
    series = parsedicom.get_series(study)[0]
    images = parsedicom.get_images(series)
    volume = parsedicom.create_volume(images, testing_dataset)

    # instantiating without calling __init__ !!
    # https://stackoverflow.com/questions/6383914/is-there-a-way-to-instantiate-a-class-without-calling-init
    view = MainView.__new__(MainView)
    view.state = ApplicationState(
        volume, parsedicom.Patient.from_dicom(patient), parsedicom.Series.from_dicom(study, series))

    return view


def test_state_view_title_str(testing_main_view: MainView):
    """
    test state_view_title_str
    """

    assert testing_main_view.title_str() == 'NAME^NONE - 1002'


def test_state_view_patient_str(testing_main_view: MainView):
    """
    test state_view_patient_str
    """

    assert testing_main_view.patient_str() == 'Patient: NAME^NONE (UNKNOWN, NOID)'


def test_state_view_series_str(testing_main_view: MainView):
    """
    test state_view_series_str
    """

    assert testing_main_view.series_str() == 'Series: hlava mozek - 1002'


def test_state_view_resolution_str(testing_main_view: MainView):
    """
    test state_view_resolution_str
    """

    assert 'Resolution: 3x512x512 (8.0mm : 0.684mm : 0.684mm)'


def test_state_view_normalized_str(testing_main_view: MainView):
    """
    test state_view_normalized_str
    """

    assert testing_main_view.normalized_str() == ''


# TODO mock window object?
# test MainView.rotate
# test MainView.resample
# test MainView.normalize
# test MainView.save_to_tiff
# test MainView.save_to_vox
