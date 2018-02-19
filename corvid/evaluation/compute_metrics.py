"""



"""

from corvid.types.table import Table
from corvid.types.semantic_table import SemanticTable
from typing import Dict

def _is_row_in_gold_table(row, gold_table: Table) -> bool:
    """
        Searches for the first match of the row in the gold table; returns on success
    """
    
    for gold_row_idx, gold_row in enumerate(gold_table.grid):
        #Skip header row
        if gold_row_idx == 0:
            continue
        match_count = 0
        for gold_col_idx, gold_cell in enumerate(gold_row):
            #Skip subject column
            if gold_col_idx == 0:
                continue
            for cell in row:
                if str(cell) == str(gold_cell):
                    match_count += 1

        if match_count == (len(row)-1):
            return True

def _get_best_match_in_gold_table(row, gold_table: Table) -> float:
    """
        Computes match scores between each row of the gold table and the row
        and returns the match score with the best match
    """

    max_match = 0
    
    for gold_row_idx, gold_row in enumerate(gold_table.grid):
        #Skip header row
        if gold_row_idx == 0:
            continue
        match_count = 0
        for gold_col_idx, gold_cell in enumerate(gold_row):
            #Skip subject column
            if gold_col_idx == 0:
                continue
            for cell in row:
                if str(cell) == str(gold_cell):
                    match_count += 1

        if match_count > max_match:
            max_match = match_count

    match_score = max_match / gold_table.ncol

    return match_score


def compute_metrics(gold_table: Table,
                    aggregate_table: Table) -> Dict[str, float]:
    """
        Compute accuracy for: reproducing the target schema, reproducing the gold table
    """

    metric_scores = {}
    schema_match_count  = 0
    row_match_count     = 0 #aggregates row counts when a row exactly match with 
    match_score         = 0 #aggregates match_score for rows without exact matches

    for row_idx, aggregate_table_row in enumerate(aggregate_table.grid):
        #Row 0 is assumed to be header row and is evaluated 
        #only for schema match and is discounted from table row match
        if row_idx == 0:
            for col_idx, aggregate_table_cell in enumerate(aggregate_table_row):
                #Skip the subject column
                if col_idx == 1:
                    continue
                for gold_row_cell in gold_table.grid[0]:
                    if str(aggregate_table_cell) == str(gold_row_cell):
                        schema_match_count += 1
        elif _is_row_in_gold_table(aggregate_table_row, gold_table):
            row_match_count += 1
        else:
            match_score += _get_best_match_in_gold_table(aggregate_table_row, gold_table)

    schema_match_accuracy = (schema_match_count / (gold_table.ncol -1) ) * 100
    table_match_accuracy_row_level  = (row_match_count / (gold_table.nrow - 1) ) * 100
    table_match_accuracy_cell_level = round((match_score + row_match_count / (gold_table.nrow - 1) ) * 100, 2)

    print ('Schema Match Accuracy: ' + str(schema_match_accuracy))
    print ('Table Match Accuracy (Row level): ' + str(table_match_accuracy_row_level))
    print ('Table Match Accuracy (Cell level): ' + str(table_match_accuracy_cell_level))

    metric_scores['schema_match_accuracy']          =  schema_match_accuracy
    metric_scores['table_match_ccuracy_exact']      =  table_match_accuracy_row_level 
    metric_scores['table_match_ccuracy_inexact']    =  table_match_accuracy_cell_level

    return (metric_scores)
