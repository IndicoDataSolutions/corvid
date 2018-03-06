"""

Compute evaluation metrics between `pred` and `gold` Tables

"""

from typing import Dict, List, Callable

import numpy as np
from scipy.optimize import linear_sum_assignment

from corvid.types.semantic_table import SemanticTable
from corvid.types.table import Cell, Table
from corvid.util.lists import compute_similarity


def _count_matching_cells(row1: List[Cell], row2: List[Cell]) -> float:
    """Count the number of matching cells between two rows of Cells,
    assuming their columns are aligned.
    """
    if len(row1) != len(row2):
        print('Row 1: ' + str(row1))
        print('Row 2: ' + str(row2))
        raise Exception('Unequal number of cells in each row')

    return compute_similarity(
        x=row1,
        y=row2,
        sim=lambda cell1, cell2: int(str(cell1) == str(cell2)),
        agg=sum)


def _row_level_recall(gold_table: Table, pred_table: Table) -> int:
    """Computes normalized count of rows in `gold` reproduced in `pred`

    For example:

    gold =  1, 2, 3         pred =  1, 2, 4
            4, 5, 6                 4, 5, 6
                                    7, 8, 9

    returns 1/2 = 0.5

    * Assumes `gold` and `pred` Tables have the same (ordered) schema
    * Dont evaluate on the `header` or (`0`th) row for each Table
    * Dont evaluate on the `subject` (or `0`th) column for each Table
    """

    max_match_count = gold_table.ncol - 1

    row_match_count = 0
    row_match_indices = set()

    for gold_row in gold_table[1:, :]:
        for index_pred_row, pred_row in enumerate(pred_table[1:, :]):

            is_row_match = _count_matching_cells(
                row1=gold_row[1:], row2=pred_row[1:]) == max_match_count
            is_available = index_pred_row not in row_match_indices

            if is_available and is_row_match:
                row_match_count += 1
                row_match_indices.add(index_pred_row)

    return row_match_count / (gold_table.nrow - 1)


def _cell_level_recall(gold_table: Table, pred_table: Table) -> float:
    """Computes normalized count of cells in `gold` reproduced in `pred`

    For example:

    gold =  1, 2, 3         pred =  1, 2, 4
            4, 5, 6                 4, 5, 6
                                    7, 8, 9

    returns 5/6 = 0.67

    * Assumes `gold` and `pred` Tables have the same (ordered) schema
    * Dont evaluate on the `header` or (`0`th) row for each Table
    * Dont evaluate on the `subject` (or `0`th) column for each Table

    * The search to match rows in `gold` to rows in `pred` such that
    their sum total of matching cells is maximized can be solved via
    the Hungarian algorithm (aka Kuhn-Munkres).  See
    https://docs.scipy.org/doc/scipy-0.18.1/reference/generated/scipy.optimize.linear_sum_assignment.html
    """

    cell_match_counts = np.array([
        [
            _count_matching_cells(row1=gold_row[1:], row2=pred_row[1:])
            for pred_row in pred_table[1:, :]
        ]
        for gold_row in gold_table[1:, :]
    ])

    # negative sign here because scipy implementation minimizes sum of weights
    index_gold, index_pred = linear_sum_assignment(-1.0 * cell_match_counts)

    return cell_match_counts[index_gold, index_pred].sum() / \
           ((gold_table.nrow - 1) * (gold_table.ncol - 1))


# TODO: link to documentation that describes formulas for each of these
def compute_metrics(gold_table: Table, pred_table: Table) -> Dict[str, float]:
    """Computes all evaluation metrics between a `pred` and `gold` Table pair"""

    return {
        'row_level_recall': _row_level_recall(gold_table, pred_table),
        'cell_level_recall': _cell_level_recall(gold_table, pred_table)
    }
