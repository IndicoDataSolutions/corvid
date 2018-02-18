"""

Miscellaneous functions for performing operations on strings

"""

import os
import re

from typing import List
import string


def canonicalize_path(path: str):
    """Converts a path string to its canonical form (easier for comparisons)"""
    return os.path.abspath(os.path.realpath(os.path.expanduser(path)))


def format_list(l: List[str]) -> str:
    """
    e.g.
    input: ['This', 'is', 'a', 'sentence', '.', 'That', 'is', 'too', '.']
    output: "This is a sentence . That is too ."

    """
    return ' '.join(l)


# TODO: clean up syntax/style
def format_grid(grid: List[List[str]]) -> str:
    """
    e.g.
    input: [['a', 'b', 'c'], ['d', 'e', 'f']]
    output: 'a\tb\t\c\nd\te\tf'
    printed:
    >    a   b   c
    >    d   e   f

    Source: https://stackoverflow.com/questions/13214809/pretty-print-2d-python-list"""
    if any([len(row) != len(grid[0]) for row in grid]):
        raise Exception('Grid missing entries (i.e. different row lengths)')
    g = [[cell for cell in row] for row in grid]
    lens = [max(map(len, col)) for col in zip(*g)]
    fmt = '\t'.join('{{:{}}}'.format(x) for x in lens)
    return '\n'.join([fmt.format(*row) for row in g])


def is_floatable(s: str) -> bool:
    try:
        float(s)
        return True
    except ValueError:
        return False


def is_contains_alpha(s: str) -> bool:
    return len(re.findall(pattern=r'[a-z,A-Z]', string=s)) > 0
