'''
TODO
'''

import gui.dicomdir
from src import parsedicom


def main():
    '''
    app entrypoint
    '''
    dicomdir_path = gui.dicomdir.get_dicomdir()
    if dicomdir_path is None:
        return

    dcm = parsedicom.Dataset(dicomdir_path)

    series = gui.dicomdir.choose_series(dcm)

    images = parsedicom.get_images(series)
    volume = parsedicom.get_volume(images, dcm)

    print(volume)


main()
