# Contributing

Contributions are welcome through GitHub issues and pull requests.

## Supported scope

The `main` branch supports GNU Radio 3.10.x and Python 3. GNU Radio 4 work must
remain isolated until the module has a tested GR4 design and migration plan.

## Development workflow

1. Create a focused branch from `main`.
2. Add or update tests for behavior changes.
3. Configure and run the complete test suite:

   ```console
   cmake -S . -B build -DCMAKE_BUILD_TYPE=Debug
   cmake --build build
   ctest --test-dir build --output-on-failure
   ```

4. If GRC definitions or examples changed, open them in GNU Radio Companion
   and compile the affected flowgraphs.
5. Update `CHANGELOG.md` for user-visible changes.
6. Open a pull request describing the behavior, rationale, and validation.

## Coding guidelines

- Use Python 3 type hints for new public APIs.
- Keep the codec core independent of GNU Radio.
- Do not use process-global mutable algorithm state.
- Do not print from block work functions; use Python logging for diagnostics.
- Validate constructor parameters before starting a flowgraph.
- Preserve the established least-significant-bit ordering of the BBC codec.
- Include SPDX license identifiers in new source files.

## Releases

Maintainers should only tag a release after CI passes on every supported
platform. Release tags use `vMAJOR.MINOR.PATCH`; update `project(... VERSION)`,
`MANIFEST.yml`, and `CHANGELOG.md` together before tagging.
