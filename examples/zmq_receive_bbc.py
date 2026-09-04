#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright 2022 James Morrison.
#
# SPDX-License-Identifier: GPL-3.0-or-later
#
"""Print BBC messages that a flow graph pushes out over ZeroMQ.

The counterpart to `zmq_tx_bbc.py`: that script feeds codewords into a flow
graph, this one reads whatever the flow graph managed to decode back out. Pair
it with `bbc_zmq_bridge.grc`, or with any flow graph whose ZMQ PUSH Sink is fed
by the decoder's stream output.

    ./zmq_receive_bbc.py --message-length 32

This script CONNECTS, because GNU Radio's ZMQ PUSH Sink binds by default.
Messages arrive as raw bytes, a whole number of decoded messages per part.
"""

import argparse
import sys

import zmq

DEFAULT_ADDRESS = 'tcp://127.0.0.1:5556'


def printable(message):
    text = message.rstrip(b'\x00')
    try:
        return text.decode('utf-8')
    except UnicodeDecodeError:
        return repr(text)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-m', '--message-length', type=int, default=32,
                        help='message size in bytes (default: %(default)s)')
    parser.add_argument('-a', '--address', default=DEFAULT_ADDRESS,
                        help='ZeroMQ address to connect (default: %(default)s)')
    parser.add_argument('-n', '--count', type=int, default=0,
                        help='exit after this many messages (0 = run forever)')
    parser.add_argument('-t', '--timeout', type=float, default=0,
                        help='exit after this many idle seconds (0 = never)')
    parser.add_argument('-u', '--unique', action='store_true',
                        help='only print messages not seen before')
    args = parser.parse_args()

    context = zmq.Context()
    socket = context.socket(zmq.PULL)
    socket.connect(args.address)
    if args.timeout:
        socket.setsockopt(zmq.RCVTIMEO, int(args.timeout * 1000))
    print("connected %s, %d byte messages"
          % (args.address, args.message_length), file=sys.stderr)

    seen = set()
    count = 0
    try:
        while True:
            try:
                part = socket.recv()
            except zmq.Again:
                print("idle for %gs, exiting" % args.timeout, file=sys.stderr)
                break

            # A part may carry several messages back to back.
            for offset in range(0, len(part), args.message_length):
                message = part[offset:offset + args.message_length]
                if len(message) < args.message_length:
                    break
                if args.unique:
                    if message in seen:
                        continue
                    seen.add(message)
                print(printable(message), flush=True)
                count += 1
                if args.count and count >= args.count:
                    return 0
    except KeyboardInterrupt:
        pass
    finally:
        socket.close(linger=0)
        context.term()
        print("received %d messages" % count, file=sys.stderr)
    return 0


if __name__ == '__main__':
    sys.exit(main())
