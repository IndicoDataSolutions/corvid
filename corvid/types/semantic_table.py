"""

The SemanticTable class adds semantic representation of tables on top of
the physical representation in the Table class

"""

from typing import List

from corvid.types.table import Table


class SemanticTable(object):
    """A SemanticTable is a semantic representation of a physical Table.

    It provides additional semantic features, including:
        - class labels for whether a Cell serves a 'LABEL' or 'VALUE' purpose
        -

    """

    VALID_CELL_CLASSES = ['LABEL', 'VALUE']

    def __init__(self, table: Table):
        self.cell_classes = self._classify_cells(table)
        if self._should_transpose(table):
            table = table.transpose()
        self.table = self._normalize(table)

    def _classify_cells(self, table: Table) -> List[str]:
        raise NotImplementedError

    def _should_transpose(self, table: Table) -> bool:
        raise NotImplementedError

    def _normalize(self, table: Table) -> Table:
        raise NotImplementedError
