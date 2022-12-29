'''
TODO
'''

from pathlib import Path
import os
import PySimpleGUI as sg
from src import parsedicom
from . import TITLE, ICON


def get_dicomdir() -> Path:
    '''
    TODO
    '''
    dicomdir_path: Path = None
    first_input = True
    while dicomdir_path is None or not os.path.isfile(dicomdir_path):
        if not first_input:
            sg.popup_error(f'"{dicomdir_path}" is not a valid path')

        dicomdir_path = sg.popup_get_file(
            message='Select a DICOMDIR file', title=TITLE, icon=ICON)

        first_input = False
        if dicomdir_path is None:
            break

    return dicomdir_path


def _choose_series_get_options(ds: parsedicom.Dataset, indices: tuple[int, int, int] = (0, 0, 0)) -> tuple[list[str], list[str], list[str]]:
    patients = ds.ds.patient_records
    studies = parsedicom.get_studies(patients[indices[0]])
    series = parsedicom.get_series(studies[indices[1]])

    patients_labels = [
        f'{patient[(0x0010, 0x0010)].value} - {patient[(0x0010, 0x0020)].value}' for patient in patients]
    studies_labels = [
        f'{study[(0x0020, 0x0010)].value} - {study[(0x0008, 0x1030)].value}' for study in studies]
    series_labels = [str(series[(0x0020, 0x0011)].value) for series in series]

    return (patients_labels, studies_labels, series_labels)


def choose_series(ds: parsedicom.Dataset):
    '''
    TODO
    '''

    # TODO doesnt update much idk why
    patients, studies, series = _choose_series_get_options(ds)

    layout = [[sg.Text('Choose a series to load')],
              [sg.Text('Patient:', size=(9, 1)), sg.Combo(
                  patients, size=(40, 1), enable_events=True, key='-patient-')],
              [sg.Text('Study:', size=(9, 1)), sg.Combo(
                  studies, size=(40, 1), enable_events=True, key='-study-')],
              [sg.Text('Series:', size=(9, 1)), sg.Combo(
                  series, size=(40, 1), key='-series-')],
              [sg.Button('Ok'), sg.Button('Cancel')]]

    window = sg.Window(TITLE, layout, size=(390, 200), icon=ICON)

    ok = False
    indices = (0, 0, 0)

    window.read(0)

    while True:
        patients, studies, series = _choose_series_get_options(ds, indices)
        window['-patient-'].update(patients, set_to_index=indices[0])
        window['-study-'].update(studies, set_to_index=indices[1])
        window['-series-'].update(series, set_to_index=indices[2])

        event, _ = window.read()

        indices = (window['-patient-'].widget.current(),
                   window['-study-'].widget.current(),
                   window['-series-'].widget.current())

        if event in (sg.WIN_CLOSED, 'Ok', 'Cancel'):
            ok = event == 'Ok'
            break

        if event == "-patient-":
            indices = (indices[0], 0, 0)
        elif event == "-study-":
            indices = (indices[0], indices[1], 0)

    window.close()

    patient = ds.ds.patient_records[indices[0]]
    study = parsedicom.get_studies(patient)[indices[1]]
    series = parsedicom.get_series(study)[indices[2]]

    # TODO check invalid stuff
    return series if ok else None
