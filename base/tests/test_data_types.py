"""


"""

import unittest
from base.data_types import Cell, Table


class TestCell(unittest.TestCase):
    def test_default(self):
        c = Cell()
        self.assertEqual(c.text, '')
        self.assertEqual(c.colspan, 1)


class TestTable(unittest.TestCase):
    def test_pass(self):
        self.assertTrue(True)
