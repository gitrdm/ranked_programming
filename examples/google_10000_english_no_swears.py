"""
Example: Google 10000 English No Swears (Python port)
Demonstrates ranked programming with a large vocabulary (mocked for demo).
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
