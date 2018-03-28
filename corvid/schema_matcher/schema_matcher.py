from typing import List, Tuple, Union

import numpy as np
from scipy.optimize import linear_sum_assignment
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import minimum_spanning_tree

from corvid.schema_matcher.pairwise_mapping import PairwiseMapping
from corvid.types.semantic_table import SemanticTable
from corvid.types.table import Table, Cell
from corvid.util.strings import is_floatable


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
                aggregate_table.grid[index_agg_table_insert, 0] = \
                    pairwise_mapping.table1[idx_source_row, 0]

                # fill cells with source table values according to column mappings
                for index_source_col, index_target_col in pairwise_mapping.column_mappings:
                    aggregate_table.grid[
                        index_agg_table_insert, index_target_col] = \
                        pairwise_mapping.table1[
                            idx_source_row, index_source_col]

                index_agg_table_insert += 1

        return aggregate_table

    def _compute_cell_match_header(self,
                                   table1: Table,
                                   table2: Table) -> PairwiseMapping:
        """
            Counts cell level match between rows of two tables
        """

        cell_similarities = np.zeros(shape=(table1.ncol - 1,
                                            table2.ncol - 1))
        for idx1, table1_header_cell in enumerate(table1[0, 1:]):
            for idx2, table2_header_cell in enumerate(table2[0, 1:]):
                cell_similarities[idx1, idx2] = \
                    self._compute_cell_similarity(table1_header_cell,
                                                  table2_header_cell)

        # negative sign here because scipy implementation minimizes sum of weights
        index_table1, index_table2 = linear_sum_assignment(
            -1.0 * cell_similarities)

        sum_similarity_score = cell_similarities[index_table1,
                                                 index_table2].sum()

        return PairwiseMapping(table1, table2,
                               score=sum_similarity_score,
                               column_mappings=[
                                   (c1 + 1, c2 + 1)
                                   for c1, c2, in zip(index_table1,
                                                      index_table2)]
                               )

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
                self._compute_cell_match_header(table, target_schema))

        return pairwise_mappings


class ColValueSchemaMatcher(SchemaMatcher):

    def map_tables(self, tables: List[Table], target_schema: Table) -> \
            List[PairwiseMapping]:

        n = len(tables)
        adj_matrix_pairwise_mappings = [[]]
        adj_matrix_pairwise_mappings = [[0 for i in range(n)] for j in range(n)]

        for idx1 in range(n):
            for idx2 in range(idx1 + 1, n):
                # check if its a schema table; calculate match by header if so
                adj_matrix_pairwise_mappings[idx1][idx2] = \
                    self._compute_cell_match(
                        tables[idx1], tables[idx2])

                # since matrix is symmetric we can copy to the other triangle too
                adj_matrix_pairwise_mappings[idx2][idx1] = \
                    adj_matrix_pairwise_mappings[idx1][idx2]

        adj_matrix_scores = np.zeros((n,n))

        adj_matrix_scores = [
            [pairwise_mapping.score if isinstance(
                pairwise_mapping,PairwiseMapping) else 0
            for pairwise_mapping in row] for row in adj_matrix_pairwise_mappings]
        mst = minimum_spanning_tree(
            csr_matrix(adj_matrix_scores)).toarray().astype(int)

        adj_matrix_col_maps = [
                    [pairwise_mapping.column_mappings
                        if mst[idx_r, idx_c] > 0 else None
                        for idx_c, pairwise_mapping in enumerate(row)]
                        for idx_r, row in enumerate(adj_matrix_pairwise_mappings)
                ]

        pairwise_mappings_opt = []
        tables_merged_to_schema = []

        # greedily match target schema with tables in the MST. We also filter out
        # column mapping between table pairs that are not part of the
        # target schema
        for idx_r, row in enumerate(adj_matrix_col_maps):
            schema_table_pair = self._compute_cell_match_header(
                                                target_schema, tables[idx_r])
            if schema_table_pair.column_mappings is None:
                continue
            if idx_r not in tables_merged_to_schema:
                pairwise_mappings_opt.append(schema_table_pair)
                tables_merged_to_schema.append(idx_r)

            for idx_c, col_map in enumerate(row):
                if col_map is not None:
                    col_map_opt = []
                    map_score = 0.0
                    for sidx, schema_cell in enumerate(target_schema[0, 1:]):
                        for tuple in col_map:
                            if self._compute_cell_similarity(schema_cell,
                                                             tables[idx_c].
                                                                     grid[0][
                                                                 tuple[
                                                                     0]]) >= 1.0:
                                col_map_opt.append((sidx + 1, tuple[0]))
                                map_score +=  self._compute_cell_similarity(schema_cell,
                                                             tables[idx_c].
                                                                     grid[0][
                                                                 tuple[
                                                                     0]]) >= 1.0
                    if idx_c not in tables_merged_to_schema:
                        pairwise_mappings_opt.append(
                            PairwiseMapping(target_schema, tables[idx_c],
                                            column_mappings = col_map_opt,
                                            score = map_score)
                        )
                        tables_merged_to_schema.append(idx_c)

        return pairwise_mappings_opt

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
        # TODO: `table1` is always the table that needs to be aggregated
        # to `table2`=target
        for pairwise_mapping in pairwise_mappings:

            for idx_source_row in range(1, pairwise_mapping.table1.nrow):
                # copy subject for this row
                aggregate_table.grid[index_agg_table_insert, 0] = \
                    pairwise_mapping.table1[idx_source_row, 0]

                # fill cells with source table values according to column mappings
                for index_source_col, index_target_col in pairwise_mapping.column_mappings:
                    aggregate_table.grid[
                        index_agg_table_insert, index_target_col] = \
                        pairwise_mapping.table1[
                            idx_source_row, index_source_col]

                index_agg_table_insert += 1

        return aggregate_table

    def _compute_cell_list_distance(self, l1: List[Cell],
                                    l2: List[Cell], agg: str) -> float:
        """Returns distance between aggregate measures
        to indicate the match between two columns of any length"""

        try:
            l1 = [float(str(cell)) for cell in l1]
            l2 = [float(str(cell)) for cell in l2]
        except Exception as e:
            print(e)
            raise ValueError

        if agg == 'mean':
            return np.mean(l1) - np.mean(l2)
        elif agg == 'max':
            return np.max(l1) - np.max(l2)
        elif agg == 'min':
            return np.min(l1) - np.min(l2)
        else:
            cell_similarities = np.array(
                [
                    [
                        self._compute_cell_similarity(cell1, cell2)
                        for cell2 in l2
                    ]
                    for cell1 in l1
                ]
            )

            # negative sign here because scipy implementation
            # minimizes sum of weights
            index_l1, index_l2 = linear_sum_assignment(
                -1.0 * cell_similarities)

            return cell_similarities[index_l1, index_l2].sum()

    def _compute_cell_match(self, table1: Table,
                            table2: Table, agg='None') -> PairwiseMapping:
        """
            Computes cell level match between each row of the gold table
            and the aggregate table
        """
        column_cell_match = np.zeros(shape=(table1.ncol - 1,
                                            table2.ncol - 1))

        for table1_col_idx in range(1, table1.ncol):
            for table2_col_idx in range(1, table2.ncol):
                if agg == 'mean':
                    column_cell_match[table1_col_idx - 1][
                        table2_col_idx - 1] = \
                        self._compute_cell_list_distance(
                            table1[:, table1_col_idx],
                            table2[:, table2_col_idx],
                            agg='mean')
                elif agg == 'max':
                    column_cell_match[table1_col_idx - 1][
                        table2_col_idx - 1] = \
                        self._compute_cell_list_distance(
                            table1[:, table1_col_idx],
                            table2[:, table2_col_idx],
                            agg='max')
                elif agg == 'min':
                    column_cell_match[table1_col_idx - 1][
                        table2_col_idx - 1] = \
                        self._compute_cell_list_distance(
                            table1[:, table1_col_idx],
                            table2[:, table2_col_idx],
                            agg='min')
                else:
                    column_cell_match[table1_col_idx - 1][
                        table2_col_idx - 1] = \
                        self._compute_cell_list_distance(
                            table1[1:, table1_col_idx],
                            table2[1:, table2_col_idx],
                            agg='none')

        # negative sign here because scipy implementation minimizes
        # sum of weights
        tab1_col_idx, tab2_col_index = linear_sum_assignment(
            -1.0 * column_cell_match)

        col_max_match_score = column_cell_match[tab1_col_idx,
                                                tab2_col_index].sum()

        return PairwiseMapping(table1, table2,
                               score=col_max_match_score,
                               column_mappings=[
                                   (c1 + 1, c2 + 1)
                                   for c1, c2, in zip(tab1_col_idx,
                                                      tab2_col_index)]
                               )
