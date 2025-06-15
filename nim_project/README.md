# Nim Port of Ranked Programming

This directory contains a Nim implementation of the ranked programming library, targeting a C API for SWIG-based Python bindings.

## Structure
- `src/` — Nim source code
- `tests/` — Nim tests
- `capi/` — C header and SWIG interface files
- `build/` — Build artifacts

## Build/Interop Goals
- Nim code exposes a C-compatible API (using `exportc`)
- SWIG interface files wrap the C API for Python
- Python tests validate the bindings

## Getting Started
- Requires: Nim, Nimble, SWIG, Python (with dev headers), and a C compiler
- To build: See instructions in this README as the project develops

## Status
- Initial scaffold only. Core logic and bindings to be implemented.
