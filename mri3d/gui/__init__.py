'''
mri3d gui components module
'''

from __future__ import annotations
from typing import Any
import os
import PySimpleGUIQt as sg

TITLE = 'mri3d'
ICON = sg.DEFAULT_WINDOW_ICON

os.environ["QT_API"] = "pyside2"
sg.ChangeLookAndFeel('DarkBrown')


class View:
    '''
    PySimpleGUIQt window wrapper
    '''

    def __init__(self, *args, **kwargs) -> None:
        self.window = sg.Window(*args, **kwargs).Finalize()

    def handle_events(self, event: Any, _: dict) -> bool:  # _ = values
        '''
        handle a user event

        returns if the event loop should continue
        '''

        if event == sg.WIN_CLOSED:
            return False

        return True

    def run(self) -> View:
        '''
        run window loop handeling user events

        returns self
        '''

        while True:
            event, values = self.window.Read()
            if not self.handle_events(event, values):
                break

        self.on_close()
        return self

    def on_close(self) -> None:
        '''
        called at the end of view.run()
        '''

        self.window.Close()

    def enable(self) -> View:
        '''
        enable window interaction

        returns self
        '''

        self.window.Enable()
        return self

    def disable(self) -> View:
        '''
        disable window interaction

        returns self
        '''

        self.window.Disable()
        return self
