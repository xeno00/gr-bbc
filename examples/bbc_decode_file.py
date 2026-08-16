#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright 2022 James Morrison.
#
# SPDX-License-Identifier: GPL-3.0-or-later
#
"""Decode BBC codewords from a file, without GNU Radio.

Useful for working on a capture offline -- authoring a challenge around a
recorded codeword, or solving one. The input is raw bytes: a whole number of
codewords, back to back, exactly as a File Sink downstream of the encoder would
write them.

    ./bbc_decode_file.py capture.bin --message-length 8 --codeword-length 1024

If the parameters are unknown, --search tries the plausible combinations and
reports whichever ones produce a decode.
"""

import argparse
import os
import sys

sys.path.insert(
    0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'python'))

from bbc.codec import Decoder, BbcError  # noqa: E402


def printable(message):
    text = message.rstrip(b'\x00')
    try:
        return text.decode('utf-8')
    except UnicodeDecodeError:
        return repr(text)


def decode(data, message_length, codeword_length, checksum_length, quiet=False):
    decoder = Decoder(message_length, codeword_length, checksum_length)
    found = []
    for index in range(len(data) // codeword_length):
        chunk = data[index * codeword_length:(index + 1) * codeword_length]
        messages = decoder.decode(chunk)
        if decoder.truncated and not quiet:
            print("  codeword %d: search truncated after %d steps"
                  % (index, decoder.steps), file=sys.stderr)
        for message in messages:
            found.append((index, message))
    return found


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('capture', help='file of raw codeword bytes')
    parser.add_argument('-m', '--message-length', type=int, default=128,
                        help='message size in bytes (default: %(default)s)')
    parser.add_argument('-c', '--codeword-length', type=int, default=2**17,
                        help='codeword size in bytes (default: %(default)s)')
    parser.add_argument('-k', '--checksum-length', type=int, default=32,
                        help='check bits per message (default: %(default)s)')
    parser.add_argument('--search', action='store_true',
                        help='try common parameter combinations')
    args = parser.parse_args()

    with open(args.capture, 'rb') as handle:
        data = handle.read()

    if not args.search:
        try:
            found = decode(data, args.message_length, args.codeword_length,
                           args.checksum_length)
        except BbcError as exc:
            parser.error(str(exc))
        for index, message in found:
            print("codeword %d: %s" % (index, printable(message)))
        if not found:
            print("nothing decoded; try --search or check the parameters",
                  file=sys.stderr)
            return 1
        return 0

    for codeword_length in (2**n for n in range(8, 20)):
        if codeword_length > len(data):
            break
        for message_length in (2**n for n in range(0, 10)):
            if message_length >= codeword_length:
                break
            for checksum_length in (32, 0):
                found = decode(data, message_length, codeword_length,
                               checksum_length, quiet=True)
                if found:
                    print("message=%d codeword=%d checksum=%d -> %s"
                          % (message_length, codeword_length, checksum_length,
                             printable(found[0][1])))
    return 0


if __name__ == '__main__':
    sys.exit(main())
