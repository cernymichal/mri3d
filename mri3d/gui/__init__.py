'''
mri3d gui components module
'''

from __future__ import annotations
from typing import Any
import os
import sys
import PySimpleGUIQt as sg
from .icon import ICON_HEAD


TITLE = 'mri3d'
ICON = ICON_HEAD

DISABLED_BUTTON_COLORS = ('white', 'gray')


os.environ["QT_API"] = "pyside2"

sg.ChangeLookAndFeel('DarkBrown')
sg.SetOptions(icon=ICON)

# This bit gets the taskbar icon working properly in Windows
# https://github.com/PySimpleGUI/PySimpleGUI/issues/2722#issuecomment-852923088
if sys.platform.startswith('win'):
    import ctypes
    # Make sure Pyinstaller icons are still grouped
    if not sys.argv[0].endswith('.exe'):
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
            'CompanyName.ProductName.SubProduct.VersionInformation')


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

    def set_title(self, title: str = TITLE) -> View:
        '''
        sets the window title
        '''

        self.window.QT_QMainWindow.setWindowTitle(title)


def popup_error(message: str) -> None:
    '''
    popup an error message
    '''

    sg.PopupError(message)
