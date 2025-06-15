# LLM Implementation Introduction

This file is intended to establish the base implementation guidelines for LLM coding partners. LLM coding partners should work to ensure these guidelines are closely followed to help ensure consistent code quality.

## Implementation Guidelines
- All code changes must be made in a feature branch, not directly in the master branch.
  - Check that the feature branch is up-to-date with the master branch before starting work.
  - Check that a freature branch has been created before starting work.
- A TDD methodology will be followed for all code changes to ensure expectations are explicitly stated in a testable format.
  - Write tests for new features and edge cases before or alongside implementation.
- Install and use logging and tracing to debug and understand code behavior.
- All tests must pass after every code edit that impacts code logic and before any commits. This includes:
  - Adding new tests for new features or edge cases.
  - Running the full test suite to ensure no regressions.
  - If the logic requires changes to existing tests, gain approval from the local maintainer before making changes.
- All code and docstrings should have minimal example usage and edge case documentation.
- All code and docstrings must be Sphinx-compatible and use a literate, readable style To maintain Sphinx compatability for documentation:
  - Do not use single backticks for inline code; use double backticks for inline code. 
  - Avoid using Markdown-style triple backticks; use double colons and indentation for code blocks in reStructuredText.
  - Ensure all emphasis/strong markers are properly closed.
  - Escape asterisks in docstrings by using double backticks (``*args`` and ``**kwargs``) in both the Args section and anywhere else they appear.
- Treat Sphinx warnings as errors
  - Fix Sphinx warnings and errors for any documentation that has warnings or errors after any docstring or documentation edit.
- Follow PEP8 and use `black` for code formatting.
- Use descriptive commit messages and create feature branches for significant changes.
- After logic changes, always commit your changes with a descriptive message and push to the remote repository (i.e., run `git commit` and `git push`).