import os


def get_dev_null():
    return open(os.devnull, 'w')
