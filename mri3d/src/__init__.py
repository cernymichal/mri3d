'''
TODO
'''

from dataclasses import dataclass
from .volume import Volume
from .parsedicom import Patient, Series


@dataclass
class ApplicationState:
    '''
    TODO
    '''

    volume: Volume
    patient: Patient
    series: Series
