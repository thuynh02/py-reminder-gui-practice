import os
import sys


def trim_extension(filename):
    return filename.lower().rsplit(".", 1)[0]


def resource_path(relative_path, relative_to=os.path.abspath(__file__)):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, "_MEIPASS", os.path.dirname(relative_to))
    return os.path.join(base_path, relative_path)
