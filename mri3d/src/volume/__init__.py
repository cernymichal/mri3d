'''
TODO
'''

import numpy as np


class Volume:
    '''
    TODO
    '''
    def __init__(self, data: np.ndarray, spacing: tuple):
        self.data = data
        self.spacing = spacing

    def __str__(self):
        return f'Volume{self.data.shape} with spacing {self.spacing}'
