# Changelog

All notable changes to this project are documented here. The project follows
[Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added

- Automated codec and GNU Radio block tests.
- GitHub Actions validation on supported Ubuntu and GNU Radio versions.
- Search limits for malformed or dense BBC codewords.
- Modern CGRAN `MANIFEST.yml` metadata and installed examples.
- Contributor, security, and maintenance documentation.

### Changed

- Migrated to the GNU Radio 3.10 pure-Python OOT package layout.
- Replaced process-global codec state with per-operation reversible registers.
- Reimplemented the decoder as a scheduler-correct variable-output block.
- Clarified OOK carrier-offset semantics and made envelope detection independent
  of a fixed band-pass filter.
- Replaced the OOK block's infinite carrier source with a synchronous rotator so
  finite input flowgraphs terminate correctly.
- Updated GRC block definitions to import `gnuradio.bbc`.

### Removed

- Unused SWIG, C++, Doxygen, PyBOMBS-era, and generated flowgraph scaffolding.

## [0.1.0] - 2022-09-30

- Initial public release presented at GRCon22.
