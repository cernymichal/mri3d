'''
TODO
'''

from typing import Any
import PySimpleGUIQt as sg
from src import ApplicationState
from .volume_plotter import ViewWithVolumePlot
from . import TITLE, ICON


class StateView(ViewWithVolumePlot):
    '''
    TODO
    '''

    def __init__(self, state: ApplicationState, *args, **kwargs) -> None:
        self.state = state
        super().__init__(*args, **kwargs)

    def patient_str(self) -> str:
        '''
        TODO
        '''

        return f'Patient: {self.state.patient.name} ({self.state.patient.sex}, {self.state.patient.identification})'

    def series_str(self) -> str:
        '''
        TODO
        '''

        return f'Series: {self.state.series.study_description} - {self.state.series.number}'

    def resolution_str(self) -> str:
        '''
        TODO
        '''

        return (f'Resolution: {self.state.volume.data.shape[0]}x{self.state.volume.data.shape[1]}x{self.state.volume.data.shape[2]} '
                f'({self.state.volume.spacing[0]:.3}mm : {self.state.volume.spacing[1]:.3}mm : {self.state.volume.spacing[2]:.3}mm)')


class MainView(StateView):
    '''
    TODO
    '''

    def __init__(self, state: ApplicationState) -> None:
        self.state = state

        layout = [[sg.Column([[sg.Button('  Rotate X  ', key='-rx-')],
                              [sg.Button('  Rotate Y  ', key='-ry-')],
                              [sg.Button('  Rotate Z  ', key='-rz-')]]), sg.Column([[]], key='-plot-')],
                  [sg.Stretch(), sg.Button('  Save  ', key='-export-'),
                   sg.Button('  Create mesh  ', key='-mesh-')],
                  [sg.Text(self.patient_str()), sg.Text(self.series_str()), sg.Text(self.resolution_str(), key='-resolution-')]]

        super().__init__(state, TITLE, layout, size=(1200, 800), icon=ICON)

        self.enable()

    def handle_events(self, event: Any, _: dict) -> bool:
        '''
        TODO
        '''

        if event == sg.WIN_CLOSED:
            return False

        if event[0:2] == '-r' and len(event) == 4:
            axis = 0 if event[2] == 'x' else 1 if event[2] == 'y' else 2
            self.state.volume.rotate90(axis)
            self.plotter.plot_volume(self.state.volume)
            self.window['-resolution-'].Update(self.resolution_str())

        if event in ('-export-', '-mesh-'):
            self.disable()

            if event == '-export-':
                ExportView(self.state).run()

            elif event == '-mesh-':
                MeshView(self.state).run()

            self.enable()

        return True

    def enable(self) -> None:
        '''
        TODO
        '''

        self.add_plotter(background_color=sg.theme_background_color())
        self.plotter.plot_volume(self.state.volume)
        super().enable()

    def disable(self) -> None:
        '''
        TODO
        '''

        super().disable()
        self.remove_plotter()


class ExportView(StateView):
    '''
    TODO
    '''

    def __init__(self, state: ApplicationState) -> None:
        self.state = state

        layout = [[sg.Column([[sg.Button('  Scale 2x  ', key='-su-')],
                              [sg.Button('  Scale .5x  ', key='-sd-')]]), sg.Column([[]], key='-plot-')],
                  [sg.Stretch(), sg.Button('  Save TIFF  ', key='-save-tiff-'),
                   sg.Button('  Save VOX  ', key='-save-vox-')],
                  [sg.Stretch(), sg.Text(self.resolution_str(), key='-resolution-')]]

        super().__init__(state, TITLE, layout, size=(1200, 800), icon=ICON)

        self.add_plotter(background_color=sg.theme_background_color())
        self.plotter.plot_volume(self.state.volume)

    def handle_events(self, event: Any, _: dict) -> bool:
        '''
        TODO
        '''

        if event == sg.WIN_CLOSED:
            return False

        if event[0:2] == '-s' and len(event) == 4:
            # TODO interpolate volume
            self.window['-resolution-'].Update(self.resolution_str())

        elif event == '-save-tiff-':
            # TODO save to tiff
            pass

        elif event == '-save-vox-':
            # TODO save to vox
            pass

        return True


class MeshView(StateView):
    '''
    TODO
    '''

    def __init__(self, state: ApplicationState) -> None:
        self.state = state

        layout = [[sg.Column([[sg.Button('  Scale 2x  ', key='-su-')],
                              [sg.Button('  Scale .5x  ', key='-sd-')],
                              [sg.Button('  ???  ', key='-idk-')]]), sg.Column([[]], key='-plot-')],
                  [sg.Stretch(), sg.Button('  Save OBJ  ', key='-save-')],
                  [sg.Text("Polygons: TODO", key='-polycount-'), sg.Stretch(), sg.Text(self.resolution_str(), key='-resolution-')]]

        super().__init__(state, TITLE, layout, size=(1200, 800), icon=ICON)

        self.add_plotter(background_color=sg.theme_background_color())
        self.plotter.plot_volume(self.state.volume)

    def handle_events(self, event: Any, _: dict) -> bool:
        '''
        TODO
        '''

        if event == sg.WIN_CLOSED:
            return False

        if event[0:2] == '-s' and len(event) == 4:
            # TODO interpolate volume
            self.window['-resolution-'].Update(self.resolution_str())

        return True
