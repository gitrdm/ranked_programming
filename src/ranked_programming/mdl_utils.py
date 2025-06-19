"""
MDL (Minimum Description Length) utility for ranked programming.

This module provides a principled way to set the evidence penalty for observation combinators (such as ``observe_e`` and ``observe_e_x``) using the MDL principle from information theory and complexity theory.

**Motivation**

In ranked programming, the evidence penalty determines how "surprising" it is to violate a given observation or constraint. The MDL principle suggests that the penalty should reflect the number of bits needed to describe a world that violates the evidence, relative to one that satisfies it.

**MDL Penalty Formula**

The penalty is computed as:

    penalty = ceil(log2(N / M))

where:
    - N = number of possible values in the ranking
    - M = number of values satisfying the predicate (evidence)

This means that the penalty increases as the evidence becomes more restrictive (smaller M), and is 0 if all values satisfy the evidence.

**Usage Example**

.. code-block:: python

    from ranked_programming.mdl_utils import mdl_evidence_penalty
    from ranked_programming.ranking_observe import observe_e
    ranking = [(x, 0) for x in range(8)]
    pred = lambda x: x % 2 == 0
    penalty = mdl_evidence_penalty(ranking, pred)
    observed = list(observe_e(penalty, pred, ranking))

**Practical Impact**

- The MDL penalty adapts to the size of the search space and the restrictiveness of the evidence.
- This approach is principled, interpretable, and avoids arbitrary penalty choices.
- For hard constraints (M=0), the penalty is infinite (impossible evidence).

See the ``examples/boolean_circuit_mdl.py`` file for a full worked example.
"""
import math
from typing import Iterable, Tuple, Any, Callable

def mdl_evidence_penalty(ranking: Iterable[Tuple[Any, int]], pred: Callable[[Any], bool]) -> int:
    """
    Compute the MDL-based evidence penalty for a ranking and predicate.

    Args:
        ranking: Iterable of (value, rank) pairs.
        pred: Predicate function.

    Returns:
        int: The MDL penalty (ceil(log2(N / M))). Returns float('inf') if M==0 or N==0.

    Example::

        >>> ranking = [(1, 0), (2, 1), (3, 2), (4, 3)]
        >>> mdl_evidence_penalty(ranking, lambda x: x % 2 == 0)
        1
        >>> mdl_evidence_penalty(ranking, lambda x: x == 1)
        2
        >>> mdl_evidence_penalty(ranking, lambda x: True)
        0
        >>> mdl_evidence_penalty(ranking, lambda x: False)
        inf
    """
    items = list(ranking)
    N = len(items)
    M = sum(1 for v, _ in items if pred(v))
    if M == 0 or N == 0:
        return float('inf')
    return math.ceil(math.log2(N / M))
