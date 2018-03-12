"""

Miscellaneous functions for performing operations on strings

"""

import re

from typing import List


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


def remove_non_alphanumeric(s: str) -> str:
    return re.sub('[^A-Za-z0-9]+', '', s)
