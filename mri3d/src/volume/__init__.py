'''
TODO
'''

from __future__ import annotations
import numpy as np
import open3d as o3d


class Volume:
    '''
    TODO
    '''

    def __init__(self, data: np.ndarray, spacing: tuple[float], value_range: tuple[float, float]):
        self.data = data
        self.spacing = spacing
        self.value_range = value_range

    def rotate90(self, axis: int, k: int = 1) -> Volume:
        axes = ((1, 2), (2, 0), (0, 1))[axis]
        self.data = np.rot90(self.data, k=k, axes=axes)

        if k % 2 == 1:
            new_spacing = list(self.spacing)
            new_spacing[axes[0]], new_spacing[axes[1]
                                              ] = new_spacing[axes[1]], new_spacing[axes[0]]
            self.spacing = tuple(new_spacing)

        return self

    def to_point_cloud(self) -> o3d.geometry.PointCloud:
        cloud = o3d.geometry.PointCloud()

        represented_values = self.value_range[1] - self.value_range[0]

        points = np.indices(self.data.shape).reshape(
            (3, self.data.size)).T * self.spacing
        colors = np.tile(np.vectorize(lambda x: (
            x - self.value_range[0]) / represented_values)(self.data).flatten(), (3, 1)).T

        cloud.points = o3d.utility.Vector3dVector(points)
        cloud.colors = o3d.utility.Vector3dVector(colors)

        return cloud

    def __str__(self):
        return f'Volume{self.data.shape} with spacing {self.spacing}'
