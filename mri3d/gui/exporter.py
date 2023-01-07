'''
views for editing and exporting a Volume
'''

from __future__ import annotations
from typing import Any
import PySimpleGUIQt as sg
from src import ApplicationState
from src.volume import Volume
from .volume_plotter import ViewWithVolumePlot
from . import TITLE, ICON


class StateView(ViewWithVolumePlot):
    '''
    a view prepared for showing ApplicationState
    '''

    def __init__(self, state: ApplicationState, *args, **kwargs) -> None:
        self.state = state
        super().__init__(*args, **kwargs)

    def patient_str(self) -> str:
        '''
        parse state patient information into a string
        '''

        return f'Patient: {self.state.patient.name} ({self.state.patient.sex}, {self.state.patient.identification})'

    def series_str(self) -> str:
        '''
        parse state series information into a string
        '''

        return f'Series: {self.state.series.study_description} - {self.state.series.number}'

    def resolution_str(self) -> str:
        '''
        parse state volume resolution into a string
        '''

        return (f'Resolution: {self.state.volume.data.shape[0]}x{self.state.volume.data.shape[1]}x{self.state.volume.data.shape[2]} '
                f'({self.state.volume.spacing[0]:.3}mm : {self.state.volume.spacing[1]:.3}mm : {self.state.volume.spacing[2]:.3}mm)')


class MainView(StateView):
    '''
    main view of the application

    preview and rotate volume, offers export options
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
        if event == sg.WIN_CLOSED:
            return False

        if event[0:2] == '-r' and len(event) == 4:
            axis = 0 if event[2] == 'x' else 1 if event[2] == 'y' else 2
            self.state.volume = Volume.rotate90(self.state.volume, axis)
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

    def enable(self) -> MainView:
        self.add_plotter(background_color=sg.theme_background_color())
        self.plotter.plot_volume(self.state.volume)
        super().enable()
        return self

    def disable(self) -> MainView:
        super().disable()
        # also remove the plotter to avoid OpenGL errors
        self.remove_plotter()
        return self


class ExportView(StateView):
    '''
    view for exporting a Volume to matrix based formats
    '''

    def __init__(self, state: ApplicationState) -> None:
        self.state = state

        layout = [[sg.Column([[sg.Button('  Scale 2x  ', key='-su-')],
                              [sg.Button('  Scale .5x  ', key='-sd-')]]), sg.Column([[]], key='-plot-')],
                  [sg.Stretch(), sg.SaveAs('  Save TIFF  ', key='-save-tiff-', target='-tiff-path-', file_types=(("TIFF Files", "*.tiff"), ("ALL Files", "*"))),
                   sg.SaveAs('  Save VOX  ', key='-save-vox-', target='-vox-path-', file_types=(("VOX Files", "*.vox"), ("ALL Files", "*")))],
                  [sg.Stretch(), sg.Text(self.resolution_str(), key='-resolution-')],
                  [sg.Input(key='-tiff-path-', enable_events=True, visible=False), sg.Input(key='-vox-path-', enable_events=True, visible=False)]]

        super().__init__(state, TITLE, layout, size=(1200, 800), icon=ICON)

        self.add_plotter(background_color=sg.theme_background_color())
        self.plotter.plot_volume(self.state.volume)

    def handle_events(self, event: Any, values: dict) -> bool:
        if event == sg.WIN_CLOSED:
            return False

        if event[0:2] == '-s' and len(event) == 4:
            if event[2] == 'd':
                self.state.volume = Volume.halfsample(self.state.volume)
            else:
                self.state.volume = Volume.resample(self.state.volume, 2)
            self.window['-resolution-'].Update(self.resolution_str())
            self.plotter.plot_volume(self.state.volume)

        elif event == '-tiff-path-':
            # TODO fs error
            self.state.volume.save_to_tiff(values['-tiff-path-'])

        elif event == '-vox-path-':
            # TODO dim error
            # TODO fs error
            self.state.volume.save_to_vox(values['-vox-path-'])

        return True


class MeshView(StateView):
    '''
    view for creating a mesh from a Volume
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
        if event == sg.WIN_CLOSED:
            return False

        if event[0:2] == '-s' and len(event) == 4:
            # TODO interpolate volume
            self.window['-resolution-'].Update(self.resolution_str())

        return True
