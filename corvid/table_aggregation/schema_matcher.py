from typing import List, Callable, Tuple

import numpy as np
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import minimum_spanning_tree
from fuzzywuzzy import fuzz

from corvid.table.table import Table, Cell

from corvid.util.lists import compute_best_alignments_with_threshold


class SchemaMatcher(object):
    def predict(self, tables: List[Table], target_schema: List[str]) -> Table:
        raise NotImplementedError


class ColNameSchemaMatcher(SchemaMatcher):
    def predict(self, tables: List[Table], target_schema: List[str]) -> Table:
        schema_table = Table(cells=[Cell(tokens=[s],
                                         index_topleft_row=0,
                                         index_topleft_col=j,
                                         rowspan=1, colspan=1)
                                    for j, s in enumerate(target_schema)],
                             nrow=1, ncol=len(target_schema))

        # match each table to the schema (order doesnt matter)
        for table in tables:
            score, column_alignments = \
                self.compute_column_alignments_by_column_names(schema_table,
                                                               table)
            schema_table = self.merge_two_tables(target=schema_table,
                                                 source=table,
                                                 column_alignments=column_alignments)
        return schema_table

    # TODO: replace `str(cell)` with additional tokenization and processing
    # TODO: allow for matching to columns containing NONE strings
    def compute_column_alignments_by_column_names(self, t1: Table,
                                                  t2: Table) -> \
            Tuple[float, List[Tuple[int, int]]]:
        """Computes similarity between t1 and t2 based on their column names
        (excluding the first column).

        Table similarity equals the sum of column similarities.

        Column similarity equals the string edit distance between the column names
        (string is tokenized and distance is token-order-invariant).

        Returns the table similarity score, and a list of tuples (i, j) where i
        is the column index for t1 and j is the column index for t2.

        Similarity scores are thresholded such that scores 0.0 or below have their
        alignments removed.
        """
        t1_cols = [str(t1[0, j]) for j in range(1, t1.ncol)]
        t2_cols = [str(t2[0, j]) for j in range(1, t2.ncol)]
        score, column_alignments = compute_best_alignments_with_threshold(
            x=t1_cols, y=t2_cols,
            sim=lambda c1, c2: fuzz.token_set_ratio(c1, c2) / 100,
            threshold=0.0
        )
        # matching ignores first column, so indices need to be incremented by 1
        return score, [(0, 0)] + [(i + 1, j + 1) for i, j in column_alignments]

    def merge_two_tables(self, target: Table, source: Table,
                         column_alignments: List[Tuple[int, int]],
                         pad: str = 'NONE') -> Table:
        """Merge a `source` table into a `target` table based on their
        `column_alignments`, which is a List of Tuple[int, int] that index
        the `target` column and the `source` column, respectively.

        Unaligned target columns are padded."""

        t = np.array([[str(cell) for cell in row] for row in target.grid],
                     dtype=object)
        s = np.array([[str(cell) for cell in row] for row in source.grid[1:]],
                     dtype=object)
        index_t_cols = [i for i, j in column_alignments]
        index_s_cols = [j for i, j in column_alignments]

        new_rows = np.array([], dtype=object).reshape(source.nrow - 1, 0)
        for j in range(target.ncol):
            # target column has a source column alignment
            if j in index_t_cols:
                new_col = s[:, index_s_cols[index_t_cols.index(j)]] \
                    .reshape(source.nrow - 1, 1)
            # padding if target column doesnt have a source column alignment
            else:
                new_col = np.array([[pad]] * (source.nrow - 1), dtype=object)

            new_rows = np.append(new_rows, new_col, axis=1)

        # append rows of permuted source (excluding header) into target
        t = np.append(t, new_rows, axis=0)

        # convert to a table
        new_table = Table(grid=[[Cell([cell], i, j)
                                 for j, cell in enumerate(row)]
                                for i, row in enumerate(t)])
        return new_table

