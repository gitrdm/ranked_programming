"""
Example: Google 10000 English No Swears (Python port)

This example demonstrates ranked programming applied to natural language processing (NLP) tasks,
specifically handling large vocabularies for applications like spelling correction, autocomplete,
or language modeling.

**What is Ranked Programming?**
Ranked programming is an alternative to probabilistic programming. Instead of assigning probabilities
(0.0 to 1.0) to outcomes, it uses integer "ranks" to represent degrees of surprise or disbelief:
- Rank 0: Not surprising (normal/expected)
- Rank 1+: Increasingly surprising (exceptional/unexpected)
- Rank ∞: Impossible

This approach is computationally simpler for certain types of uncertainty and excels at modeling
"normal vs. exceptional" scenarios without needing precise probability distributions.

**Purpose of This Example:**
- Shows how to represent a large vocabulary (10,000+ common English words) as equally plausible options.
- Demonstrates the `either_of` combinator for creating flat rankings over multiple possibilities.
- Illustrates lazy evaluation for handling large datasets efficiently.
- Provides a foundation for NLP applications where you might:
  * Start with all words equally ranked (rank 0)
  * Use conditionalization to adjust ranks based on context (e.g., penalize unlikely spellings)
  * Find the least surprising (lowest rank) completions or corrections

**Key Concepts Demonstrated:**
- Ranking Theory foundations: Graded disbelief and surprise
- Combinators: `either_of` for choice, `pr_all` for output
- Scalability: Handling large search spaces with lazy generators
- Real-world application: Vocabulary-based NLP tasks

**Usage:**
- By default, uses a small subset of words for demo purposes (to keep output manageable for testing).
- Optionally, can load the full Google 10000 English No Swears list from the text file.
- The either_of combinator creates a ranking where each word is equally plausible.
- The output is a ranking of the words.

Run this file to see the ranked output. Use --full to load the real data.
"""
import argparse
from ranked_programming.rp_api import either_of, pr_all, Ranking

def google_10000_example(use_full=False, limit=None):
    if use_full:
        # Load real data from file
        with open('examples/google-10000-english-no-swears.txt', 'r') as f:
            words = [line.strip() for line in f if line.strip()]
        if limit:
            words = words[:limit]
    else:
        # Use small subset for demo
        words = ['apple', 'banana', 'cherry', 'date', 'elderberry']
    
    # Use either_of on a list of Ranking objects, each yielding (word, 0)
    ranking = either_of(*(Ranking(lambda w=w: [(w, 0)]) for w in words))
    print(f"Google 10000 English No Swears output ranking ({'full' if use_full else 'demo'}):")
    pr_all(ranking)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Google 10000 English No Swears example")
    parser.add_argument('--full', action='store_true', help="Use full vocabulary from file")
    parser.add_argument('--limit', type=int, help="Limit number of words when using full data")
    args = parser.parse_args()
    google_10000_example(use_full=args.full, limit=args.limit)
