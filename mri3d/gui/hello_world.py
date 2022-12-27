'''
a simple hello world window
'''

import PySimpleGUI as sg


def create() -> None:
    '''
    creates a hello world window
    '''

    layout = [[sg.VPush()],
              [sg.Push(),
               sg.Column([[sg.Text('hello world! 🎉', font=(sg.DEFAULT_FONT[0], 24))],
                          [sg.Button('Ok')]],
                         element_justification='c'),
               sg.Push()],
              [sg.VPush()]]

    window = sg.Window('hello_world', layout, size=(400, 200))

    while True:
        event, values = window.read()
        if event in (sg.WIN_CLOSED, 'Ok'):
            break

    window.close()
