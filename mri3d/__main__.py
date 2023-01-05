'''
an application for opening, reviewing, slightly adjusting and exporting dicom mri volumes to standard 3d formats
'''

from gui.dicomdir import get_dicomdir, ChooseSeriesView
from gui.exporter import MainView
from src import ApplicationState, Patient, Series
from src import parsedicom


def get_state() -> ApplicationState:
    '''
    query user for dicom series
    '''

    dicomdir_path = get_dicomdir()
    if dicomdir_path is None:
        # TODO add popup
        raise RuntimeError("Not a valid path")

    # TODO catch pydicom.errors.InvalidDicomError
    dcm = parsedicom.Dataset(dicomdir_path)
    if not dcm.has_any_series():
        # TODO add popup
        raise RuntimeError("No series found")

    patient, study, series = ChooseSeriesView(dcm).run().get_chosen_values()
    if series is None:
        # TODO add popup
        raise RuntimeError("Couldn't choose a series")

    images = parsedicom.get_images(series)
    # TODO error check
    volume = parsedicom.create_volume(images, dcm)

    return ApplicationState(
        volume=volume,
        patient=Patient.from_dicom(patient),
        series=Series.from_dicom(study, series))


def main():
    '''
    app entrypoint
    '''

    try:
        state = get_state()
    except RuntimeError:
        return

    MainView(state).run()


main()
