# gr-bbc

[![CI](https://github.com/xeno00/gr-bbc/actions/workflows/ci.yml/badge.svg)](https://github.com/xeno00/gr-bbc/actions/workflows/ci.yml)
[![GNU Radio](https://img.shields.io/badge/GNU%20Radio-3.10.x-blue)](https://www.gnuradio.org/)
[![License: GPL-3.0-or-later](https://img.shields.io/badge/License-GPL--3.0--or--later-blue.svg)](LICENSE)

`gr-bbc` is a pure-Python GNU Radio out-of-tree (OOT) module implementing the
Baird, Bahn, and Collins (BBC) mark-code algorithm. The module provides:

- fixed-vector BBC encoder and variable-output decoder blocks;
- dependency-free Python codec classes for testing and offline use;
- ideal noncoherent OOK modulation and demodulation blocks; and
- GNU Radio Companion examples for base, OOK, and frequency-hop scenarios.

The design and motivation are described in the
[GRCon paper](https://pubs.gnuradio.org/index.php/grcon/article/view/127) and
[GRCon22 presentation](https://www.youtube.com/watch?v=I3QmZwdsavE&t=27525s).

> [!IMPORTANT]
> BBC is a mark code intended for asymmetric channels where marks can be added
> but not removed. It does not provide encryption, authentication, or general
> protection against arbitrary interference.

## Compatibility

The maintained branch targets GNU Radio 3.10.x and Python 3. GNU Radio 4 uses
a different module API and is not supported by this branch.

CI validates the module on Ubuntu 22.04 and 24.04 using the GNU Radio packages
provided by those distributions.

## Install from source

Install GNU Radio and its development files first. On Ubuntu:

```console
sudo apt update
sudo apt install cmake gnuradio gnuradio-dev python3-numpy
```

Configure, test, and install the module:

```console
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build
ctest --test-dir build --output-on-failure
sudo cmake --install build
```

If GNU Radio was installed under a custom prefix, pass that prefix through
`CMAKE_PREFIX_PATH`. A non-root install is also supported:

```console
cmake -S . -B build \
  -DCMAKE_INSTALL_PREFIX="$HOME/.local" \
  -DCMAKE_PREFIX_PATH=/path/to/gnuradio
cmake --build build
cmake --install build
```

Ensure the corresponding Python and GRC paths under the chosen prefix are
visible to GNU Radio. Confirm the installation with:

```console
python3 -c "from gnuradio import bbc; print(bbc.__file__)"
gnuradio-companion
```

## Blocks

### BBC Encoder

Consumes byte vectors of `message_length` bytes and emits BBC codewords of
`codeword_length` bytes. Each input vector produces exactly one output vector.

### BBC Decoder

Consumes codeword vectors and emits zero or more candidate message vectors.
BBC decoding is a tree search; `max_candidates` and `max_search_nodes` bound
the work performed for malformed or unusually dense codewords.

### OOK Modulator and Demodulator

The modulator consumes packed bytes, unpacks them MSB-first, and produces a
complex OOK waveform. `carrier_frequency` is a digital offset relative to an
SDR's tuned center frequency—not an RF tuning frequency—and must remain inside
the Nyquist interval.

The demodulator performs noncoherent envelope detection on an ideally timed
waveform. It does not implement carrier or symbol synchronization. For both
blocks, `sample_rate` must be an integer multiple of `symbol_rate`.

## Pure-Python codec

The core algorithm can be used independently of a running flowgraph:

```python
from gnuradio.bbc import Decoder, Encoder

message = b"BBC"
codeword = Encoder(message_length=3, codeword_length=128).encode(message)
candidates = Decoder(message_length=3, codeword_length=128).decode(codeword)
assert message in candidates
```

## Examples

The `examples/` directory contains:

- `bbc-gr-base.grc` — codec-only vector processing;
- `bbc-gr-ook.grc` — ideal OOK loopback; and
- `bbc-gr-ook-fhss.grc` — an experimental frequency-hop demonstration.

These examples are demonstrations, not production radio designs. In
particular, real over-the-air operation requires timing recovery, RF hardware
configuration, filtering, gain control, and regulatory compliance.

## Development and maintenance

See [CONTRIBUTING.md](CONTRIBUTING.md) for the test and review workflow and
[SECURITY.md](SECURITY.md) for security reporting. Changes are recorded in
[CHANGELOG.md](CHANGELOG.md). Releases use semantic version tags and the
`main` branch is expected to remain buildable.

## License

GPL-3.0-or-later. See [LICENSE](LICENSE).
