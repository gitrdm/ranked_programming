# Base Case Development Guidelines

This file is intended to capture the core development standards and requirements for this project. Please update and maintain this file as the single source of truth for all contributors and for automated tools.

## Requirements

- All tests must pass after every code edit that impacts code logic and before any commits.
- All code and docstrings must be Sphinx-compatible and use a literate, readable style.
- For documentation, do not use single backticks; use double backticks for inline code.
- For documentation, avoid using Markdown-style triple backticks; use double colons and indentation for code blocks in reStructuredText.
- For documentation, ensure all emphasis/strong markers are properly closed.
- For documentation, escape asterisks in docstrings by using double backticks (``*args`` and ``**kwargs``) in both the Args section and anywhere else they appear.
- Sphinx documentation must build without warnings after any docstring or documentation edit.
- Test-driven development (TDD) methodology should be followed: write tests for new features and edge cases before or alongside implementation.
- All combinators and core logic should be robustly documented, including usage examples and edge case notes.
- All new or modified combinators/helpers should include appropriate logging/tracing if they impact core logic or debugging.
- All public combinators must be exported from `rp_core.py` and documented in the Sphinx API docs.
- Follow PEP8 and use `black` for code formatting.
- Use descriptive commit messages and create feature branches for significant changes.
- After logic changes, always commit your changes with a descriptive message and push to the remote repository (i.e., run `git commit` and `git push`).
- Any additional requirements, coding standards, or project-specific rules should be added below.

## Additional Notes

- This Project is a port of the original Racket ranked programming library by Tjitze Rienstra. The Python version aims to maintain the same core functionality and being at semantic parity while adapting to Python idioms and best practices.
- If a change only affects documentation or comments, running tests is optional unless the documentation impacts code behavior or Sphinx build output.

## Best Practice Guidance

- **Write small, focused functions:** Each function should do one thing well. If a function is getting long or complex, consider breaking it up.
- **Use meaningful names:** Name variables, functions, and classes clearly to reflect their purpose.
- **Write and run tests frequently:** Test new features and bug fixes as you go. Use TDD when possible.
- **Document as you code:** Keep docstrings up to date and write them as you implement features.
- **Keep commits small and descriptive:** Make one logical change per commit and write clear commit messages.
- **Refactor regularly:** Clean up code, remove duplication, and improve readability as you work.
- **Ask for code review:** If possible, have someone else review your code, or review it yourself after a break.
- **Handle errors gracefully:** Use exceptions and error messages to make debugging easier.
- **Keep dependencies minimal:** Only add libraries you really need, and document why they’re used.
- **Automate repetitive tasks:** Use scripts or tools for testing, formatting, and building documentation.
- **Stay consistent:** Follow the project’s style and conventions throughout the codebase.
- **Learn from mistakes:** If you encounter a bug or issue, add a test for it and document the fix.

(Add your own best practices as you learn and grow!)
