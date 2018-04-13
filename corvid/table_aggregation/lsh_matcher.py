from typing import List
import numpy as np
import nearpy.utils.utils
from nearpy import Engine
from nearpy.distances import CosineDistance
from nearpy.hashes import LSHash, RandomBinaryProjections
from nearpy.filters.nearestfilter import NearestFilter
from nearpy.filters.distancethresholdfilter import DistanceThresholdFilter
from nltk.util import ngrams
from sklearn.feature_extraction.text import TfidfVectorizer

from corvid.table_aggregation.pairwise_mapping import PairwiseMapping
from corvid.types.semantic_table import SemanticTable
from corvid.types.table import Table, Cell, Tuple, Token
from corvid.table_aggregation.schema_matcher import SchemaMatcher


class LSHMatcher(SchemaMatcher):

    def __init__(self):
        # Dimension of feature space
        self.vector_dimension = 100

        rbp = RandomBinaryProjections('rbp', 20)
        self.engine = Engine(self.vector_dimension, lshashes=[rbp],
                             distance=CosineDistance(),
                             vector_filters=[NearestFilter(10)])

    def map_tables(self, tables: List[Table], target_schema: Table) -> List[
        PairwiseMapping]:
        pairwise_mappings = []

        # First index some random vectors
        self.matrix = np.zeros((target_schema.ncol, self.vector_dimension))

        all_ngrams = []
        for table in tables:
            schema = table[0, 1:]
            for cell in schema:
                all_ngrams.append(self._make_char_ngrams(str(cell)))

        ngram_string = [' '.join(ngrams) for ngrams in all_ngrams]
        ngram_term_weights = self._term_weigh_ngrams(ngram_string)
        # print(ngram_term_weights)

        # hash the target schema using random projections method
        for idx_c, cell in enumerate(target_schema[0, 1:]):
            ngram_vector = self._make_char_ngrams(str(cell))
            ngram_weight_vector = [ngram_term_weights[str(ngram).lower()] if str(ngram).lower() in ngram_term_weights else 0 for ngram in
                                   ngram_vector]
            if len(ngram_weight_vector) < self.vector_dimension:
                ngram_weight_vector = self._pad_ngram_vector(ngram_weight_vector,
                                                         self.vector_dimension)
            else:
                del ngram_weight_vector[self.vector_dimension:]

            self.matrix[idx_c, :] = nearpy.utils.utils.unitvec(
                np.asarray(ngram_weight_vector))
            ngram_weight_vector_np = np.asarray(ngram_weight_vector)
            self.engine.store_vector(ngram_weight_vector_np, idx_c)

        # for each table header cell query for the nearest neighbour in target schemas
        for idx_t, table in enumerate(tables):
            schema = table[0, 1:]
            column_mappings = []
            assigned_columns = []
            score = 0
            for idx_c, cell in enumerate(schema):
                ngram_vector = self._make_char_ngrams(str(cell))
                ngram_weight_vector = [ngram_term_weights[str(ngram).lower()] if str(ngram).lower() in ngram_term_weights else 0 for ngram in
                                        ngram_vector]
                if len(ngram_weight_vector) < self.vector_dimension:
                    ngram_weight_vector = self._pad_ngram_vector(
                        ngram_weight_vector,
                        self.vector_dimension)
                else:
                    del ngram_weight_vector[self.vector_dimension:]
                ngram_weight_vector_np = np.asarray(ngram_weight_vector)
                ngram_weight_vector_np = nearpy.utils.utils.unitvec(
                    ngram_weight_vector_np)
                # query = np.random.randn(self.dim)
                #print('\nNeighbour distances with RandomBinaryProjections:')
                #print('\n Candidate count is %d' % self.engine.candidate_count(
                #    ngram_weight_vector_np))
                results = self.engine.neighbours(ngram_weight_vector_np)
                #print('  Data \t| Distance')
                for r in results:
                    data = r[1]
                    dist = r[2]
                    score += dist
                score = round(score,2)
                    #print('  {} \t| {:.4f} | '.format(data, dist))
                if results:
                    for result in results:
                        if result[1] not in assigned_columns:
                            #print(idx_t, idx_c, result[1])
                            column_mappings.append((idx_c + 1, result[1] + 1))
                            assigned_columns.append(result[1])
                            break
            pairwise_mappings.append(PairwiseMapping(table1=table,
                                                     table2=target_schema,
                                                     column_mappings=column_mappings,
                                                     score=score))
        return pairwise_mappings

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
                    try:
                        aggregate_table.grid[
                            index_agg_table_insert, index_target_col] = \
                            pairwise_mapping.table1[
                                idx_source_row, index_source_col]
                    except IndexError:
                        pass
                index_agg_table_insert += 1

        return aggregate_table

    def _pad_ngram_vector(self, ngram_vector: List, dim: int) -> List:
        padding = [0 for i in range(dim - len(ngram_vector))]
        ngram_vector.extend(padding)
        return ngram_vector

    def _term_weigh_ngrams(self, ngram_vector) -> dict:
        vectorizer = TfidfVectorizer(min_df=1)
        X = vectorizer.fit_transform(ngram_vector)
        idf = vectorizer.idf_
        return dict(zip(vectorizer.get_feature_names(), idf))

    def _make_char_ngrams(self, text: str) -> List:
        char_ngrams = []
        # char_ngrams_tuples.extend(list(ngrams(text, 1)))
        for tuple in (list(ngrams(text, 2))):
            ngram = []
            for element in tuple:
                ngram.append(element)
            char_ngrams.append(''.join(ngram))

        for tuple in (list(ngrams(text, 3))):
            ngram = []
            for element in tuple:
                ngram.append(element)
            char_ngrams.append(''.join(ngram))

        return char_ngrams



