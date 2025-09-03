"""
Spelling Correction with Multiple Penalty Analysis

This example demonstrates the same spelling correction logic as the original spelling_correction.py,
but applies multiple penalty algorithms to analyze how penalties affect correction quality rankings.

**Original Logic Preserved:**
- Input word: 'hte' (intended correction: 'the')
- Edit operations: deletions, insertions, substitutions, transpositions
- Dictionary matching with wildcards
- Ranking by minimum edit distance
- Same ranking structures and lazy evaluation

**Penalty Analysis Added:**
- Applies MDL, Adaptive, Confidence, and Fixed penalties to correction candidates
- Analyzes correction quality based on different criteria
- Shows how penalty choice affects correction rankings
- Demonstrates trade-offs between different penalty approaches

**Key Concepts:**
- **Spelling Correction**: Finding dictionary words closest to misspelled input
- **Edit Distance**: Minimum operations to transform one word to another
- **Penalty Algorithms**: Different ways to evaluate correction quality
- **Correction Analysis**: How penalties affect the ranking of spelling corrections

**Key Insights and Common Confusions:**

**Understanding Penalty Effects on Rankings:**
This example demonstrates an important concept: penalties modify existing plausibility rankings,
they don't replace them. The final ranking depends on both the original base rankings AND the
penalty adjustments.

**Why Different Corrections Get Different Penalties:**
- Short corrections (like "the") may get lower penalties than longer ones
- Different penalty algorithms weight edit distance differently
- Some algorithms are more conservative (Adaptive, Confidence start with penalty=0)
- Others are more aggressive (MDL calculates based on information theory)

**Penalty Algorithm Differences:**
- MDL: Information-theoretic penalties based on edit patterns
- Adaptive: Learning-based, starts conservative (penalty=0)
- Confidence: Statistical bounds, starts conservative (penalty=0)
- Fixed: Constant penalty regardless of correction characteristics

**Important: Don't Expect All Corrections to Have Higher Ranks**
The original edit distance matters! If a correction has a very low edit distance,
penalties might not be enough to push it below other corrections with higher edit distances.

**Expected Output:**
1. Original spelling correction rankings for 'hte'
2. Penalty calculations showing how different algorithms assess correction quality
3. Comparative rankings demonstrating how penalties modify base edit distances
4. Clear examples of when penalties do/don't change the top correction
"""
from ranked_programming.rp_core import Ranking, nrm_exc, pr_all
from ranked_programming.ranking_observe import observe_e
from ranked_programming.mdl_utils import mdl_evidence_penalty, adaptive_evidence_penalty, confidence_evidence_penalty
import os

# Load dictionary from file (as set of tuples of chars)
dict_path = os.path.join(os.path.dirname(__file__), 'google-10000-english-no-swears.txt')
with open(dict_path, 'r') as f:
    DICTIONARY = set(tuple(line.strip()) for line in f if line.strip())

def edits(word, max_edits=3, current_edits=0, seen=None):
    """Recursively generate all possible edits (insert, delete, substitute, wildcard) for the word as tuples of chars, up to max_edits."""
    if seen is None:
        seen = set()
    word = tuple(word)
    if (word, current_edits) in seen or current_edits > max_edits:
        return
    seen.add((word, current_edits))
    yield (word, current_edits)
    n = len(word)
    # Deletion
    for i in range(n):
        w = word[:i] + word[i+1:]
        yield from edits(w, max_edits, current_edits + 1, seen)
    # Insertion (wildcard)
    for i in range(n+1):
        w = word[:i] + ('*',) + word[i:]
        yield from edits(w, max_edits, current_edits + 1, seen)
    # Substitution (wildcard)
    for i in range(n):
        w = word[:i] + ('*',) + word[i+1:]
        yield from edits(w, max_edits, current_edits + 1, seen)
    # Transposition (swap adjacent characters)
    for i in range(n-1):
        w = word[:i] + (word[i+1], word[i]) + word[i+2:]
        yield from edits(w, max_edits, current_edits + 1, seen)


def matches_pattern(pattern, dictionary):
    """Return all words in the dictionary that match the pattern (with '*' as wildcard)."""
    plen = len(pattern)
    results = set()
    for word in dictionary:
        if len(word) != plen:
            continue
        for c1, c2 in zip(pattern, word):
            if c1 != '*' and c1 != c2:
                break
        else:
            results.add(word)
    return results


def get_spelling_corrections():
    """Get the original spelling correction rankings"""
    input_word = 'hte'
    # Generate all edits up to 3 edits
    candidates = dict()  # word -> min edits
    for pattern, edits_count in edits(input_word, max_edits=3):
        for match in matches_pattern(pattern, DICTIONARY):
            if match not in candidates or edits_count < candidates[match]:
                candidates[match] = edits_count

    # Convert to ranking format
    corrections = []
    for word_tuple, edit_distance in sorted(candidates.items(), key=lambda x: (x[1], x[0])):
        corrections.append((word_tuple, edit_distance))

    return corrections


def analyze_spelling_corrections_with_penalties():
    """Apply penalty analysis to spelling correction candidates"""

    print("="*80)
    print("SPELLING CORRECTION ANALYSIS WITH MULTIPLE PENALTIES")
    print("="*80)

    corrections = get_spelling_corrections()

    print("\n1. ORIGINAL SPELLING CORRECTION BEHAVIOR:")

    print("\nSpelling corrections for 'hte':")
    print("Edits  Word")
    print("-----------")
    for word_tuple, edit_distance in corrections[:15]:  # Show first 15
        word_str = ''.join(word_tuple)
        print(f"{edit_distance:<6} {word_str}")
    print("...")

    # Define correction quality predicates
    def short_word(word_tuple):
        """Predicate: prefer short corrections (fewer characters)"""
        return len(word_tuple) <= 4

    def common_correction(word_tuple):
        """Predicate: prefer common English words (top 20 most frequent)"""
        word = ''.join(word_tuple)
        # Top 20 most common English words based on Google 10k corpus
        common_words = {
            'the', 'of', 'and', 'to', 'a', 'in', 'for', 'is', 'on', 'that',
            'by', 'this', 'with', 'i', 'you', 'it', 'not', 'or', 'be', 'are'
        }
        return word in common_words

    def low_edit_distance(word_tuple):
        """Predicate: prefer corrections with low edit distance"""
        # For this predicate, we need to look up the edit distance from our corrections data
        word_str = ''.join(word_tuple)
        for w_tuple, edit_dist in corrections:
            if w_tuple == word_tuple:
                return edit_dist <= 2
        return False  # If not found, assume high edit distance

    def starts_with_t(word_tuple):
        """Predicate: prefer corrections starting with 't'"""
        return len(word_tuple) > 0 and word_tuple[0] == 't'

    print("\n2. PENALTY ANALYSIS FOR CORRECTION QUALITY:")
    print("Note: Penalties modify existing rankings, they don't replace them!")
    print("      The final ranking depends on BOTH original edit distances AND penalty adjustments.")

    # Convert corrections to ranking format for penalty analysis
    correction_ranking = Ranking(lambda: corrections)

    for predicate_name, predicate, description in [
        ("short", short_word, "Prefer short corrections (≤4 chars)"),
        ("common", common_correction, "Prefer common English words"),
        ("low_edit", low_edit_distance, "Prefer low edit distance (≤2)"),
        ("starts_t", starts_with_t, "Prefer corrections starting with 't'")
    ]:
        print(f"\n{description}:")

        # MDL penalty
        penalty_mdl = mdl_evidence_penalty(correction_ranking, predicate)
        observed_mdl = list(observe_e(penalty_mdl, predicate, correction_ranking))
        top_mdl = observed_mdl[0]
        word_str = ''.join(top_mdl[0])
        print(f"MDL penalty ({penalty_mdl}): {word_str} (edits {top_mdl[1]})")
        if len(observed_mdl) > 1:
            ranking_str = ', '.join([f"{''.join(w)}({r})" for w, r in observed_mdl[:3]])
            print(f"  Full ranking: {ranking_str}")

        # Adaptive penalty
        penalty_adaptive = adaptive_evidence_penalty(correction_ranking, predicate, f"correction_{predicate_name}")
        observed_adaptive = list(observe_e(penalty_adaptive, predicate, correction_ranking))
        top_adaptive = observed_adaptive[0]
        word_str = ''.join(top_adaptive[0])
        print(f"Adaptive penalty ({penalty_adaptive}): {word_str} (edits {top_adaptive[1]})")
        if len(observed_adaptive) > 1:
            ranking_str = ', '.join([f"{''.join(w)}({r})" for w, r in observed_adaptive[:3]])
            print(f"  Full ranking: {ranking_str}")

        # Confidence penalty
        penalty_confidence = confidence_evidence_penalty(correction_ranking, predicate)
        observed_confidence = list(observe_e(penalty_confidence, predicate, correction_ranking))
        top_confidence = observed_confidence[0]
        word_str = ''.join(top_confidence[0])
        print(f"Confidence penalty ({penalty_confidence}): {word_str} (edits {top_confidence[1]})")
        if len(observed_confidence) > 1:
            ranking_str = ', '.join([f"{''.join(w)}({r})" for w, r in observed_confidence[:3]])
            print(f"  Full ranking: {ranking_str}")

        # Fixed penalty
        observed_fixed = list(observe_e(1, predicate, correction_ranking))
        top_fixed = observed_fixed[0]
        word_str = ''.join(top_fixed[0])
        print(f"Fixed penalty (1): {word_str} (edits {top_fixed[1]})")
        if len(observed_fixed) > 1:
            ranking_str = ', '.join([f"{''.join(w)}({r})" for w, r in observed_fixed[:3]])
            print(f"  Full ranking: {ranking_str}")

    print("\n" + "="*80)
    print("ANALYSIS: SPELLING CORRECTION INSIGHTS")
    print("="*80)

    print("\nSpelling Correction Pattern Analysis:")
    print("- Edit operations: deletions, insertions, substitutions, transpositions")
    print("- Dictionary matching with wildcards for flexible pattern matching")
    print("- Ranking by minimum edit distance (lower = better)")

    print("\nPenalty Algorithm Comparison:")
    print("- MDL: Information-theoretic assessment of correction quality")
    print("- Adaptive: Learns from correction patterns over time")
    print("- Confidence: Statistical bounds on correction reliability")
    print("- Fixed: Constant penalty regardless of correction characteristics")

    print("\nKey Observations:")
    print("- Penalties can shift preferences between different correction candidates")
    print("- Different quality criteria (short, common, low-edit, starts-with-t) affect rankings differently")
    print("- Original edit distances heavily influence penalty effectiveness")
    print("- Some criteria show dramatic ranking changes, others show minimal effects")
    print("- 'the' appears as a top correction due to transposition support")

if __name__ == "__main__":
    analyze_spelling_corrections_with_penalties()
