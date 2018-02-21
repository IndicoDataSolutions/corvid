"""

Methods to compute metrics to evaluate schema matching 
and table aggregation against gold tables and gold  
schema

"""

from corvid.types.semantic_table import SemanticTable
from corvid.types.table import Cell, Table

from typing import Dict, List


def _compute_number_matching_cells(row1: List[Cell], row2: List[Cell]) -> int:
    """Returns the number of matching cells between two rows of equal length"""
    if len(row1) != len(row2):
        raise Exception('Unequal number of cells in each row')
    match_count = 0
    for cell1 in row1:
        for cell2 in row2:
            if str(cell1) == str(cell2):
                match_count += 1
                break
    return match_count


def _get_best_match_in_gold_table(row, gold_table: Table) -> float:
    """
        Computes match scores between each row of the gold table and the row
        and returns the highest match score
    """
    MAX_MATCH_SCORE = 1.0
    max_match = 0.0
    # Skip header row by looping from row 1
    for gold_row in gold_table.grid[1:]:
        # Skip the subject column when checking for matches; Assumes subject column is column 0
        match_count = _compute_number_matching_cells(row[1:], gold_row[1:])
        match_score = match_count / (gold_table.ncol - 1)

        if match_score == MAX_MATCH_SCORE:
            return match_score

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
    schema_match_count = 0
    row_exact_match_score = 0  # aggregates match_score for rows with exact matches
    overall_match_score = 0  # aggregates match_score for rows with exact and partial matches

    # Row 0 is assumed to be header row. It is evaluated only for schema match
    # It is omitted from row-level and cell-level table evaluations
    # Skip the subject column when checking for matches; Assumes subject column is column 0
    aggregate_table_schema = aggregate_table.grid[0][1:]
    gold_table_schema = gold_table.grid[0][1:]

    schema_match_count = _compute_number_matching_cells(aggregate_table_schema, gold_table_schema)
    schema_match_accuracy = (schema_match_count / (gold_table.ncol - 1)) * 100

    for aggregate_table_row in aggregate_table.grid[1:]:
        match_score = _get_best_match_in_gold_table(aggregate_table_row,
                                                    gold_table)

        if match_score == 1:
            row_exact_match_score += match_score

        overall_match_score += match_score

    table_match_accuracy_row_level = (row_exact_match_score / (gold_table.nrow - 1)) * 100
    table_match_accuracy_cell_level = round((overall_match_score / (gold_table.nrow - 1)) * 100, 2)

    print('Schema Match Accuracy: ' + str(schema_match_accuracy))
    print('Table Match Accuracy (Row level): ' + str(
        table_match_accuracy_row_level))
    print('Table Match Accuracy (Cell level): ' + str(
        table_match_accuracy_cell_level))

    metric_scores['schema_match_accuracy'] = schema_match_accuracy
    metric_scores['table_match_accuracy_exact'] = table_match_accuracy_row_level
    metric_scores['table_match_accuracy_inexact'] = table_match_accuracy_cell_level

    return metric_scores
