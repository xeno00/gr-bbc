# **BBC Anti-Jam Communications**: gr-bbc

Baird, Bahn and Collins' **BBC concurrent codec** for GNU Radio 3.10+.

Read our [paper](https://pubs.gnuradio.org/index.php/grcon/article/view/127) for
background and use cases, or watch the GRCon22 presentation
[here](https://youtu.be/I3QmZwdsavE&t=7h38m45s).

## What BBC does

BBC targets an asymmetric **Z channel**: a mark (a 1 bit) can be *added* to a
codeword by noise or by a jammer, but never removed. On-off keying is the
natural physical layer for such a channel.

Encoding walks the message one bit at a time, hashing the prefix so far and
setting a single mark at the resulting pseudo-random location in a much longer
codeword. Decoding replays that walk as a depth-first search: a prefix is
plausible only if its mark is present, so the search prunes hard even when most
of the codeword has been jammed to 1.

Because marks are only ever added, several independently encoded messages can
be OR'd into one codeword and all of them still decode. That is the "concurrent
codes" property BBC is named for, and it is what makes the code jam resistant
without a shared secret.

## Requirements

- GNU Radio **3.10** or newer, built with Python support
- Python 3.7+, NumPy

gr-bbc is pure Python. There is no C++ to compile and no SWIG or pybind11
bindings to generate.

## Build and install

```sh
mkdir -p build && cd build
cmake ..
make
sudo make install
sudo ldconfig
```

Run the test suite with `ctest` from the build directory.

## Blocks

| Block | Purpose |
| --- | --- |
| **BBC Encoder** | Message vector in, codeword vector out |
| **BBC Decoder** | Codeword vector in, decoded message vectors out, plus a `decoded` message port |
| **OOK Modulator** | Packed bytes to on-off keyed complex baseband |
| **OOK Demodulator** | On-off keyed complex baseband back to packed bytes |

Sizes are given in **bytes** and set the vector lengths of the stream ports.
The default 128 B message in a 128 KiB codeword is a 1024x expansion.

The encoder and decoder must agree on message length, codeword length **and
checksum length**, or nothing decodes.

### The checksum

Each message carries a few check bits derived from its content. The decoder
*forces* those bits rather than searching them, so a wrong branch simply fails
to find its mark and gets pruned. Without them a heavily jammed codeword
produces a flood of false decodes — at 80% mark density, a 32-bit checksum cut
a run from thousands of candidates to exactly one. It defaults to 32 bits;
set it to 0 to disable.

### Using the codec without GNU Radio

`bbc.codec` imports nothing from GNU Radio, so a challenge author or solver can
drive it from a plain script:

```python
from bbc.codec import Encoder, Decoder

encoder = Encoder(message_length=8, codeword_length=1024)
decoder = Decoder(message_length=8, codeword_length=1024)
codeword = encoder.encode(b"GRCon26!")
print(decoder.decode(codeword))      # [b'GRCon26!']
```

`examples/bbc_decode_file.py` wraps that up for captures on disk, including a
`--search` mode for when the parameters are unknown.

## Examples

| Flow graph | Shows |
| --- | --- |
| `bbc_loopback.grc` | The smallest encode/decode round trip |
| `bbc_concurrent_codes.grc` | Two messages OR'd into one codeword, both recovered |
| `bbc_ook_jammed.grc` | BBC over OOK, recovered with a jammer at equal power |
| `bbc_fhss_control.grc` | A jam-resistant control channel commanding a frequency hop |
| `bbc_zmq_bridge.grc` | Codewords in and messages out over ZeroMQ |

### Driving a flow graph over ZeroMQ

`zmq_tx_bbc.py` encodes messages and pushes the codewords to a running flow
graph; `zmq_receive_bbc.py` reads whatever came back out. Keeping the encoder
outside GNU Radio means the payload can be changed, or rotated on a timer,
without regenerating or restarting the flow graph.

```sh
python3 bbc_zmq_bridge.py &            # generated from bbc_zmq_bridge.grc
./zmq_receive_bbc.py -m 32 &
./zmq_tx_bbc.py "FLAG{...}" -m 32 --repeat --interval 2
```

The TX script binds and the flow graph connects, so they can start in either
order and the sender can be restarted underneath a running flow graph. One
ZeroMQ message carries exactly one codeword, which is what keeps the receiving
stream aligned to codeword boundaries — see the framing note below. Both
scripts need `pyzmq`, which GNU Radio already pulls in for `gr-zeromq`.

## Notes and limitations

- **No framing.** Codeword boundaries are positional. The OOK modulator and
  demodulator are bit transparent — demodulated bit *j* is modulated bit *j* —
  which is what lets a flow graph slice the received stream straight back into
  codeword vectors. Anything that disturbs that alignment (a real radio, a
  capture that starts mid-codeword) needs a preamble you supply yourself.
- **Open-loop symbol timing.** The demodulator cancels the group delay it knows
  about but has no timing recovery, so it will not track a transmitter whose
  clock differs from its own.
- **Bias the slicer low.** A spurious mark costs the decoder a little search
  effort; a *dropped* mark breaks the message outright. The default threshold
  sits well below the halfway point on purpose. A threshold near zero is not
  "safer" — it turns any noise floor into a solid wall of marks.
- **Search limits.** A codeword saturated with marks makes every branch look
  plausible, so the decoder stops at `max_candidates` or `max_steps` and logs a
  warning. A truncated search can miss the real message, which is the strongest
  reason to leave the checksum enabled.
- The `carrier_freq` on the OOK blocks is a **baseband offset**, not an RF
  frequency; keep its magnitude below half the sample rate and set the real
  frequency on your sink block.
