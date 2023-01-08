"""
Test mri3d.gui
"""

# pylint: disable=redefined-outer-name

import os
import pytest
from mri3d import gui


# TODO numba fails in test environment
IN_CI = 'IN_CI' in os.environ


# series options mock data
#
# patients_labels = ["a", "b"]
# studies_labels = [["1", "2"], ["3", "4"]][indices[0]]
# series_labels = [[["1a", "1b"], ["2a", "2b"]], [["3a", "3b"], ["4a", "4b"]]][indices[0]][indices[1]]

# dicomdir.py
# TODO _get_options https://stackoverflow.com/questions/6383914/is-there-a-way-to-instantiate-a-class-without-calling-init
# TODO get_chosen_values

# exporter.py
# TODO StateView.title_str
# TODO StateView.patient_str
# TODO StateView.series_str
# TODO StateView.resolution_str
# TODO StateView.normalized_str

# TODO MainView.handle_events
# TODO MainView.rotate
# TODO MainView.resample
# TODO MainView.normalize
# TODO MainView.save_to_tiff
# TODO MainView.save_to_vox
