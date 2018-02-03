import os
import re

from typing import List
import string


def canonicalize_path(path: str):
    """Converts a path string to its canonical form (easier for comparisons)"""
    return os.path.abspath(os.path.realpath(os.path.expanduser(path)))


def format_list(l: List[str]) -> str:
    text = ''
    for s in l:
        if s in string.punctuation:
            text += s
        else:
            text += ' ' + s
    return text


# TODO: clean up syntax/style
def format_matrix(matrix: List[List[str]]) -> str:
    """Source: https://stackoverflow.com/questions/13214809/pretty-print-2d-python-list"""
    if any([len(row) != len(matrix[0]) for row in matrix]):
        raise Exception('Matrix missing entries (i.e. different row lengths)')
    m = [[cell for cell in row] for row in matrix]
    lens = [max(map(len, col)) for col in zip(*m)]
    fmt = '\t'.join('{{:{}}}'.format(x) for x in lens)
    table = [fmt.format(*row) for row in m]
    return '\n'.join(table)


def is_floatable(s: str) -> bool:
    try:
        f = float(s)
        return True
    except ValueError:
        return False


def is_contains_alpha(s: str) -> bool:
    return len(re.findall(pattern=r'[a-z,A-Z]', string=s)) > 0
