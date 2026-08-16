title: gr-bbc
brief: Use Baird, Bahn and Collins' algorithm (BBC) to encode and decode signals
tags:
  - secure communications
  - codec
  - bbc
  - jam resistance
author:
  - James Morrison <jamescmorrison00@gmail.com>
copyright_owner:
  - James Morrison <jamescmorrison00@gmail.com>
dependencies:
  - gnuradio (>= 3.10.0)
repo: https://github.com/xeno00/gr-bbc
stable_release: HEAD
---

This project implements Baird, Bahn and Collins' **BBC codec** in GNU Radio.
See the [GRCon22 events page](https://events.gnuradio.org/event/18/contributions/278/)
for background and use cases, or watch the GRCon22 presentation
[here](https://youtu.be/I3QmZwdsavE&t=7h38m45s).

The BBC algorithm assumes an asymmetric Z channel, where a mark (a bit with
value 1) can be added but cannot be removed. On-off keying is a straightforward
physical layer for such a channel.

These blocks perform BBC encoding and decoding around the physical layer:

* `bbc_encoder` encodes a message by hashing each prefix and placing a mark at
  a pseudo-random location in the codeword.
* `bbc_decoder` reverses the process with an iterative prefix reconstruction
  search, and can recover several messages from one codeword.
* `OOKModulator` and `OOKDemodulator` provide a matching on-off keyed physical
  layer.

The codec itself lives in `bbc.codec` and does not import GNU Radio, so it can
also be driven from a plain Python script.

Examples:

* `bbc_loopback.grc` — the smallest encode/decode round trip.
* `bbc_concurrent_codes.grc` — two messages OR'd into one codeword, both
  recovered.
* `bbc_ook_jammed.grc` — BBC over OOK, recovered with a jammer at equal power.
* `bbc_fhss_control.grc` — a jam-resistant control channel that commands a
  frequency hop for another signal.
* `bbc_zmq_bridge.grc` with `zmq_tx_bbc.py` and `zmq_receive_bbc.py` — encode
  outside GNU Radio and feed a running flow graph over ZeroMQ, so the payload
  can change without restarting it.
