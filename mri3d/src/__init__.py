'''
module for holding other dependancies
'''

from dataclasses import dataclass
from .volume import Volume
from .parsedicom import Patient, Series


@dataclass
class ApplicationState:
    '''
    application state holder
    '''

    volume: Volume
    patient: Patient
    series: Series
