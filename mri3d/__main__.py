'''
TODO
'''

import gui.dicomdir
import gui.main_view
from src import parsedicom


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
    volume = parsedicom.get_volume(images, dcm)  # TODO error check

    gui.main_view.create(volume)


main()
