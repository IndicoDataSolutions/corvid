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

from corvid.schema_matcher.pairwise_mapping import PairwiseMapping
from corvid.types.semantic_table import SemanticTable
from corvid.types.table import Table, Cell, Tuple, Token
from corvid.schema_matcher.schema_matcher import SchemaMatcher


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
            ngram_weight_vector = [ngram_term_weights[ngram] for ngram in
                                   ngram_vector]
            ngram_weight_vector = self._pad_ngram_vector(ngram_weight_vector,
                                                         self.vector_dimension)
            self.matrix[idx_c, :] = nearpy.utils.utils.unitvec(
                np.asarray(ngram_weight_vector))
            ngram_weight_vector_np = np.asarray(ngram_weight_vector)
            self.engine.store_vector(ngram_weight_vector_np, idx_c)

        # query for the nearest neighbour to target schemas
        for idx_t, table in enumerate(tables):
            schema = table[0, 1:]
            column_mappings = []
            for idx_c, cell in enumerate(schema):
                ngram_vector = self._make_char_ngrams(str(cell))
                ngram_weight_vector = [ngram_term_weights[ngram] for ngram in
                                       ngram_vector]
                ngram_weight_vector = self._pad_ngram_vector(
                    ngram_weight_vector,
                    self.vector_dimension)
                ngram_weight_vector_np = np.asarray(ngram_weight_vector)
                ngram_weight_vector_np = nearpy.utils.utils.unitvec(
                    ngram_weight_vector_np)
                print(ngram_weight_vector_np)
                # query = np.random.randn(self.dim)
                print('\nNeighbour distances with RandomBinaryProjections:')
                print('\n Candidate count is %d' % self.engine.candidate_count(
                    ngram_weight_vector_np))
                results = self.engine.neighbours(ngram_weight_vector_np)
                print('  Data \t| Distance')
                for r in results:
                    data = r[1]
                    dist = r[2]
                    print('  {} \t| {:.4f} | '.format(data, dist))
                if results:
                    column_mappings.append((results[0][1] + 1, idx_c))
            pairwise_mappings.append(PairwiseMapping(table1=target_schema,
                                                     table2=table,
                                                     column_mappings=column_mappings))
        return pairwise_mappings

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



