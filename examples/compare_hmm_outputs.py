import subprocess
import sys
import os
from difflib import unified_diff

# Observation sequences to test
test_cases = [
    ['no', 'no', 'yes', 'no', 'no'],
    ['yes', 'yes', 'yes', 'no', 'no'],
    ['yes', 'yes', 'yes', 'yes', 'yes', 'yes'],
]

python_script = 'examples/hidden_markov.py'
racket_script = 'examples/hidden_markov.rkt'


def run_python(obs):
    env = os.environ.copy()
    env['HMM_DEBUG'] = '0'
    obs_str = ','.join(f"'{o}'" for o in obs)
    code = f"from examples.hidden_markov import print_hmm; print_hmm([{obs_str}])"
    result = subprocess.run([sys.executable, '-c', code], capture_output=True, text=True, env=env)
    return result.stdout

def run_racket(obs):
    obs_str = ','.join(obs)
    result = subprocess.run(['racket', racket_script, obs_str], capture_output=True, text=True)
    return result.stdout

def print_diff(a, b, fromfile, tofile):
    a_lines = a.strip().splitlines()
    b_lines = b.strip().splitlines()
    diff = list(unified_diff(a_lines, b_lines, fromfile=fromfile, tofile=tofile, lineterm=''))
    if diff:
        print('\n'.join(diff))
    else:
        print('[MATCH] Python and Racket outputs are identical.')

def main():
    for obs in test_cases:
        print(f"\n=== Test case: {obs} ===\n")
        py_out = run_python(obs)
        racket_out = run_racket(obs)
        print("--- Python output ---")
        print(py_out)
        print("--- Racket output ---")
        print(racket_out)
        print("--- Unified Diff ---")
        print_diff(py_out, racket_out, 'python', 'racket')

if __name__ == '__main__':
    main()
