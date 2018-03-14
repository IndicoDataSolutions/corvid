from corvid.schema_matcher.pairwise_mapping import PairwiseMapping
from corvid.types.semantic_table import SemanticTable
from corvid.types.table import Table, Cell

from typing import List, Tuple

import numpy as np


class SchemaMatcher(object):

    def map_tables(self, tables: List[Table]) -> \
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
