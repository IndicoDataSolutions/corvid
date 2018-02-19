"""

Miscellaneous functions for working with files

"""

import os
from typing import List, Callable


def canonicalize_path(path: str):
    """Converts a path string to its canonical form (easier for comparisons)"""
    return os.path.abspath(os.path.realpath(os.path.expanduser(path)))


def scan_file_for_sections(filepath: str,
                           start_condition: Callable,
                           end_condition: Callable) -> List[List[str]]:
    """Returns contiguous lines between some start and end condition

    Example - Return lines that occur between <tag> and </tag> (inclusive):

        scan_file_for_sections(filepath: MYFILE,
                               start_condition: lambda l: '<tag>' in l
                               end_condition: lambda l: '</tag>' in l)
    """
    sections = []
    with open(filepath, 'r') as f:
        is_read = False
        for line in f:
            if start_condition(line):
                is_read = True
                section = []
            if is_read:
                section.append(line)
            if end_condition(line):
                is_read = False
                sections.append(section)
    return sections


