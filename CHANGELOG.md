# Changelog

## 2.0.0 — GNU Radio 3.10 port

### Wire format

Codewords produced by this release do **not** interoperate with 1.x captures.
Two things changed:

- The glowworm hash now inverts all 64 bits of the register word for a set bit,
  matching the published algorithm. 1.x inverted only the low 32. Measured over
  heavily jammed codewords, the corrected version produces about half as many
  false decodes.
- Messages carry 32 check bits by default. Set `checksum_length` to 0 on both
  the encoder and the decoder for the old behaviour.

### Build and layout

- Ported to GNU Radio 3.10. SWIG was removed from GNU Radio in 3.9; the `swig/`
  directory is gone, and since gr-bbc is pure Python there are no pybind11
  bindings to replace it.
- Python sources moved to `python/bbc/` to match the 3.10 module layout.
- Removed the empty C++ scaffolding — `lib/`, `include/`, the Doxygen tree with
  its SWIG docstring generator, and the C++ CMake export helpers. They built
  nothing and only offered ways for the build to fail.
- Added a `ctest` suite covering the codec, both blocks, and the OOK physical
  layer.

### Correctness

- **The encoder never reset its shift register between messages.** Only the
  first message in a stream ever decoded; every later one was hashed against a
  register the decoder had already unwound. The register is now reset per
  codeword.
- **The decoder left its search index at -1 after each packet**, so a reused
  decoder started the next packet indexing off the front of the buffer. The
  index is now local to a decode.
- **The encoder encoded only the first vector of each `work()` call** but
  returned the full item count, so everything after the first vector in a batch
  went out as an unrelated codeword. It now encodes every vector.
- **The decoder was a `gr.interp_block` calling `set_relative_rate()` at
  runtime.** A codeword can carry zero, one, or several messages, which a fixed
  rate cannot express. It is now a `gr.basic_block` with an internal queue, and
  also publishes each message on a `decoded` PMT port.
- The glowworm register lived in module globals, so two blocks in one flow
  graph corrupted each other's state. It is now a `Glowworm` class shared by
  both the encoder and decoder rather than copy-pasted into each.
- Stream types changed from `np.byte` (signed) to `np.uint8`. The signed type
  is what produced the "Fix integer max in byte output" failures, and under
  NumPy 2 it raises instead of wrapping.
- The decoder's checksum backtracking called `del_bit(0)` regardless of the bit
  actually added, which corrupts the register. It now unwinds the real value.
- Added `max_candidates` and `max_steps`. A codeword saturated with marks
  previously ran unbounded — one measured case produced 161,000 false messages
  from 1.7 million search steps.
- Parameters are now validated: a codeword must be longer than its message, and
  message and codeword lengths must match what the block was built for.

### OOK physical layer

- **The demodulator's band-pass filter was hard-coded to 50 kHz** regardless of
  the carrier in use, and its group delay was never accounted for. The filter
  now tracks `carrier_freq`, and the sampler discards exactly the group delay,
  which puts the integrator window on symbol boundaries.
- Modulator and demodulator are now **bit transparent**: demodulated bit *j* is
  modulated bit *j*. Without this a flow graph cannot slice the received stream
  back into codeword vectors, since there is no framing.
- Added an integrate-over-a-symbol stage before decimation, so slicing uses
  accumulated symbol energy rather than one arbitrarily timed instant.
- **The slicer threshold defaulted to 1e-3**, which declares a mark on any
  energy at all and turns the faintest noise floor into a wall of marks. It now
  defaults to 0.25 — still biased low, as the Z channel wants, but usable.
- The modulator's default carrier was 433.937e6 at a 128 kHz sample rate, more
  than 3000x past Nyquist. `carrier_freq` is documented as a baseband offset
  and the GRC block asserts it stays below half the sample rate.
- Both blocks now reject a sample rate below the symbol rate instead of failing
  later inside `firdes`.
- Replaced the GRC-generated hier blocks — 675 lines of inlined GPL text apiece
  — with hand-maintained sources, and dropped the duplicate copies in `blocks/`.

### GRC and examples

- The OOK hier block definitions imported `from OOKModulator import ...`, which
  cannot resolve once installed into the `bbc` package, and filed themselves
  under `[GRC Hier Blocks]`. Both are fixed, and all four blocks now carry
  documentation and parameter validation.
- The old `bbc-gr-ook.grc` and `bbc-gr-ook-fhss.grc` embedded their own copies
  of the buggy codec as Embedded Python Blocks, and referenced hier block IDs
  that no longer exist. All example flow graphs were rebuilt against the
  installed blocks and verified end to end:
  `bbc_loopback.grc`, `bbc_concurrent_codes.grc`, `bbc_ook_jammed.grc`, and
  `bbc_fhss_control.grc` (which replaces the FHSS demo).
- Several old flow graphs declared the same variable name twice, which GRC
  rejects.
- Added `examples/bbc_decode_file.py` for decoding captures offline, with a
  `--search` mode for unknown parameters.
- Added a ZeroMQ path so the encoder can live outside GNU Radio and feed a
  running flow graph: `zmq_tx_bbc.py` encodes and pushes codewords,
  `bbc_zmq_bridge.grc` decodes them and pushes the messages back out, and
  `zmq_receive_bbc.py` prints those. The sender binds and the flow graph
  connects, so the payload can be rotated without restarting the flow graph.
  `zmq_receive_bbc.py` was rewritten for this: it previously dumped raw
  buffers, and after the old flow graphs were replaced it paired with nothing.
