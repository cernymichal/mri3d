'''
classes for Volume plotting in Qt
'''

from __future__ import annotations
from typing import Any
from PySide2.QtWidgets import QVBoxLayout
from pyvistaqt import QtInteractor
import pyvista as pv
from ..volume import Volume
from . import View

OPACITY_TRANSFER_LINEAR = 'linear'
OPACITY_TRANSFER_SIGMOID = 'sigmoid'
OPACITY_TRANSFER_SEETHROUGH = [0, 0, .1]
SCALAR_BAR_ARGS = {'title': '', 'label_font_size': 14, 'fmt': ' % .3'}


class VolumePlotter(QtInteractor):
    '''
    QtWidget wrapper for plotting a Volume onto a PySimpleGUIQt element
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
        returns pyvista.UniformGrid created from Volume
        '''

        grid = pv.UniformGrid()
        grid.dimensions = volume.data.shape
        grid.spacing = volume.spacing
        grid.point_data['values'] = volume.data.flatten(order='F')
        return grid

    def plot_volume(self, volume: Volume, cmap='bone', show_scalar_bar=False) -> VolumePlotter:
        '''
        reset and add a Volume to the plot scene

        returns self
        '''

        ugrid = self.get_ugrid_from_volume(volume)

        self.remove_bounding_box()
        self.clear_actors()
        self.view_isometric()
        self.add_volume(ugrid, clim=volume.value_range, cmap=cmap, opacity=self.opacity_transfer,
                        show_scalar_bar=show_scalar_bar, scalar_bar_args=SCALAR_BAR_ARGS)
        self.add_bounding_box(color='white')
        return self

    def hook_widget(self, vbox_layout: QVBoxLayout) -> VolumePlotter:
        '''
        hook this plotter to a Qt element

        returns self
        '''

        vbox_layout.addWidget(self.interactor)
        return self

    def close(self) -> None:
        # pylint doesn't see close() on super() for some reason
        QtInteractor.close(self)
        self.deep_clean()


class ViewWithVolumePlot(View):
    '''
    view with a single VolumePlotter element
    '''

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.plotter = None

    def add_plotter(self, *args, column_key: str = '-plot-', **kwargs) -> ViewWithVolumePlot:
        '''
        add the plotter to the windo, hooks on a element with column_key key

        returns self
        '''

        self.plotter = VolumePlotter(
            self.window.QT_QMainWindow, *args, **kwargs)
        self.plotter.hook_widget(self.window[column_key].vbox_layout)
        return self

    def remove_plotter(self) -> ViewWithVolumePlot:
        '''
        removes the plotter from the windo

        returns self
        '''

        if self.plotter is not None:
            self.plotter.close()
            self.plotter.deep_clean()
            self.plotter = None
        return self

    def on_close(self) -> None:
        if self.plotter is not None:
            self.plotter.close()
        super().on_close()

    def enable(self) -> ViewWithVolumePlot:
        super().enable()
        if self.plotter is not None:
            self.plotter.enable()
        return self

    def disable(self) -> ViewWithVolumePlot:
        if self.plotter is not None:
            self.plotter.disable()
        super().disable()
        return self
