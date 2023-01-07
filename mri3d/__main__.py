'''
an application for opening, reviewing, slightly adjusting and exporting dicom mri volumes to standard 3d formats
'''

from __future__ import annotations
import traceback
import pydicom.errors
from gui import popup_error
from gui.dicomdir import get_dicomdir, ChooseSeriesView
from gui.exporter import MainView
from src import ApplicationState, Patient, Series
from src import parsedicom


def get_state() -> ApplicationState | None:
    '''
    query user for a DICOM series to load
    '''

    while True:
        dicomdir_path = get_dicomdir()
        if dicomdir_path is None:  # user quit
            return None

        try:
            dcm = parsedicom.Dataset(dicomdir_path)
        except pydicom.errors.InvalidDicomError:
            popup_error('Not a valid DICOMDIR file.')
            continue

        if not dcm.has_any_series():
            popup_error('No series found in DICOMDIR.')
            continue

        patient, study, series = ChooseSeriesView(
            dcm).run().get_chosen_values()
        if series is None:  # user quit
            return None

        try:
            images = parsedicom.get_images(series)
            volume = parsedicom.create_volume(images, dcm)
        except:  # pylint: disable=bare-except
            popup_error(
                f'Unknown error while loading volume:\n{traceback.format_exc()}')

        return ApplicationState(
            volume=volume,
            patient=Patient.from_dicom(patient),
            series=Series.from_dicom(study, series))


def main():
    '''
    app entrypoint
    '''

    state = get_state()
    if state is None:  # user quit
        return

    MainView(state).run()


try:
    main()
except:  # pylint: disable=bare-except
    popup_error(f'Unknown error occured:\n{traceback.format_exc()}')
