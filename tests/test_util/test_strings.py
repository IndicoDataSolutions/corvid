"""


"""

import unittest

from corvid.util.strings import format_grid

class TestStrings(unittest.TestCase):

    def test_format_grid(self):
        single = [['a']]
        self.assertEqual(format_grid(single).replace(' ', ''), 'a')

        row = [['a', 'b']]
        self.assertEqual(format_grid(row).replace(' ', ''), 'a\tb')

        col = [['a'], ['c']]
        self.assertEqual(format_grid(col).replace(' ', ''), 'a\nc')

        grid = [['a', 'b'], ['c', 'd']]
        self.assertEqual(format_grid(grid).replace(' ', ''), 'a\tb\nc\td')

        empty_single = [['']]
        self.assertEqual(format_grid(empty_single).replace(' ', ''), '')

        empty_row = [['', '']]
        self.assertEqual(format_grid(empty_row).replace(' ', ''), '\t')

        empty_col = [[''], ['']]
        self.assertEqual(format_grid(empty_col).replace(' ', ''), '\n')

        empty_grid = [['', ''], ['', '']]
        self.assertEqual(format_grid(empty_grid).replace(' ', ''), '\t\n\t')