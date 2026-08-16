#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright 2022 James Morrison.
#
# SPDX-License-Identifier: GPL-3.0-or-later
#
"""Glowworm hash used by the BBC (Baird, Bahn, Collins) concurrent codec.

The glowworm is a reversible, bit-at-a-time hash over a 32-word x 64-bit shift
register.  ``add_bit`` folds one message bit into the register and returns the
new head word, which the codec reduces modulo the codeword length to pick the
location of a mark.  ``del_bit`` undoes exactly one ``add_bit``, which is what
makes the decoder's depth-first search affordable: backtracking one level costs
one register update instead of re-hashing the whole prefix.

Encoder and decoder must walk identical register states, so both sides import
this module rather than keeping private copies.
"""

MASK64 = 0xFFFFFFFFFFFFFFFF

# Register geometry and warm-up, per the reference implementation.
STATE_WORDS = 32
INIT_ROUNDS = 4096


class Glowworm(object):
    """Reversible bit-at-a-time hash over a 32 x 64-bit shift register.

    State lives on the instance.  Earlier revisions of this module kept ``s``
    and ``n`` as module globals, which meant two blocks in the same flowgraph
    silently corrupted each other's register.
    """

    def __init__(self):
        self.s = [0] * STATE_WORDS
        self.n = 0
        self._warm_up()
        # Snapshot so reset() is a copy instead of another 4096 rounds.
        self._initial_state = list(self.s)

    def _warm_up(self):
        """Run the fixed key schedule that seeds the register."""
        self.s = [0] * STATE_WORDS
        self.n = 0
        h = 1
        for _ in range(INIT_ROUNDS):
            h = self.add_bit(h & 1)
        self.n = 0

    def reset(self):
        """Return the register to its seeded state, ready for a new codeword."""
        self.s[:] = self._initial_state
        self.n = 0

    def add_bit(self, b):
        """Fold bit ``b`` into the register and return the new head word."""
        s = self.s
        n = self.n
        t = s[n % STATE_WORDS] ^ (MASK64 if b else 0)
        t = ((t | (t >> 1)) ^ ((t << 1) & MASK64)) & MASK64
        t = (t ^ (t >> 4) ^ (t >> 8) ^ (t >> 16) ^ (t >> 32)) & MASK64
        n += 1
        s[n % STATE_WORDS] ^= t
        self.n = n
        return s[n % STATE_WORDS]

    def del_bit(self, b):
        """Undo the ``add_bit(b)`` that most recently advanced the register.

        ``b`` must be the same value that was added, otherwise the register is
        left in a state neither side can recover from.
        """
        self.n -= 1
        self.add_bit(b)
        self.n -= 1
        return self.s[self.n % STATE_WORDS]
