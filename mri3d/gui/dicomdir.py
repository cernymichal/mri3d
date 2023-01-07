'''
collection of views for loading a dicom image set
'''

from __future__ import annotations
from typing import Any
from pathlib import Path
import os
import PySimpleGUIQt as sg
import pydicom
from src import parsedicom
from src.parsedicom.dicom_indices import PATIENT_NAME_INDEX, PATIENT_ID_INDEX, STUDY_ID_INDEX, STUDY_DESCRIPTION_INDEX, SERIES_NUMBER_INDEX
from . import TITLE, ICON, View


def get_dicomdir() -> Path | None:
    '''
    query the user for file path with a PySimpleGUI popup
    '''
    dicomdir_path: Path = None
    first_input = True
    while dicomdir_path is None or not os.path.isfile(dicomdir_path):
        if not first_input:
            sg.PopupError(f'"{dicomdir_path}" is not a valid path')

        dicomdir_path = sg.PopupGetFile(
            message='Select a DICOMDIR file', title=TITLE, icon=ICON)

        first_input = False
        if dicomdir_path is None:
            break

    return dicomdir_path


class ChooseSeriesView(View):
    '''
    view for choosing an image series from a DICOM dataset
    '''

    def __init__(self, ds: parsedicom.Dataset) -> None:
        self.ds = ds
        self.ok = False
        self.indices = (0, 0, 0)
        patients, studies, series = self._get_options()

        layout = [[sg.Text('Choose a series to load')],
                  [sg.Text('Patient:', size=(9, 1)), sg.Combo(
                      patients, size=(40, 1), enable_events=True, key='-patient-')],
                  [sg.Text('Study:', size=(9, 1)), sg.Combo(
                      studies, size=(40, 1), enable_events=True, key='-study-')],
                  [sg.Text('Series:', size=(9, 1)), sg.Combo(
                      series, size=(40, 1), key='-series-')],
                  [sg.Column([[]])],
                  [sg.Button('  Ok  ', key='-ok-'), sg.Button('  Cancel  ', key='-cancel-'), sg.Stretch()]]

        super().__init__(TITLE, layout, size=(390, 200), icon=ICON)

    def handle_events(self, event: Any, _: dict) -> bool:
        self.indices = (self.window['-patient-'].Widget.currentIndex(),
                        self.window['-study-'].Widget.currentIndex(),
                        self.window['-series-'].Widget.currentIndex())

        if event in (sg.WIN_CLOSED, '-ok-', '-cancel-'):
            self.ok = event == '-ok-'
            return False

        if event == "-patient-":
            self.indices = (self.indices[0], 0, 0)
        elif event == "-study-":
            self.indices = (self.indices[0], self.indices[1], 0)

        patients, studies, series = self._get_options()
        self.window['-patient-'].Update(values=patients,
                                        set_to_index=self.indices[0])
        self.window['-study-'].Update(values=studies,
                                      set_to_index=self.indices[1])
        self.window['-series-'].Update(values=series,
                                       set_to_index=self.indices[2])

        return True

    def get_chosen_values(self) -> tuple[pydicom.dataset.Dataset | None, pydicom.dataset.Dataset | None, pydicom.dataset.Dataset | None]:
        '''
        returns the values chosen from the dataset
        '''

        if not self.ok:
            return (None, None, None)

        try:
            patient = self.ds.ds.patient_records[self.indices[0]]
            study = parsedicom.get_studies(patient)[self.indices[1]]
            series = parsedicom.get_series(study)[self.indices[2]]
        except IndexError:
            return (None, None, None)

        return (patient, study, series)

    def _get_options(self) -> tuple[list[str], list[str], list[str]]:
        '''
        get the correct combo box content for the current chosen values
        '''

        patients = self.ds.ds.patient_records
        studies = parsedicom.get_studies(patients[self.indices[0]])
        series = parsedicom.get_series(studies[self.indices[1]])

        patients_labels = [
            f'{patient[PATIENT_NAME_INDEX].value} - {patient[PATIENT_ID_INDEX].value}' for patient in patients]

        studies_labels = [
            f'{study[STUDY_ID_INDEX].value} - {study[STUDY_DESCRIPTION_INDEX].value}' for study in studies]

        series_labels = [str(series[SERIES_NUMBER_INDEX].value)
                         for series in series]

        return (patients_labels, studies_labels, series_labels)
