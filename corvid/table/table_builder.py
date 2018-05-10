"""

Handles building of Tables from inputs other than `grid` or `cells`.
Builder design chosen because easier to work with when start subclassing Cell
and Table as opposed to needing to override @classmethods

"""

from typing import Callable, Dict, List

from corvid.table.table import Cell, Table


class CellBuilder(object):
    def __init__(self,
                 cell_type: Callable[..., Cell]):
        self.cell_type = cell_type

    def from_json(self, json: Dict) -> Cell:
        cell = self.cell_type(**json)
        return cell


class TableBuilder(object):
    def __init__(self,
                 table_type: Callable[..., Table],
                 cell_builder: CellBuilder):
        self.table_type = table_type
        self.cell_builder = cell_builder

    def from_json(self, json: Dict) -> Table:
        cells = [self.cell_builder.from_json(d) for d in json['cells']]
        kwargs = {k: v for k, v in json.items() if k not in 'cells'}
        table = self.table_type(cells=cells, **kwargs)
        return table
