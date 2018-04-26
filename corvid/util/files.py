"""

Miscellaneous functions for working with files

"""

import os

import csv
import json


def canonicalize_path(path: str):
    """Converts a path string to its canonical form (easier for comparisons)"""
    return os.path.abspath(os.path.realpath(os.path.expanduser(path)))


def csv_to_json(csv_path: str, json_path: str):
    """Converts a CSV into a JSON (each row is a JSON object)"""
    with open(csv_path, 'r') as f_csv:
        out = list(csv.reader(f_csv))
    with open(json_path, 'w') as f_json:
        json.dump(out, f_json)
