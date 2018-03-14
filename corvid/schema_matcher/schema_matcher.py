from corvid.schema_matcher.pairwise_mapping import PairwiseMapping
from corvid.types.semantic_table import SemanticTable
from corvid.types.table import Table, Cell

from typing import List, Tuple

import numpy as np


class SchemaMatcher(object):

    def map_tables(self, tables: List[Table], target_schema: Table) -> \
            List[PairwiseMapping]:
        raise NotImplementedError

    def aggregate_tables(self,
                         pairwise_mappings: List[PairwiseMapping],
                         target_schema: Table) -> Table:

        # initialize empty aggregate table
        num_rows_agg_table = sum([pairwise_mapping.table1.nrow - 1
                                  for pairwise_mapping in pairwise_mappings])

        aggregate_table = Table.create_from_grid(grid=np.array([
            [None for _ in range(target_schema.ncol)]
            for _ in range(num_rows_agg_table)
        ]))
        aggregate_table = aggregate_table.insert_row(index=0,
                                                     row=target_schema[0, :])

        index_agg_table_insert = 1
        # TODO: `table1` is always the table that needs to be aggregated to `table2`=target
        for pairwise_mapping in sorted(pairwise_mappings):

            for idx_source_row in range(1, pairwise_mapping.table1.nrow):
                # copy subject for this row
                aggregate_table.grid[index_agg_table_insert, 0] = pairwise_mapping.table1[idx_source_row, 0]

                # fill cells with source table values according to column mappings
                for index_source_col, index_target_col in pairwise_mapping.column_mappings:
                    aggregate_table.grid[index_agg_table_insert, index_target_col] = pairwise_mapping.table1[idx_source_row, index_source_col]

                index_agg_table_insert += 1

        return aggregate_table


    def _compute_cell_similarity(self, cell1: Cell, cell2: Cell) -> float:
        """
        Returns similarity between two cells;
        currently it tests for equality
        """
        return float(str(cell1).strip().lower() == str(cell2).strip().lower())


class ColNameSchemaMatcher(SchemaMatcher):

    def map_tables(self, tables: List[Table], target_schema: Table) -> \
            List[PairwiseMapping]:
        pairwise_mappings = []

        for table in tables:
            pairwise_mappings.append(
                self._compute_cell_match(table, target_schema))

        return pairwise_mappings



    def _compute_cell_match(self,
                            table1: Table,
                            table2: Table) -> PairwiseMapping:
        """
            Counts cell level match between rows of two tables
        """

        cell_match_counts = np.array([
            [
                self._compute_cell_similarity(cell1=gold_row[1:], cell2=pred_row[1:])
                for pred_row in pred_table.grid[1:, :]
            ]
            for gold_row in gold_table.grid[1:, :]
        ])

        # negative sign here because scipy implementation minimizes sum of weights
        index_gold, index_pred = linear_sum_assignment(
            -1.0 * cell_match_counts)

        return cell_match_counts[index_gold, index_pred].sum() / \
               ((gold_table.nrow - 1) * (gold_table.ncol - 1))




        column_mappings = []

        # initializing w/ ncol - 1 because ignoring subject columns
        cell_similarities = np.zeros(shape=(table1.ncol - 1,
                                            table2.ncol - 1))

        #
        for idx1, table1_header_cell in enumerate(table1[1, :]):
            for idx2, table2_header_cell in enumerate(table2[1, :]):
                cell_similarities[idx1 - 1, idx2 - 1] = \
                    self._compute_cell_similarity(table1_header_cell,
                                                  table2_header_cell)

        sum_similarity_score = 0.0
        for table1_col_idx in range(cell_similarities.shape[0]):
            # sort each row of cell similarity matrix descending
            # get the indices in the sorted order
            sorted_table2_col_indexes = np.argsort(
                cell_similarities[table1_col_idx, :][::-1])
            for table2_col_index in sorted_table2_col_indexes:
                max_table2_match = np.amax(
                    cell_similarities[:, table2_col_index])
                if cell_similarities[table1_col_idx, table2_col_index] \
                        >= max_table2_match:
                    sum_similarity_score += \
                        cell_similarities[table1_col_idx, table2_col_index]
                    column_mappings.append(
                        (table1_col_idx, table2_col_index))
                    break

        return PairwiseMapping(table1, table2,
                               score=sum_similarity_score,
                               column_mappings=column_mappings)
