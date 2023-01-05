'''
volume storage and operations with numpy
'''

from __future__ import annotations
import numpy as np


class Volume:
    '''
    holds volume in a numpy array
    '''

    def __init__(self, data: np.ndarray, spacing: tuple[float], value_range: tuple[float, float]):
        self.data = data
        self.spacing = spacing
        self.value_range = value_range

    def rotate90(self, axis: int, k: int = 1) -> Volume:
        '''
        rotate volume 90 degrees around axis k times, applies the right hand rule
        '''

        axes = ((1, 2), (2, 0), (0, 1))[axis]
        self.data = np.rot90(self.data, k=k, axes=axes)

        if k % 2 == 1:
            new_spacing = list(self.spacing)
            new_spacing[axes[0]], new_spacing[axes[1]
                                              ] = new_spacing[axes[1]], new_spacing[axes[0]]
            self.spacing = tuple(new_spacing)

        return self

    def __str__(self):
        return f'Volume{self.data.shape} with spacing {self.spacing}'
