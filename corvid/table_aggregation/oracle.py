from typing import List, Callable, Tuple

import numpy as np

from corvid.table.table import Table, Cell
from corvid.table_aggregation.pairwise_mapping import PairwiseMapping

from corvid.util.lists import compute_best_alignments, compute_intersection


def compute_best_alignments_with_threshold(x: List, y: List, sim: Callable,
                                           threshold: float) -> \
        Tuple[float, List[Tuple[int, int]]]:
    _, raw_alignments = compute_best_alignments(x=x, y=y, sim=sim)

    clean_alignments = []
    score = 0
    for i, j in raw_alignments:
        sim_ij = sim(x[i], y[j])
        if sim_ij > threshold:
            score += sim_ij
            clean_alignments.append((i, j))

    return score, clean_alignments


def predict_oracle(source_tables: List[Table], gold_table: Table) -> Table:
    # convert tables into numpy arrays for easier management
    # - strip header row & subject col
    # - pad sources w/ Nones s.t. they have at least as many columns as gold
    gold = np.array([[str(cell) for cell in row]
                     for row in gold_table.grid[1:, 1:]], dtype=object)
    sources = []
    for source_table in source_tables:
        s = {
            'subject': np.array([str(cell)
                                 for cell in source_table.grid[1:, 0]],
                                dtype=object),
            'source': np.array([[str(cell) for cell in row]
                                for row in source_table.grid[1:, 1:]],
                               dtype=object)
        }
        n_pad_cols = gold.shape[1] - s['source'].shape[1]
        if n_pad_cols > 0:
            padding = np.empty(shape=[s['source'].shape[0], n_pad_cols],
                               dtype=object)
            s['source'] = np.append(s['source'], padding, axis=1)
        sources.append(s)

    # initialize predicted output
    pred = np.array([[str(cell) for cell in gold_table.grid[0, :]]],
                    dtype=object)

    # continue until every gold row is matched and/or run out of sources
    while gold.shape[0] > 0 and len(sources) > 0:
        #
        # (1) which source table has most similar columns to gold?
        #
        scores = []
        all_column_mappings = []
        for s in sources:
            # represent each column j as a list [ cell_1j, cell_2j, ... ]
            # gold & source can have differing-length columns
            gold_cols = [list(col) for col in zip(*gold)]
            source_cols = [list(col) for col in zip(*s['source'])]

            # align columns between gold & source
            score, column_mappings = compute_best_alignments(
                x=gold_cols, y=source_cols,
                sim=lambda gold_col, source_col:
                len(compute_intersection(x=gold_col, y=source_col))
            )
            scores.append(score)
            all_column_mappings.append(column_mappings)

        # pick best match among sources & permute its cols to match gold
        # also, pop this source from the list of sources
        index_best_score = np.argmax(scores)
        best_column_mappings = all_column_mappings[index_best_score]
        s = sources.pop(index_best_score)
        permute_source_cols = [
            source_col for gold_col, source_col in best_column_mappings
        ]
        source = s['source'][:, permute_source_cols]
        subject = s['subject']

        #
        # (2) which rows of (col-permuted) source table match best to gold rows?
        #
        # represent each row i as a tuple = ( cell_i1, cell_i2, ..., cell_ik )
        #  where k = ncol(gold)
        gold_rows = [tuple(cell for cell in row) for row in gold]
        source_rows = [tuple(cell for cell in row) for row in source]

        # align rows between gold & source
        _, row_mappings = compute_best_alignments_with_threshold(
            x=gold_rows, y=source_rows,
            sim=lambda gold_row, source_row:
            sum([g_i == s_i for g_i, s_i in zip(gold_row, source_row)]),
            threshold=0
        )
        index_gold_rows = []
        index_source_rows = []
        for index_gold_row, index_source_row in row_mappings:
            index_gold_rows.append(index_gold_row)
            index_source_rows.append(index_source_row)

        #
        # (3) append matched source rows to pred
        #
        new_rows = [
            [str(index_best_score) + '__' + subject[i]] + list(source_rows[i])
            for i in index_source_rows
        ]
        pred = np.append(pred, new_rows, axis=0)

        #
        # (4) remove gold rows that matched
        #
        gold = np.delete(gold, index_gold_rows, axis=0)

    return Table(grid=[[Cell([cell], i, j, 0, 0)
                        for j, cell in enumerate(row)]
                       for i, row in enumerate(pred)])


if __name__ == '__main__':
    source_table1 = Table(cells=[
        Cell([''], 0, 0), Cell(['x'], 0, 1), Cell(['y'], 0, 2),
        Cell(['z'], 0, 3),
        Cell(['s:m1'], 1, 0), Cell(['a'], 1, 1), Cell(['?'], 1, 2),
        Cell(['2'], 1, 3),
        Cell(['s:m2'], 2, 0), Cell(['b'], 2, 1), Cell(['?'], 2, 2),
        Cell(['1'], 2, 3),
    ], nrow=3, ncol=4)

    source_table2 = Table(cells=[
        Cell([''], 0, 0), Cell(['w'], 0, 1),
        Cell(['s:m3'], 1, 0), Cell(['a'], 1, 1),
        Cell(['s:m4'], 2, 0), Cell(['b'], 2, 1),
        Cell(['s:m5'], 3, 0), Cell(['c'], 3, 1),
    ], nrow=4, ncol=2)

    source_table3 = Table(cells=[
        Cell([''], 0, 0), Cell(['xx'], 0, 1), Cell(['yy'], 0, 2),
        Cell(['s:m6'], 1, 0), Cell(['c'], 1, 1), Cell(['asdf'], 1, 2),
        Cell(['s:m7'], 2, 0), Cell(['d'], 2, 1), Cell(['fdsa'], 2, 2),
    ], nrow=3, ncol=3)

    gold_table = Table(cells=[
        Cell([''], 0, 0), Cell(['h1'], 0, 1), Cell(['h2'], 0, 2),
        Cell(['g:m1'], 1, 0), Cell(['1'], 1, 1), Cell(['a'], 1, 2),
        Cell(['g:m2'], 2, 0), Cell(['2'], 2, 1), Cell(['b'], 2, 2),
        Cell(['g:m3'], 3, 0), Cell(['3'], 3, 1), Cell(['c'], 3, 2),
        Cell(['g:m4'], 4, 0), Cell(['4'], 4, 1), Cell(['d'], 4, 2),
    ], nrow=5, ncol=3)

    source_tables = [source_table3, source_table2, source_table1]
    print(predict_oracle(source_tables, gold_table))
