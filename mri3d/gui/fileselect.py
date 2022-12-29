'''
popup to select a file or a folder
'''

from pathlib import Path
import PySimpleGUI as sg
from . import TITLE


def create(title: str = TITLE, text: str = "Select a file", file_types: tuple = sg.FILE_TYPES_ALL_FILES, folder=False) -> Path:
    '''
    creates a file select window
    - existence of path is not checked
    - return None on cancel or empty input
    '''

    layout = [[sg.VPush()],
              [sg.Push(),
               sg.Column([[sg.Text(text, justification="right")],
                          [sg.InputText(size=(40, 1), key="-path-"),
                           sg.FolderBrowse(target="-path-") if folder else sg.FileBrowse(target="-path-", file_types=file_types)],
                          [sg.Button("Cancel"), sg.Button("Ok")]],
                         element_justification="c"),
               sg.Push()],
              [sg.VPush()]]

    window = sg.Window(title, layout, size=(390, 120))

    ok = False

    while True:
        event, values = window.read()
        if event in (sg.WIN_CLOSED, "Ok", "Cancel"):
            ok = event == "Ok" and values["-path-"] != ""
            break

    window.close()

    return Path(window["-path-"].get()) if ok else None
