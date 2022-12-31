'''
TODO
'''

from typing import Any
from PySide2.QtWidgets import QVBoxLayout
from pyvistaqt import QtInteractor
import pyvista as pv
from src.volume import Volume

OPACITY_TRANSFER_LINEAR = 'linear'
OPACITY_TRANSFER_SIGMOID = 'sigmoid'
OPACITY_TRANSFER_SEETHROUGH = [0, 0, .1]
SCALAR_BAR_ARGS = {'title': '', 'label_font_size': 14, 'fmt': ' % .3f'}


class VolumePlotter(QtInteractor):
    '''
    TODO
    '''

    def __init__(self, *args, background_color: Any = 'black', opacity_transfer: Any = None, **kwargs):
        QtInteractor.__init__(self, *args, **kwargs)
        self.set_background(background_color)
        # plotter.enable_anti_aliasing()
        self.show_axes()

        if opacity_transfer is None:
            opacity_transfer = OPACITY_TRANSFER_SEETHROUGH

        self.opacity_transfer = opacity_transfer

    @classmethod
    def get_ugrid_from_volume(cls, volume: Volume) -> pv.UniformGrid:
        '''
        TODO
        '''

        grid = pv.UniformGrid()
        grid.dimensions = volume.data.shape
        grid.spacing = volume.spacing
        grid.point_data['values'] = volume.data.flatten(order='F')
        return grid

    def plot_volume(self, volume: Volume, cmap='bone', show_scalar_bar=False) -> None:
        '''
        TODO
        '''

        ugrid = self.get_ugrid_from_volume(volume)

        self.remove_bounding_box()
        self.clear_actors()
        self.view_isometric()
        self.add_volume(ugrid, clim=volume.value_range, cmap=cmap, opacity=self.opacity_transfer,
                        show_scalar_bar=show_scalar_bar, scalar_bar_args=SCALAR_BAR_ARGS)
        self.add_bounding_box(color='white')

    def hook_widget(self, vbox_layout: QVBoxLayout) -> None:
        '''
        TODO
        '''

        vbox_layout.addWidget(self.interactor)
