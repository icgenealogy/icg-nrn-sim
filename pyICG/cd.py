import os

class cd:
    """Context manager for changing the current working directory"""
    def __init__(self, newPath):
        self.newPath = os.path.expanduser(newPath)

    def __enter__(self):
        self.savedPath = os.getcwd()
        os.chdir(self.newPath)
        print("in " + os.getcwd())

    def __exit__(self, etype, value, traceback):
        print("out " + os.getcwd())
        os.chdir(self.savedPath)
        print("in " + os.getcwd())
