<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

This project is a Rust gRPC microservice (using tonic) intended to be called from Python clients for integration testing. Please follow idiomatic Rust, TDD, and microservice best practices. The goal is to port the Python version of ranked programming to Rust, ensuring it is idiomatic and efficient and allowing clients to call it from Python.
This project is currently "housed" under the Python port of ranked programming to facilitate porting, but it is intended to be a standalone Rust microservice that can be called from Python clients.

## Implementation Guidelines
- A Design-by-Contract (DbC) methodology will be followed for all applicable code blocks to ensure code block expectations are explicitly stated and are tested.
- A TDD (Test-Driven Development) methodology will be followed for all code changes to ensure expectations are explicitly stated in a testable format.
  - Write tests for new features and edge cases before or alongside implementation.
- Install and use logging and tracing to debug and understand code behavior.
  - Provide recommendations for logging and tracing in the codebase.
- Provide recommendations for "best practices" for coding logic, program structure, and code organization.
- All tests must pass after every code edit that impacts code logic and before any commits. This includes:
  - Adding new tests for new features or edge cases.
  - Running the full test suite to ensure no regressions.
- All code should have docstrings should have minimal example usage and edge case documentation.
- Use descriptive commit messages and create feature branches for significant changes.
- After logic changes, always commit your changes with a descriptive message and push to the remote repository (i.e., run `git commit` and `git push`).
