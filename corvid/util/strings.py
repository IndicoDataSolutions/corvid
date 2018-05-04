"""

Miscellaneous functions for performing operations on strings

"""

import re

from typing import List


def tokenize(s: str) -> List[str]:
    """Standard function for string tokenization used throughout this module"""
    pass


# TODO: clean up syntax/style
def format_grid(grid: List[List[str]]) -> str:
    """
    e.g.
    input: [['a', 'b', 'c'], ['d', 'e', 'f']]
    output: 'a\tb\tc\nd\te\tf'
    printed:
    >    a   b   c
    >    d   e   f

    Source: https://stackoverflow.com/questions/13214809/pretty-print-2d-python-list"""
    if any([len(row) != len(grid[0]) for row in grid]):
        raise Exception('Grid missing entries (i.e. different row lengths)')
    g = [[cell if len(cell) > 0 else ' ' for cell in row] for row in grid]
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
    return len(re.findall(pattern=r'[a-zA-Z]', string=s)) > 0
    # return re.search(pattern=r'[a-z,A-Z]', string=s) is not None


def remove_non_alphanumeric(s: str) -> str:
    return re.sub(r'[^A-Za-z0-9]+', '', s)


def is_like_citation(s: str) -> bool:
    s = s.replace(' ', '').lower()
    if len(s) < 1:
        return False
    is_begins_capitalized = s[0].isupper()
    is_contains_et_al = 'etal' in s
    is_contains_year_in_parentheses = re.search(r'\([1-2][0-9]{3}\)',
                                                s) is not None
    is_contains_year_in_brackets = re.search(r'\[[1-2][0-9]{3}\]',
                                             s) is not None
    is_contains_reference_brackets = re.search(r'\[[0-9]*\]', s) is not None
    is_contains_year = re.search(r'[1-2][0-9]{3}', s) is not None
    return is_contains_et_al or \
           (is_begins_capitalized and is_contains_year_in_parentheses) or \
           (is_begins_capitalized and is_contains_year_in_brackets) or \
           (is_begins_capitalized and is_contains_reference_brackets) or \
           (is_begins_capitalized and is_contains_year)


def is_like_result(s: str) -> bool:
    s = s.strip()
    is_one_or_zero = s == '1' or s == '0'
    is_contains_float = re.search(r'[0-9]*\.[0-9]*', s) is not None
    is_contains_digit_percentage = re.search(r'[0-9]\%', s) is not None
    is_only_number_symbol = not is_contains_alpha(s)
    return is_one_or_zero or \
           (is_only_number_symbol and is_contains_float) or \
           (is_only_number_symbol and is_contains_digit_percentage)
