#!/bin/bash
# Run all example scripts in the examples/ directory
# Usage: ./run_examples.sh [example_name.py]

EXAMPLES_DIR="examples"

if [ "$1" != "" ]; then
    # Run a specific example
    python "$EXAMPLES_DIR/$1"
    exit $?
fi

echo "Running all example scripts in $EXAMPLES_DIR..."
for script in $(ls $EXAMPLES_DIR/*.py | sort); do
    echo "\n===== Running: $script ====="
    python "$script"
    echo "===== Finished: $script =====\n"
done

echo "All examples completed."
