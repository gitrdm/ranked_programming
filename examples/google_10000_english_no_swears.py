"""
Example: Google 10000 English No Swears (Python port)

This example demonstrates ranked programming with a large vocabulary (mocked for demo purposes).

- Normally, you would use a large list of words (e.g., Google 10000 English No Swears).
- For demonstration, a small subset of words is used.
- The either_of combinator creates a ranking where each word is equally plausible.
- The output is a ranking of the words.

Run this file to see the ranked output for the demo vocabulary.
"""
from ranked_programming.rp_api import either_of, pr_all

def google_10000_example():
    # For demo, use a small subset
    words = ['apple', 'banana', 'cherry', 'date', 'elderberry']
    ranking = either_of(*words)
    print("Google 10000 English No Swears output ranking:")
    pr_all(ranking)

if __name__ == "__main__":
    google_10000_example()
