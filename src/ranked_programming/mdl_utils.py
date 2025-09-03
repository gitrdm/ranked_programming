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

**Additional Penalty Types**

Besides MDL, this module also provides:
- **Adaptive Penalty**: Learns from historical data to approach optimal penalties asymptotically
- **Confidence Penalty**: Based on statistical confidence intervals

**Usage Example**

.. code-block:: python

    from ranked_programming.mdl_utils import mdl_evidence_penalty, adaptive_evidence_penalty
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
from collections import defaultdict

from ranked_programming.theory_types import PRACTICAL_INFINITY

TERMINATE_RANK = PRACTICAL_INFINITY  # Large integer to represent impossible evidence

# Global history for adaptive penalty
_penalty_history = defaultdict(lambda: {'successes': 0, 'total': 0, 'penalty': 1})

def mdl_evidence_penalty(ranking: Iterable[Tuple[Any, int]], pred: Callable[[Any], bool]) -> int:
    """
    Compute the MDL-based evidence penalty for a ranking and predicate.

    Args:
        ranking: Iterable of (value, rank) pairs.
        pred: Predicate function.

    Returns:
        int: The MDL penalty (ceil(log2(N / M))). Returns TERMINATE_RANK if M==0 or N==0.

    Example::

        >>> ranking = [(1, 0), (2, 1), (3, 2), (4, 3)]
        >>> mdl_evidence_penalty(ranking, lambda x: x % 2 == 0)
        1
        >>> mdl_evidence_penalty(ranking, lambda x: x == 1)
        2
        >>> mdl_evidence_penalty(ranking, lambda x: True)
        0
        >>> mdl_evidence_penalty(ranking, lambda x: False)
        1000000000
    """
    items = list(ranking)
    N = len(items)
    M = sum(1 for v, _ in items if pred(v))
    if M == 0 or N == 0:
        return TERMINATE_RANK
    return math.ceil(math.log2(N / M))

def adaptive_evidence_penalty(ranking: Iterable[Tuple[Any, int]], pred: Callable[[Any], bool], 
                            predicate_id: str = "default", learning_rate: float = 0.1) -> int:
    """
    Compute an adaptive evidence penalty that learns from historical performance.
    
    This penalty starts with an initial value and adjusts asymptotically based on how well
    the predicate performs over time. It approaches 0 when evidence is consistently satisfied,
    and approaches infinity when evidence is consistently violated.
    
    Args:
        ranking: Iterable of (value, rank) pairs.
        pred: Predicate function.
        predicate_id: Unique identifier for this predicate to maintain separate history.
        learning_rate: How quickly to adapt (0.0 to 1.0, default 0.1).
    
    Returns:
        int: Adaptive penalty that converges asymptotically.
    
    Example::
        >>> ranking = [(1, 0), (2, 1), (3, 2), (4, 3)]
        >>> adaptive_evidence_penalty(ranking, lambda x: x % 2 == 0, "even_pred")
        1  # Initial penalty
    """
    items = list(ranking)
    N = len(items)
    M = sum(1 for v, _ in items if pred(v))
    
    if N == 0:
        return TERMINATE_RANK
    
    # Update history
    history = _penalty_history[predicate_id]
    history['total'] += 1
    if M > 0:  # Some evidence satisfied
        history['successes'] += 1
    
    # Calculate empirical probability of satisfaction
    empirical_prob = history['successes'] / history['total']
    
    # Adaptive penalty: approaches 0 when prob=1, approaches infinity when prob=0
    if empirical_prob == 0:
        penalty = TERMINATE_RANK
    elif empirical_prob == 1:
        penalty = 0
    else:
        # Use inverse sigmoid to create asymptotic behavior
        # As empirical_prob approaches 0, penalty approaches infinity
        # As empirical_prob approaches 1, penalty approaches 0
        sigmoid_input = math.log(empirical_prob / (1 - empirical_prob))
        target_penalty = max(0, -sigmoid_input)  # Positive when prob < 0.5
        
        # Smooth adaptation
        current_penalty = history['penalty']
        penalty = current_penalty + learning_rate * (target_penalty - current_penalty)
        penalty = max(0, min(TERMINATE_RANK, penalty))
    
    # Update stored penalty
    history['penalty'] = int(penalty)
    
    return int(math.ceil(penalty))

def confidence_evidence_penalty(ranking: Iterable[Tuple[Any, int]], pred: Callable[[Any], bool], 
                              confidence_level: float = 0.95) -> int:
    """
    Compute evidence penalty based on statistical confidence intervals.
    
    This penalty uses binomial confidence intervals to determine how surprising it is
    to observe the current evidence satisfaction rate, given the sample size.
    
    Args:
        ranking: Iterable of (value, rank) pairs.
        pred: Predicate function.
        confidence_level: Statistical confidence level (0.0 to 1.0, default 0.95).
    
    Returns:
        int: Confidence-based penalty.
    
    Example::
        >>> ranking = [(1, 0), (2, 1), (3, 2), (4, 3)]
        >>> confidence_evidence_penalty(ranking, lambda x: x % 2 == 0)
        1
    """
    items = list(ranking)
    N = len(items)
    M = sum(1 for v, _ in items if pred(v))
    
    if N == 0:
        return TERMINATE_RANK
    if M == 0:
        return TERMINATE_RANK
    
    # Observed proportion
    p_hat = M / N
    
    # Standard error for proportion
    if p_hat == 0 or p_hat == 1:
        return 0 if p_hat == 1 else TERMINATE_RANK
    
    se = math.sqrt(p_hat * (1 - p_hat) / N)
    
    # Z-score for confidence level (approximate)
    if confidence_level >= 0.99:
        z = 2.576
    elif confidence_level >= 0.95:
        z = 1.96
    elif confidence_level >= 0.90:
        z = 1.645
    else:
        z = 1.0
    
    # Confidence interval bounds
    margin = z * se
    lower_bound = max(0, p_hat - margin)
    upper_bound = min(1, p_hat + margin)
    
    # Penalty based on how far 0.5 is from the confidence interval
    # If 0.5 is outside the interval, penalty reflects the deviation
    if upper_bound < 0.5:
        # Evidence strongly suggests low satisfaction rate
        deviation = 0.5 - upper_bound
        penalty = math.ceil(-math.log2(deviation + 0.001))  # Approaches infinity as deviation increases
    elif lower_bound > 0.5:
        # Evidence strongly suggests high satisfaction rate
        deviation = lower_bound - 0.5
        penalty = math.ceil(-math.log2(deviation + 0.001))  # Approaches infinity as deviation increases
    else:
        # 0.5 is within confidence interval - no strong evidence either way
        penalty = 0
    
    return min(penalty, TERMINATE_RANK)
