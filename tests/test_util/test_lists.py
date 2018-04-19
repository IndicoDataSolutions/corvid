"""



"""

import unittest

from corvid.util.lists import compute_similarity, \
    compute_best_permutation, compute_union, compute_intersection


class TestLists(unittest.TestCase):
    def test_compute_elementwise_similarity(self):
        self.assertEqual(
            compute_similarity(x=[1, 2, 3], y=[1, 2, 3],
                               sim=lambda x, y: x == y, agg=sum),
            3.0)
        self.assertEqual(
            compute_similarity(x=[1, 2, 3], y=[3, 2, 1],
                               sim=lambda x, y: x == y, agg=sum),
            1.0)
        self.assertEqual(
            compute_similarity(x=[3, 3, 3], y=[3, 2, 3],
                               sim=lambda x, y: x == y, agg=sum),
            2.0)
        self.assertEqual(
            compute_similarity(x=[1, 2, 3], y=[3, 1, 3],
                               sim=lambda x, y: x == y, agg=sum),
            1.0)

    def test_compute_max_permutation_similarity(self):
        sim, index_y = \
            compute_best_permutation(x=[1, 2, 3], y=[1, 2, 3],
                                     sim=lambda x, y: x == y,
                                     agg=sum)
        self.assertEqual(sim, 3.0)
        self.assertTupleEqual(index_y, (0, 1, 2))
        sim, index_y = \
            compute_best_permutation(x=[1, 2, 3], y=[3, 2, 1],
                                     sim=lambda x, y: x == y,
                                     agg=sum)
        self.assertEqual(sim, 3.0)
        self.assertTupleEqual(index_y, (2, 1, 0))
        sim, index_y = \
            compute_best_permutation(x=[3, 3, 3], y=[3, 2, 3],
                                     sim=lambda x, y: x == y,
                                     agg=sum)
        self.assertEqual(sim, 2.0)
        self.assertTupleEqual(index_y, (0, 1, 2))
        sim, index_y = \
            compute_best_permutation(x=[1, 2, 3], y=[3, 1, 3],
                                     sim=lambda x, y: x == y,
                                     agg=sum)
        self.assertEqual(sim, 2.0)
        self.assertTupleEqual(index_y, (1, 0, 2))

    def test_compute_union(self):
        x = ['a', 'a', 'b', 'c']
        y = ['a', 'c', 'c', 'd', 'e']
        self.assertListEqual(sorted(compute_union(x=x, y=y)),
                             ['a', 'a', 'b', 'c', 'c', 'd', 'e'])

    def test_compute_intersection(self):
        x = ['a', 'a', 'a', 'b', 'c']
        y = ['a', 'a', 'c', 'c', 'd', 'e']
        self.assertListEqual(sorted(compute_intersection(x=x, y=y)),
                             ['a', 'a', 'c'])
