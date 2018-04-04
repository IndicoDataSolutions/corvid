"""

Functions for performing common diagnostics in Python interactive Console

"""

import numpy as np

from corvid.types.table import Table

def sample_rows(table: Table, k: int = 10) -> Table:
    # exclude first header row from random sample but add it back after
    k = min(k, table.nrow) - 1
    index = np.insert(np.random.permutation(range(1, table.nrow))[:k], 0, [0])
    return table[index, :]
