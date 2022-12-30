'''
TODO
'''

from pyvistaqt import QtInteractor
import PySimpleGUIQt as sg
import pyvista as pv
from src.volume import Volume
from . import TITLE, ICON


def _get_grid(volume: Volume) -> pv.UniformGrid:
    grid = pv.UniformGrid()
    grid.dimensions = volume.data.shape
    grid.spacing = volume.spacing
    grid.point_data['values'] = volume.data.flatten(order='F')
    return grid


def _reset_plot(plotter: pv.BasePlotter, volume: Volume) -> None:
    plotter.clear_actors()
    plotter.view_isometric()
    plotter.add_volume(_get_grid(volume), clim=volume.value_range, cmap='bone', opacity='sigmoid',
                       scalar_bar_args={'title': '', 'label_font_size': 14, 'fmt': ' % .3f'})


def create(volume: Volume) -> None:
    '''
    TODO
    '''

    layout = [[sg.Button('Rotate X', key='-rx-'), sg.Button('Rotate Y', key='-ry-'), sg.Button('Rotate Z', key='-rz-')],
              [sg.Column([[]], key='-plot-')]]

    window = sg.Window(TITLE, layout, size=(800, 500), icon=ICON).Finalize()

    plotter = QtInteractor(window.QT_QMainWindow)
    plotter.show_axes()
    plotter.enable_anti_aliasing()
    plotter.add_bounding_box(color='white')
    _reset_plot(plotter, volume)

    window['-plot-'].vbox_layout.addWidget(plotter.interactor)

    while True:
        event, _ = window.Read()

        if event == sg.WIN_CLOSED:
            break

        if event[0:2] == '-r' and len(event) == 4:
            axis = 0 if event[2] == 'x' else 1 if event[2] == 'y' else 2
            volume.rotate90(axis)
            _reset_plot(plotter, volume)

    plotter.close()
    window.close()
