"""


"""

from typing import List, Dict

import numpy as np

from corvid.semantic_table.table import Table


class SemanticTable(object):
    VALID_LABELS = ['metric', 'method', 'dataset', 'value', 'other', 'empty']

    def __init__(self, table: Table):
        self.table = table
        self.labels = self._classify_cells()
        self.tuples = self._get_tuples()

    # TODO: implement
    def _classify_cells(self) -> List[str]:
        pred = []
        for cell in self.table.cells:
            pred.append(np.random.choice(SemanticTable.VALID_LABELS, size=1))
        return pred

    # TODO: implement
    def _get_tuples(self) -> List[Dict]:
        tuples = []
        for cell, label in zip(self.table.cells, self.labels):
            tuple = {}
            if label == 'value':
                tuple['value'] = str(cell)
            tuples.append(tuple)
        return tuples

