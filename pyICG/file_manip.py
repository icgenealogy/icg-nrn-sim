'''
Helper functions for manipulating files in python
Written by Christopher Currin
'''

# coding=utf-8
import os
import shutil
from datetime import datetime


def create_dir(path, root=None, timestamp=None):
    """

    :param path:
    :param root:
    :param timestamp:
    :return: path of created directory
    """
    try:
        os.makedirs(path)
    except OSError:
        if not os.path.isdir(path):
            raise
    return path


def copy_file(src, dest):
    """

    :param src:
    :param dest:
    """
    # From shutil docs:
    #   If dest is a directory, a file with the same basename as
    #   src is created (or overwritten) in the directory specified.
    try:
        shutil.copy(src, dest)
    # eg. src and dest are the same file
    except shutil.Error as e:
        print('Error: %s' % e)
    # eg. source or destination doesn't exist
    except IOError as e:
        print('Error: %s' % e.strerror)


def move_file(src, dest):
    """

    :param src:
    :param dest:
    """
    try:
        copy_file(src, dest)
    except:
        print("error copying file")
    finally:
        os.remove(src)


def log(file, text):
    """

    :param file:
    :param text:
    :return:
    """
    file.write(text + "\n")
    try:
        print(text)
    except IOError:
        file.write("IOError: {}".format(IOError.message))


class cd(object):
    """Context manager for changing the current working directory"""

    def __init__(self, new_path):
        self.new_path = os.path.expanduser(new_path)

    def __enter__(self):
        self.savedPath = os.getcwd()
        os.chdir(self.new_path)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.savedPath)
