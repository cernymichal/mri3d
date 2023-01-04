'''
mri3d gui components module
'''

from typing import Any
import os
import PySimpleGUIQt as sg

TITLE = 'mri3d'
ICON = sg.DEFAULT_WINDOW_ICON

os.environ["QT_API"] = "pyside2"
sg.ChangeLookAndFeel('DarkBrown')


class View:
    '''
    TODO
    '''

    def __init__(self, *args, **kwargs) -> None:
        self.window = sg.Window(*args, **kwargs).Finalize()

    def handle_events(self, event: Any, _: dict) -> bool:  # _ = values
        '''
        TODO
        '''

        if event == sg.WIN_CLOSED:
            return False

        return True

    def run(self) -> None:
        '''
        TODO
        '''

        while True:
            event, values = self.window.Read()
            if not self.handle_events(event, values):
                break

        self.on_close()

    def on_close(self) -> None:
        '''
        TODO
        '''

        self.window.close()

    def enable(self) -> None:
        '''
        TODO
        '''

        self.window.Enable()

    def disable(self) -> None:
        '''
        TODO
        '''

        self.window.Disable()
