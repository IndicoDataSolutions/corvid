"""

Utility functions for comparing lists

"""

from typing import List, Callable, Tuple, Iterable, Union, Any, Dict

import numpy as np
from itertools import permutations
from collections import Counter

from scipy.optimize import linear_sum_assignment


def permute_list(x: List, permutation_indices: Iterable[int]) -> List:
    """Permute `x` according to the indices in `permutation_indices`"""
    return [x[i] for i in permutation_indices]


def compute_similarity(x: List, y: List,
                       sim: Callable[[Any, Any], Union[bool, int, float]],
                       agg: Callable[[List], float]) -> float:
    """Computes similarity between two lists `x` and `y`:

        - `sim(x_i, y_i) -> Union[bool, int, float]` is applied elementwise

        - `agg([float1, float2, ... ]) -> float` is an aggregation function, i.e. mean, max

    e.g.
        inputs:
            x = [1, 2, 3]       vs      y = [1, 2, 4]
            sim = lambda x_i, y_i: x_i == y_i
            agg = sum

        output: 2.0  since  1 == 1 (+1) and 2 == 2 (+1) but 3 != 4 (+0)
    """
    assert len(x) == len(y)
    return agg([sim(x_i, y_i) for x_i, y_i in zip(x, y)])


def compute_best_permutation(x: List,
                             y: List,
                             sim: Callable[[Any, Any], Union[bool, int, float]],
                             agg: Callable[[List], float]) -> \
        Tuple[float, Tuple]:
    """Computes similarity for all possible pairings of `x` and `permute(y)`,
    and returns the permutation that gives highest score
    """
    n = len(x)
    if len(y) != n:
        raise Exception('Unequal number of elements in each list')

    sim_matrix = np.array([[float(sim(x_i, y_j)) for y_j in y] for x_i in x])
    col_index_permutations = list(permutations(range(n)))
    agg_sims = [
        agg([sim_matrix[i, j] for i, j in zip(range(n), col_index_permutation)])
        for col_index_permutation in col_index_permutations
    ]

    # LESS EFFICIENT BUT MORE ILLUSTRATIVE IMPLEMENTATION:
    # agg_sims = [
    #     compute_elementwise_similarity(x,
    #                                    permute_list(y, col_index_permutation),
    #                                    sim,
    #                                    agg)
    #     for col_index_permutation in col_index_permutations
    # ]

    # note: if there are ties, arbitrarily chooses first one in list
    index_max = np.argmax(agg_sims)
    return agg_sims[index_max], col_index_permutations[index_max]


def compute_best_alignments(x: List, y: List,
                            sim: Callable[[Any, Any],
                                          Union[bool, int, float]]) -> \
        List[Dict[str, Tuple[int, Any]]]:
    """Uses Hungarian algorithm (Kuhn) to compute globally optimal pairwise
    alignments between items in lists `x` and `y`, where `sim` computes
    the score of a pairing `x_i` and `y_i`.
    """

    # similarity matrix
    sim_matrix = np.array([[sim(xi, yj) for yj in y] for xi in x])

    # negative sign here because scipy implementation minimizes sum of weights
    index_x, index_y = linear_sum_assignment(-1.0 * sim_matrix)

    # results
    best_alignment_indices = [(i, j) for i, j in zip(index_x, index_y)]
    score_best_alignment = sim_matrix[index_x, index_y].sum()

    return best_alignment_indices


def compute_union(x: Iterable, y: Iterable) -> List:
    """Returns union of items in `x` and `y`, where `x` and `y` allow for
    duplicates.  Items must be hashable.  For example:

    x = ['a', 'a', 'b', 'c']
    y = ['a', 'c', 'c', 'd']

    then their union is ['a', 'a', 'b', 'c', 'c', 'd'].

    **DOES NOT GUARANTEE ORDER OF THE OUTPUT LIST**
    """

    # 1) count everything in `x` and `y`
    counter_x = Counter(x)
    counter_y = Counter(y)

    # 2) fill in `union` with values
    union = []
    keys = set.union(set(x), set(y))
    for key in keys:
        count_x = counter_x.get(key, 0)
        count_y = counter_y.get(key, 0)
        union.extend([key for _ in range(max(count_x, count_y))])

    return union


def compute_intersection(x: Iterable, y: Iterable) -> List:
    """Returns intersection of `x` and `y`, where `x` and `y` allow for
    duplicates.  Items must be hashable.  For example:

    x = ['a', 'a', 'a', 'b', 'c']
    y = ['a', 'a', 'c', 'c', 'd']

    then their intersection is ['a', 'a', 'c'].

    **DOES NOT GUARANTEE ORDER OF THE OUTPUT LIST**
    """

    # 1) count everything in `x` and `y`
    counter_x = Counter(x)
    counter_y = Counter(y)

    # 2) fill in `union` with values
    intersection = []
    keys = set.intersection(set(x), set(y))
    for key in keys:
        count_x = counter_x.get(key)
        count_y = counter_y.get(key)
        intersection.extend([key for _ in range(min(count_x, count_y))])

    return intersection
