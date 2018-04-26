"""

Evaluates predicted (i.e. extracted) Tables against gold Tables

"""

from typing import Dict, Callable

from corvid.types.table import Table
from corvid.util.strings import remove_non_alphanumeric
from corvid.util.lists import compute_intersection, compute_union


def is_same_dimensions(gold: Table, pred: Table) -> bool:
    return pred.shape == gold.shape


def bag_of_cells_iou(gold: Table, pred: Table) -> float:
    """Computes Intersection over Union (IOU) between `gold` and `pred`
    Tables where each Table is treated like a Bag of Cells"""

    pass


def cell_level_grid_accuracy(gold: Table, pred: Table,
                             sim: Callable, agg: Callable) -> float:
    """"""
    if not is_same_dimensions(pred, gold):
        raise Exception('Cant compare tables of different dimensions')

    return agg([sim(gold[i, j], pred[i, j])
                for i in range(gold.nrow)
                for j in range(gold.ncol)]) / (gold.nrow * gold.ncol)


def evaluate(gold_table: Table, pred_table: Table) -> Dict[str, float]:
    """Computes all evaluation metrics between a `gold` and `pred` Table pair"""

    if not is_same_dimensions(gold_table, pred_table):
        raise Exception('`gold` and `pred` requires identical dimensions')

    return {
        'cell_level_grid_accuracy': cell_level_grid_accuracy(
            gold_table,
            pred_table,
            sim=lambda cell1, cell2: remove_non_alphanumeric(str(cell1)) == \
                                     remove_non_alphanumeric(str(cell2)),
            agg=sum
        )
    }
