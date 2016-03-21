import os
import re


def get_dev_null():
    return open(os.devnull, 'w')


def extract_addr(line):
    match = re.search(r'[\w\.-]+@[\w\.-]+', line)
    return match.group(0) if match else None
