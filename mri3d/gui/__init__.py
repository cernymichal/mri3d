'''
mri3d gui components module
'''

import os
import PySimpleGUIQt as sg

TITLE = 'mri3d'
ICON = sg.DEFAULT_WINDOW_ICON

os.environ["QT_API"] = "pyside2"
sg.ChangeLookAndFeel('DarkBrown')
