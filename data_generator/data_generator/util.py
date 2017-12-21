
import os

from typing import List

from copy import deepcopy

def canonicalize_path(path: str):
    """Converts a path string to its canonical form (easier for comparisons)"""
    return os.path.abspath(os.path.realpath(os.path.expanduser(path)))


# TODO: clean up syntax/style
def format_matrix(matrix: List[List[str]]) -> str:
    """Source: https://stackoverflow.com/questions/13214809/pretty-print-2d-python-list"""
    if any([len(row) != len(matrix[0]) for row in matrix]):
        raise Exception('Matrix missing entries (i.e. different row lengths)')
    m = deepcopy(matrix)
    lens = [max(map(len, col)) for col in zip(*m)]
    fmt = '\t'.join('{{:{}}}'.format(x) for x in lens)
    table = [fmt.format(*row) for row in m]
    return '\n'.join(table)
