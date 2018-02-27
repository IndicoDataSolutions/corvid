"""

Methods to compute metrics to evaluate schema matching 
and table aggregation against gold tables and gold  
schema

"""

from corvid.types.semantic_table import SemanticTable
from corvid.types.table import Cell, Table

from typing import Dict, List
import numpy as np


def _compute_number_matching_cells(row1: List[Cell], row2: List[Cell]) -> int:
    """Returns the number of matching cells between two rows of equal length"""
    if len(row1) != len(row2):
        raise Exception('Unequal number of cells in each row')

    match_count = 0
    index_matched_row2 = set()
    for cell1 in row1:
        for cell2_idx, cell2 in enumerate(row2):
            if cell2_idx not in index_matched_row2 and str(cell1) == str(cell2):
                match_count += 1
                index_matched_row2.add(cell2_idx)

    return match_count


def _compute_cell_similarity(row1: List[Cell], row2: List[Cell]) -> float:
    pass


def _count_row_match_(gold_table: Table, aggregate_table: Table) -> int:
    """
        Computes exact match scores between each row of the gold table and the aggregate table
    """
    row_match_count = 0
    aggregate_rows_matched = set()

    # Skip header row by looping from row 1
    for gold_table_row in gold_table.grid[1:]:
        for aggregate_row_idx, aggregate_table_row in enumerate(aggregate_table.grid[1:]):
            # Skip the subject column when checking for matches; Assumes subject column is column 0
            cell_match_count = _compute_number_matching_cells(aggregate_table_row[1:], gold_table_row[1:])

            if aggregate_row_idx not in aggregate_rows_matched and cell_match_count == (gold_table.ncol - 1):
                row_match_count += 1
                aggregate_rows_matched.add(aggregate_row_idx)

    return row_match_count


def _compute_cell_match_(gold_table: Table, aggregate_table: Table) -> float:
    """
        Counts cell level match between each row of the gold table and the aggregate table
    """
    cell_match_counts = np.zeros(shape=(gold_table.nrow - 1, aggregate_table.nrow - 1))
    row_best_match_score = 0.0

    # Skip header row by looping from row 1
    for gold_row_idx, gold_table_row in enumerate(gold_table.grid[1:]):
        for aggregate_row_idx, aggregate_table_row in enumerate(aggregate_table.grid[1:]):
            # Skip the subject column when checking for matches; Assumes subject column is column 0
            cell_match_counts[gold_row_idx][aggregate_row_idx] = _compute_number_matching_cells(aggregate_table_row[1:],
                                                                                                gold_table_row[1:])
    for gold_row_idx in range(0, gold_table.nrow - 2):
        sorted_column_indexes = np.argsort(cell_match_counts[gold_row_idx, :])
        for sorted_column_index in sorted_column_indexes:
            col_max = np.amax(cell_match_counts[:, sorted_column_index])
            if cell_match_counts[gold_row_idx, sorted_column_index] >= col_max:
                row_best_match_score += col_max

    return row_best_match_score


def compute_metrics(gold_table: Table,
                    aggregate_table: Table) -> Dict[str, float]:
    """
        Compute accuracy for: reproducing the target schema, reproducing the gold table
    """

    metric_scores = {}
    cell_match_score = 0  # aggregates match_score for rows with exact and partial matches

    # Row 0 is assumed to be header row. It is evaluated only for schema match
    # It is omitted from row-level and cell-level table evaluations
    # Skip the subject column when checking for matches; Assumes subject column is column 0
    aggregate_table_schema = aggregate_table.grid[0][1:]
    gold_table_schema = gold_table.grid[0][1:]

    schema_match_count = _compute_number_matching_cells(aggregate_table_schema,
                                                        gold_table_schema)
    schema_match_accuracy = (schema_match_count / (gold_table.ncol - 1))

    row_match_count = _count_row_match_(gold_table, aggregate_table)

    cell_match_score = _compute_cell_match_(gold_table, aggregate_table)

    table_match_accuracy_row_level = (row_match_count / (gold_table.nrow - 1))
    table_match_accuracy_cell_level = (cell_match_score / ((gold_table.nrow - 1) * (gold_table.ncol - 1)))

    print('Schema Match Accuracy: ' + str(schema_match_accuracy * 100))
    print('Table Match Accuracy (Row level): ' + str(
        table_match_accuracy_row_level * 100))
    print('Table Match Accuracy (Cell level): ' + str(
        table_match_accuracy_cell_level * 100))

    metric_scores['schema_match_accuracy'] = schema_match_accuracy
    metric_scores['table_match_accuracy_exact'] = table_match_accuracy_row_level
    metric_scores['table_match_accuracy_inexact'] = table_match_accuracy_cell_level

    return metric_scores
