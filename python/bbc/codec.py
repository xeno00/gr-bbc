#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright 2022 James Morrison.
#
# SPDX-License-Identifier: GPL-3.0-or-later
#
"""Pure-Python BBC (Baird, Bahn, Collins) concurrent codec.

This module deliberately imports nothing from GNU Radio, so the codec can be
driven from a plain script -- handy when writing or solving a challenge around
a captured codeword.

BBC targets an asymmetric Z channel: a mark (a 1 bit) can be added to the
codeword by noise or by a jammer, but never removed.  Encoding walks the
message one bit at a time, hashing the prefix so far and setting a single mark
at the resulting pseudo-random location.  Decoding replays that walk as a
depth-first search: a prefix is plausible only if its mark is present, so the
search prunes hard even when most of the codeword has been jammed to 1.

Because marks can only be added, several independently encoded messages may be
OR'd into one codeword and all of them still decode -- the "concurrent codes"
property BBC is named for.

Lengths are given in *bytes* at this interface; the bit-level arithmetic is
internal.
"""

import hashlib

from .glowworm import Glowworm

# Default number of check bits appended to each message. These are forced
# rather than searched during decode, so they prune false decodes instead of
# multiplying them. 32 bits costs 32 extra marks and removes essentially all
# false positives even under heavy jamming; 0 disables the feature.
DEFAULT_CHECKSUM_BITS = 32

#: Zero-fill: append plain zero bits, as described in the GRCon 2022 paper and
#: as implemented upstream. This is the interoperable wire format.
CHECKSUM_ZEROS = 'zeros'

#: SHA-256 derived check bits. A local extension, NOT interoperable with any
#: published BBC implementation. Measured against zero-fill it prunes exactly
#: as well and no better -- the pruning comes from the mark locations depending
#: on the message prefix through the glowworm, not from the check-bit values --
#: so there is no reason to prefer it. Kept only for existing captures.
CHECKSUM_SHA256 = 'sha256'

CHECKSUM_MODES = (CHECKSUM_ZEROS, CHECKSUM_SHA256)

DEFAULT_CHECKSUM_MODE = CHECKSUM_ZEROS


class BbcError(ValueError):
    """Raised for parameter combinations the codec cannot honour."""


def checksum_bits(message, num_bits, mode=DEFAULT_CHECKSUM_MODE):
    """Return ``num_bits`` deterministic check bits for ``message``.

    The bits are *forced* during decode rather than searched, so what prunes a
    false path is that its glowworm state puts the check marks somewhere else
    -- not the bit values themselves. Plain zeros therefore work as well as any
    hash, which is what the published algorithm uses.
    """
    if num_bits <= 0:
        return []
    if mode == CHECKSUM_ZEROS:
        return [0] * num_bits
    if mode != CHECKSUM_SHA256:
        raise BbcError("unknown checksum mode %r; expected one of %r"
                       % (mode, list(CHECKSUM_MODES)))
    digest = hashlib.sha256(bytes(message)).digest()
    if num_bits > len(digest) * 8:
        raise BbcError(
            "checksum_bits: %d bits requested, at most %d available"
            % (num_bits, len(digest) * 8))
    return [(digest[i >> 3] >> (i & 7)) & 1 for i in range(num_bits)]


class _CodecBase(object):
    """Shared parameter validation and glowworm ownership."""

    def __init__(self, message_length, codeword_length, checksum_length,
                 checksum_mode=DEFAULT_CHECKSUM_MODE):
        if message_length <= 0 or codeword_length <= 0:
            raise BbcError("message and codeword lengths must be positive")
        if checksum_length < 0:
            raise BbcError("checksum length must not be negative")
        if checksum_mode not in CHECKSUM_MODES:
            raise BbcError("unknown checksum mode %r; expected one of %r"
                           % (checksum_mode, list(CHECKSUM_MODES)))
        if codeword_length <= message_length:
            raise BbcError(
                "codeword (%d B) must be longer than the message (%d B); BBC "
                "needs a sparse codeword to stay jam resistant"
                % (codeword_length, message_length))

        self.message_length = int(message_length)
        self.codeword_length = int(codeword_length)
        self.checksum_length = int(checksum_length)
        self.checksum_mode = checksum_mode

        self.msg_bits = self.message_length * 8
        self.cod_bits = self.codeword_length * 8
        self.total_bits = self.msg_bits + self.checksum_length

        self.glowworm = Glowworm()


class Encoder(_CodecBase):
    """Turn a fixed-length message into a fixed-length BBC codeword."""

    def __init__(self, message_length, codeword_length,
                 checksum_length=DEFAULT_CHECKSUM_BITS,
                 checksum_mode=DEFAULT_CHECKSUM_MODE):
        _CodecBase.__init__(self, message_length, codeword_length,
                            checksum_length, checksum_mode)

    def encode(self, message):
        """Encode ``message`` (bytes-like, ``message_length`` long).

        Returns a ``bytearray`` of ``codeword_length`` bytes.
        """
        message = bytes(message)
        if len(message) != self.message_length:
            raise BbcError("expected a %d-byte message, got %d bytes"
                           % (self.message_length, len(message)))

        # Every codeword starts from the seeded register. Without this the
        # second and later messages hash against a register the decoder has
        # already unwound, and nothing downstream decodes.
        glowworm = self.glowworm
        glowworm.reset()

        codeword = bytearray(self.codeword_length)
        for i in range(self.msg_bits):
            bit = (message[i >> 3] >> (i & 7)) & 1
            loc = glowworm.add_bit(bit) % self.cod_bits
            codeword[loc >> 3] |= 1 << (loc & 7)

        for bit in checksum_bits(message, self.checksum_length,
                                 self.checksum_mode):
            loc = glowworm.add_bit(bit) % self.cod_bits
            codeword[loc >> 3] |= 1 << (loc & 7)

        return codeword


class Decoder(_CodecBase):
    """Recover every message consistent with a received BBC codeword.

    A codeword can legitimately carry more than one message, so ``decode``
    returns a list.  Under heavy jamming the search space grows quickly, which
    is what ``max_candidates`` and ``max_steps`` bound: a run that trips either
    limit returns what it found so far and sets :attr:`truncated`.
    """

    # Generous enough that clean and moderately jammed codewords never trip
    # them, tight enough that a fully jammed codeword cannot wedge a flowgraph.
    DEFAULT_MAX_CANDIDATES = 256
    DEFAULT_MAX_STEPS = 5_000_000

    def __init__(self, message_length, codeword_length,
                 checksum_length=DEFAULT_CHECKSUM_BITS,
                 max_candidates=DEFAULT_MAX_CANDIDATES,
                 max_steps=DEFAULT_MAX_STEPS,
                 checksum_mode=DEFAULT_CHECKSUM_MODE):
        _CodecBase.__init__(self, message_length, codeword_length,
                            checksum_length, checksum_mode)
        self.max_candidates = int(max_candidates)
        self.max_steps = int(max_steps)
        #: True when the last decode hit ``max_candidates`` or ``max_steps``.
        self.truncated = False
        #: Search steps taken by the last decode, useful for tuning.
        self.steps = 0

    def decode(self, packet):
        """Return the list of messages consistent with ``packet``."""
        packet = bytes(packet)
        if len(packet) != self.codeword_length:
            raise BbcError("expected a %d-byte codeword, got %d bytes"
                           % (self.codeword_length, len(packet)))

        glowworm = self.glowworm
        # The search unwinds to the seeded state on its own, but resetting
        # makes each packet independent of however the previous one ended.
        glowworm.reset()

        self.truncated = False
        self.steps = 0

        msg_bytes = self.message_length
        # Working message: the message bits plus room for the check bits.
        candidate = bytearray(msg_bytes + (self.checksum_length + 7) // 8)
        results = []
        n = 0

        while True:
            self.steps += 1
            if self.steps > self.max_steps:
                self.truncated = True
                break

            if self.checksum_length and n == self.msg_bits:
                # The message bits are now fixed, so the check bits are too.
                # Force them instead of searching both branches: a wrong guess
                # below simply fails to find its mark and gets pruned.
                for j, value in enumerate(
                        checksum_bits(candidate[:msg_bytes],
                                      self.checksum_length,
                                      self.checksum_mode)):
                    i = self.msg_bits + j
                    if value:
                        candidate[i >> 3] |= 1 << (i & 7)
                    else:
                        candidate[i >> 3] &= 0xFF ^ (1 << (i & 7))

            proposed = (candidate[n >> 3] >> (n & 7)) & 1
            loc = glowworm.add_bit(proposed) % self.cod_bits
            mark_present = (packet[loc >> 3] >> (loc & 7)) & 1

            if mark_present:
                if n < self.total_bits - 1:
                    # Descend, trying 0 first for the next message bit. Check
                    # bits are overwritten above, so only reset message bits.
                    n += 1
                    if n < self.msg_bits:
                        candidate[n >> 3] &= 0xFF ^ (1 << (n & 7))
                    continue

                # Every bit found its mark: a complete message.
                results.append(bytes(candidate[:msg_bytes]))
                if len(results) >= self.max_candidates:
                    self.truncated = True
                    break
                # Fall through and backtrack to look for further messages.

            # Backtrack. Check bits were forced, so unwind them wholesale
            # rather than exploring their alternate branch.
            while n >= self.msg_bits:
                glowworm.del_bit((candidate[n >> 3] >> (n & 7)) & 1)
                n -= 1

            # Unwind message bits already set to 1 -- both branches are spent.
            while n >= 0 and ((candidate[n >> 3] >> (n & 7)) & 1) == 1:
                glowworm.del_bit(1)
                candidate[n >> 3] &= 0xFF ^ (1 << (n & 7))
                n -= 1

            if n < 0:
                break  # Search exhausted; the register is back at its seed.

            # Retry the current bit as a 1.
            glowworm.del_bit(0)
            candidate[n >> 3] |= 1 << (n & 7)

        if self.truncated:
            # An aborted search leaves the register mid-walk.
            glowworm.reset()

        return results
