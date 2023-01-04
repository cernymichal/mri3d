'''
TODO
'''

from typing import Any
from PySide2.QtWidgets import QVBoxLayout
from pyvistaqt import QtInteractor
import pyvista as pv
from src.volume import Volume
from . import View

OPACITY_TRANSFER_LINEAR = 'linear'
OPACITY_TRANSFER_SIGMOID = 'sigmoid'
OPACITY_TRANSFER_SEETHROUGH = [0, 0, .1]
SCALAR_BAR_ARGS = {'title': '', 'label_font_size': 14, 'fmt': ' % .3'}


class VolumePlotter(QtInteractor):
    '''
    TODO
    '''

    def __init__(self, *args, background_color: Any = 'black', border_color: Any = None, opacity_transfer: Any = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_background(background_color)
        if border_color is not None:
            self.renderer.add_border(border_color, width=2.0)
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


class ViewWithVolumePlot(View):
    '''
    TODO
    '''

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.plotter = None

    def add_plotter(self, *args, column_key: str = '-plot-', **kwargs) -> None:
        '''
        TODO
        '''

        self.plotter = VolumePlotter(
            self.window.QT_QMainWindow, *args, **kwargs)
        self.plotter.hook_widget(self.window[column_key].vbox_layout)

    def remove_plotter(self) -> None:
        '''
        TODO
        '''

        if self.plotter is not None:
            self.plotter.close()
            self.plotter = None

    def on_close(self) -> None:
        '''
        TODO
        '''

        if self.plotter is not None:
            self.plotter.close()
        super().on_close()

    def enable(self) -> None:
        '''
        TODO
        '''

        super().enable()
        if self.plotter is not None:
            self.plotter.enable()

    def disable(self) -> None:
        '''
        TODO
        '''

        if self.plotter is not None:
            self.plotter.disable()
        super().disable()
