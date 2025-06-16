# Rust gRPC Microservice

This project provides a gRPC microservice in Rust (using tonic) for ranking logic, intended to be called from Python clients for integration testing.

## Structure
- `src/` — Rust source code
- `proto/` — Protobuf definitions
- `Makefile` — Build/test automation
- `.github/copilot-instructions.md` — Copilot customization

## Quickstart

1. Install Rust (https://rustup.rs/) and protoc (https://grpc.io/docs/protoc-installation/).
2. Build the project:
   ```sh
   make build
   ```
3. Run the service:
   ```sh
   make run
   ```
4. Run tests:
   ```sh
   make test
   ```

## Python Client
- See `proto/` for protobuf definitions to generate Python client code.

## TDD & CI
- Add tests in `tests/` and integrate with your CI system.
