"""

Handles building of Tables from inputs other than `grid` or `cells`.
Builder design chosen because easier to work with when start subclassing Cell
and Table as opposed to needing to override @classmethods

"""

from typing import Callable, Dict

from corvid.semantic_table.table import Cell, Table


class CellBuilder(object):
    REQUIRED_KEYS = ['tokens', 'index_topleft_row', 'index_topleft_col',
                     'rowspan', 'colspan']

    def __init__(self, cell_type: Callable[..., Cell]):
        self.cell_type = cell_type

    def from_json(self, json: Dict) -> Cell:
        kwargs = {k: v for k, v in json.items() if k not in self.REQUIRED_KEYS}
        cell = self.cell_type(tokens=json['tokens'],
                              index_topleft_row=json['index_topleft_row'],
                              index_topleft_col=json['index_topleft_col'],
                              rowspan=json['rowspan'],
                              colspan=json['colspan'],
                              **kwargs)
        return cell


class TableBuilder(object):
    REQUIRED_KEYS = ['cells', 'nrow', 'ncol']

    def __init__(self,
                 table_type: Callable[..., Table],
                 cell_builder: CellBuilder):
        self.table_type = table_type
        self.cell_builder = cell_builder

    def from_json(self, json: Dict) -> Table:
        kwargs = {k: v for k, v in json.items() if k not in self.REQUIRED_KEYS}
        cells = [self.cell_builder.from_json(d) for d in json['cells']]
        table = self.table_type(cells=cells,
                                nrow=json['nrow'],
                                ncol=json['ncol'],
                                **kwargs)
        return table
