'''
TODO
'''

import gui.dicomdir
from src import parsedicom
#import open3d as o3d


def main():
    '''
    app entrypoint
    '''
    dicomdir_path = gui.dicomdir.get_dicomdir()
    if dicomdir_path is None:
        # TODO add popup
        return

    dcm = parsedicom.Dataset(dicomdir_path)
    if not dcm.has_any_series():
        # TODO add popup
        return

    series = gui.dicomdir.choose_series(dcm)
    if series is None:
        # TODO add popup
        return

    images = parsedicom.get_images(series)
    volume = parsedicom.get_volume(images, dcm) # TODO error check

    print(volume.rotate90(1, 1))

    print("generating point cloud")
    cloud = volume.to_point_cloud()
    print("done")
    print(cloud)
    #o3d.visualization.draw_geometries([cloud])


main()
