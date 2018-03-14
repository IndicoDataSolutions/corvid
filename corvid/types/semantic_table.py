"""

The SemanticTable class adds semantic representation of tables on top of
the physical representation in the Table class

"""

from typing import List

from corvid.types.table import Cell, Table
from corvid.util.strings import is_floatable


class SemanticTable(object):
    """A SemanticTable is a semantic representation of a physical Table.

    It provides additional semantic features, including:
        * class labels for whether a Cell serves a 'LABEL' or 'VALUE' purpose
        *

    """

    VALID_CELL_CLASSES = ['LABEL', 'VALUE']

    def __init__(self, table: Table):
        self.cell_classes = self._classify_cells(table)
        if self._should_transpose(table):
            table = table.transpose()
        self.table = self._normalize(table)

    @property
    def schema(self) -> List[Cell]:
        return self.table[0, :]

    @property
    def subjects(self) -> List[Cell]:
        return self.table[:, 0]

    def _classify_cells(self, table: Table) -> List[List[str]]:
        cell_classes = [['' for _ in range(table.ncol)]
                        for _ in range(table.nrow)]
        visited_cells = set()
        for i in range(table.nrow):
            for j in range(table.ncol):
                cell = table[i, j]
                if cell not in visited_cells:
                    cell_classes[i, j] = SemanticTable._classify_cell(cell)
                    visited_cells.add(cell)

        for row in cell_classes:
            for cell in row:
                if cell not in SemanticTable.VALID_CELL_CLASSES:
                    raise Exception('Cells must belong to one of {} classes'
                                    .format(SemanticTable.VALID_CELL_CLASSES))

        return cell_classes

    @classmethod
    def _classify_cell(cls, cell: Cell) -> str:
        if all([is_floatable(token) for token in cell.tokens]):
            return 'VALUE'
        return 'LABEL'

    def _should_transpose(self, table: Table) -> bool:
        raise NotImplementedError

    # TODO: (1) pad if missing headers; (2) collapse
    def _normalize(self, table: Table) -> Table:
        raise NotImplementedError
