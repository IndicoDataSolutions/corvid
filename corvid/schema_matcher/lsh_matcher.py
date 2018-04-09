from typing import List
import numpy as np
import nearpy.utils.utils
from nearpy import Engine
from nearpy.distances import CosineDistance
from nearpy.hashes import LSHash, RandomBinaryProjections
from nltk.util import ngrams
from collections import Counter
from sklearn.feature_extraction.text import TfidfVectorizer
from google_ngram_downloader import readline_google_store

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
                             distance=CosineDistance())

    def map_tables(self, tables: List[Table], target_schema: Table) -> List[
        PairwiseMapping]:
        pairwise_mappings = []

        # First index some random vectors
        self.matrix = np.zeros((target_schema.ncol, self.vector_dimension))

        all_ngrams = []
        for table in tables:
            schema = table[0, 1:]
            for idx_c, cell in enumerate(schema):
                all_ngrams.append(self._make_char_ngrams(str(cell)))

        ngram_string = [' '.join(ngrams) for ngrams in all_ngrams]
        ngram_term_weights = self._term_weigh_ngrams(ngram_string)

        # hash the target schema using random projections method
        for idx_c, cell in enumerate(target_schema[0, :]):
            ngram_vector = self._make_char_ngrams(str(cell))
            ngram_weight_vector = [ngram_term_weights[ngram] for ngram in
                                   range(len(ngram_vector))]
            ngram_weight_vector = self._pad_ngram_vector(ngram_weight_vector,
                                                         100)
            self.matrix[idx_c, :] = nearpy.utils.utils.unitvec(
                np.asanyarray(ngram_weight_vector))
            self.engine.store_vector(ngram_weight_vector, idx_c)

        #query for the nearest neighbour to target schemas
        for idx_t, table in enumerate(tables):
            schema = table[0, 1:]
            column_mappings = []
            for idx_c, cell in enumerate(schema):
                ngram_vector = self._make_char_ngrams(str(cell))
                ngram_weight_vector = [ngram_term_weights[ngram] for ngram in
                                       range(len(ngram_vector))]
                ngram_weight_vector = self._pad_ngram_vector(ngram_weight_vector,
                                                            100)
                # Get random query vector
                # query = np.random.randn(self.dim)
                print('\nNeighbour distances with RandomBinaryProjections:')
                print('\n Candidate count is %d' % self.engine.candidate_count(
                    ngram_weight_vector))
                results = self.engine.neighbours(ngram_weight_vector)
                print('  Data \t| Distance')
                for r in results:
                    data = r[1]
                    dist = r[2]
                    print('  {} \t| {:.4f}'.format(data, dist))
                column_mappings.append((results[0], cell))
                exit(0)
            pairwise_mappings.append(table1=target_schema,
                                     table2=table,
                                     column_mappings=column_mappings)

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


class SchemaMatchHash(LSHash):

    def reset(self, dim):
        """ Resets / Initializes the hash for the specified dimension. """
        raise NotImplementedError

    def hash_vector(self, v, querying=False):
        """
        Hashes the vector and returns a list of bucket keys, that match the
        vector. Depending on the hash implementation this list can contain
        one or many bucket keys. Querying is True if this is used for
        retrieval and not indexing.
        """
        raise NotImplementedError

    def get_config(self):
        """
        Returns pickle-serializable configuration struct for storage.
        """
        raise NotImplementedError

    def apply_config(self, config):
        """
        Applies config
        """
        raise NotImplementedError
