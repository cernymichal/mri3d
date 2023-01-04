'''
TODO
'''

import gui.dicomdir
import gui.exporter
from src import ApplicationState, Patient, Series
from src import parsedicom


def main():
    '''
    app entrypoint
    '''
    dicomdir_path = gui.dicomdir.get_dicomdir()
    if dicomdir_path is None:
        # TODO add popup
        return

    dcm = parsedicom.Dataset(dicomdir_path)
    if not dcm.has_any_series():
        # TODO add popup
        return

    patient, study, series = gui.dicomdir.choose_series(dcm)
    if series is None:
        # TODO add popup
        return

    images = parsedicom.get_images(series)
    volume = parsedicom.create_volume(images, dcm)  # TODO error check

    state = ApplicationState(
        volume=volume,
        patient=Patient.from_dicom(patient),
        series=Series.from_dicom(study, series))

    del patient, study, series, images

    gui.exporter.main_view(state)


main()
