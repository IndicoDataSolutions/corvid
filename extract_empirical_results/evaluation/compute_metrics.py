"""



"""

from extract_empirical_results.types.semantic_table import SemanticTable
from extract_empirical_results.types.table import Table
from typing import Dict

def _isRowInGoldTable(row, gold_table: Table):
    max_match = 0
    
    for gold_row_idx, gold_row in enumerate(gold_table.grid):
        if gold_row_idx == 0:
            continue
        match_count = 0
        for gold_col_idx, gold_cell in enumerate(gold_table.grid[gold_row_idx]):
            #skip subject column
            if gold_col_idx == 0:
                continue
            if str(gold_cell) in str(row):
                match_count += 1
                
        if match_count > max_match:
            max_match = match_count

        if match_count == (len(row)-1):
            return True


def compute_metrics(gold_table: Table,
                    aggregate_table: Table) -> Dict[str, float]:
    """
        computes accuracy for: reproducing the target schema, reproducing the gold table
    """

    schema_match_count  = 0
    row_match_count     = 0

    for row_idx, row in enumerate(aggregate_table.grid):
        if row_idx == 0:
            for col_idx, cell in enumerate(aggregate_table.grid[row_idx]):
                #Skip the subject column
                if col_idx == 1:
                    continue
                if str(cell) in str(gold_table.grid[0]):
                    schema_match_count += 1
        elif _isRowInGoldTable(row, gold_table):
            row_match_count += 1

    schema_match_accuracy = (schema_match_count / (gold_table.ncol -1) ) * 100
    table_match_accuracy = (row_match_count / (gold_table.nrow - 1) ) * 100

    print ('Schema Match Accuracy: ' + str(schema_match_accuracy))
    print ('Table Match Accuracy (Exact): ' + str(table_match_accuracy))

    return (schema_match_accuracy,table_match_accuracy)
