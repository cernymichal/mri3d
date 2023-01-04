'''
TODO
'''

import PySimpleGUIQt as sg
from src import ApplicationState
from src.parsedicom import Patient, Series
from src.volume import Volume
from .volume_plotter import VolumePlotter
from . import TITLE, ICON


def patient_str(patient: Patient) -> str:
    '''
    TODO
    '''

    return f'Patient: {patient.name} ({patient.sex}, {patient.identification})'


def series_str(series: Series) -> str:
    '''
    TODO
    '''

    return f'Series: {series.study_description} - {series.number}'


def resolution_str(volume: Volume) -> str:
    '''
    TODO
    '''

    return (f'Resolution: {volume.data.shape[0]}x{volume.data.shape[1]}x{volume.data.shape[2]} '
            f'({volume.spacing[0]:.3}mm : {volume.spacing[1]:.3}mm : {volume.spacing[2]:.3}mm)')


def main_view(state: ApplicationState) -> None:
    '''
    TODO
    '''

    layout = [[sg.Column([[sg.Button('  Rotate X  ', key='-rx-')],
                          [sg.Button('  Rotate Y  ', key='-ry-')],
                          [sg.Button('  Rotate Z  ', key='-rz-')]]), sg.Column([[]], key='-plot-')],
              [sg.Stretch(), sg.Button('  Save 3D texture  ', key='-e-image-'),
               sg.Button('  Create mesh  ', key='-e-mesh-'), sg.Button('  Voxelize  ', key='-e-voxel-')],
              [sg.Text(patient_str(state.patient)), sg.Text(series_str(state.series)), sg.Text(resolution_str(state.volume), key='-resolution-')]]

    window = sg.Window(TITLE, layout, size=(1200, 800), icon=ICON).Finalize()

    plotter = VolumePlotter(window.QT_QMainWindow,
                            background_color=sg.theme_background_color())
    plotter.plot_volume(state.volume)
    plotter.hook_widget(window['-plot-'].vbox_layout)

    while True:
        event, _ = window.Read()

        if event == sg.WIN_CLOSED:
            break

        if event[0:2] == '-r' and len(event) == 4:
            axis = 0 if event[2] == 'x' else 1 if event[2] == 'y' else 2
            state.volume.rotate90(axis)
            plotter.plot_volume(state.volume)
            window['-resolution-'].Update(resolution_str(state.volume))

    plotter.close()
    window.close()
