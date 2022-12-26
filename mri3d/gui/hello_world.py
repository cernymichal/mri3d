'''
a simple hello world window
'''

import PySimpleGUI as sg


def open() -> None:
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
        if event == sg.WIN_CLOSED or event == 'Ok':
            break

    window.close()
