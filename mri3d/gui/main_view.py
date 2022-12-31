'''
TODO
'''

import PySimpleGUIQt as sg
from src.volume import Volume
from .volume_plotter import VolumePlotter
from . import TITLE, ICON


def create(volume: Volume) -> None:
    '''
    TODO
    '''

    layout = [[sg.Button('Rotate X', key='-rx-'), sg.Button('Rotate Y', key='-ry-'), sg.Button('Rotate Z', key='-rz-')],
              [sg.Column([[]], key='-plot-')]]

    window = sg.Window(TITLE, layout, size=(800, 500), icon=ICON).Finalize()

    plotter = VolumePlotter(window.QT_QMainWindow,
                            background_color=sg.theme_background_color())
    plotter.plot_volume(volume)
    plotter.hook_widget(window['-plot-'].vbox_layout)

    while True:
        event, _ = window.Read()

        if event == sg.WIN_CLOSED:
            break

        if event[0:2] == '-r' and len(event) == 4:
            axis = 0 if event[2] == 'x' else 1 if event[2] == 'y' else 2
            volume.rotate90(axis)
            plotter.plot_volume(volume)

    plotter.close()
    window.close()
