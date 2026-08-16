#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright 2022 James Morrison.
#
# SPDX-License-Identifier: GPL-3.0-or-later
#
"""BBC-encode messages and push the codewords to a flow graph over ZeroMQ.

This keeps the encoder outside GNU Radio. A running flow graph picks the
codewords up with a ZMQ PULL Source and transmits them, so the payload can be
changed -- or rotated on a timer -- without regenerating or restarting the
flow graph.

Pair it with `bbc_zmq_bridge.grc`, or with any flow graph whose ZMQ PULL Source
has vlen set to the codeword length and Bind left False:

    ./zmq_tx_bbc.py "FLAG{...}" --repeat --interval 2

This script BINDS the socket and the flow graph connects to it, so the two can
be started in either order. One ZeroMQ message carries exactly one codeword,
which is what keeps the receiving stream aligned to codeword boundaries.
"""

import argparse
import os
import sys
import time

import zmq

sys.path.insert(
    0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'python'))

from bbc.codec import Encoder, BbcError  # noqa: E402

DEFAULT_ADDRESS = 'tcp://127.0.0.1:5555'


def fit(message, length):
    """Pad or truncate `message` to exactly `length` bytes."""
    payload = message.encode('utf-8') if isinstance(message, str) else message
    if len(payload) > length:
        print("warning: truncating %r to %d bytes" % (payload, length),
              file=sys.stderr)
        return payload[:length]
    return payload.ljust(length, b'\x00')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('messages', nargs='*',
                        help='messages to send; reads stdin if none are given')
    parser.add_argument('-m', '--message-length', type=int, default=32,
                        help='message size in bytes (default: %(default)s)')
    parser.add_argument('-c', '--codeword-length', type=int, default=8192,
                        help='codeword size in bytes (default: %(default)s)')
    parser.add_argument('-k', '--checksum-length', type=int, default=32,
                        help='check bits per message (default: %(default)s)')
    parser.add_argument('-a', '--address', default=DEFAULT_ADDRESS,
                        help='ZeroMQ address to bind (default: %(default)s)')
    parser.add_argument('-r', '--repeat', action='store_true',
                        help='keep resending the messages in a loop')
    parser.add_argument('-i', '--interval', type=float, default=1.0,
                        help='seconds between codewords (default: %(default)s)')
    args = parser.parse_args()

    messages = args.messages
    if not messages:
        messages = [line.rstrip('\n') for line in sys.stdin if line.strip()]
    if not messages:
        parser.error('no messages to send')

    try:
        encoder = Encoder(args.message_length, args.codeword_length,
                          args.checksum_length)
    except BbcError as exc:
        parser.error(str(exc))

    # Encode once up front: the codewords are deterministic, and this reports
    # a bad message length before the socket is opened.
    codewords = [(text, bytes(encoder.encode(fit(text, args.message_length))))
                 for text in messages]

    context = zmq.Context()
    socket = context.socket(zmq.PUSH)
    socket.bind(args.address)
    print("bound %s, %d byte codewords, %d byte messages"
          % (args.address, args.codeword_length, args.message_length))

    sent = 0
    try:
        while True:
            for text, codeword in codewords:
                socket.send(codeword)
                sent += 1
                marks = sum(bin(byte).count('1') for byte in codeword)
                print("sent %r as %d marks in %d bits"
                      % (text, marks, args.codeword_length * 8))
                time.sleep(args.interval)
            if not args.repeat:
                break
    except KeyboardInterrupt:
        pass
    finally:
        # Give ZeroMQ a moment to flush before tearing the context down,
        # otherwise the last codeword can be dropped on exit.
        socket.close(linger=2000)
        context.term()
        print("sent %d codewords" % sent)
    return 0


if __name__ == '__main__':
    sys.exit(main())
