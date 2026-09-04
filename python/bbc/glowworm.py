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

The reference is Baird, Carlisle, Bahn and Smith, "The Glowworm hash: Increased
Speed and Security for BBC Unkeyed Jam Resistance", MILCOM 2012, Fig. 4::

    #define glowwormAddBit(b,s,n,t) ( \\
        t = s[n % 32] ^ ((b) ? 0xffffffff : 0), \\
        t = (t|(t>>1)) ^ (t<<1), \\
        t ^= (t>>4) ^ (t>>8) ^ (t>>16) ^ (t>>32), \\
        n++, \\
        s[n % 32] ^= t )

Note the two masks below are *different widths*, and deliberately so. The
register words are 64-bit, so the shifts wrap modulo 2**64 -- but the set-bit
inversion is only 32 bits wide even though ``s`` is declared ``unsigned long
long``. That is not an artifact of C integer widths for a Python port to
"correct": widening it to 64 bits changes every mark location and breaks
interoperability with every other BBC implementation. :data:`CHECKVALUE` exists
to catch exactly that mistake -- see :meth:`Glowworm.init_hash`.
"""

#: Width of the register words: shifts and XORs wrap modulo 2**64.
MASK64 = 0xFFFFFFFFFFFFFFFF

#: Inversion applied when the folded bit is 1. 32 bits wide, per MILCOM 2012
#: Fig. 4 -- NOT the register width. See the module docstring.
INVERT_MASK = 0xFFFFFFFF

#: Hash of the empty string, published as a conformance self-test.
CHECKVALUE = 0xCCA4220FC78D45E0

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
        #: Hash of the empty string produced by the warm-up. Equals
        #: :data:`CHECKVALUE` for a conformant implementation.
        self.init_hash = self._warm_up()
        # Snapshot so reset() is a copy instead of another 4096 rounds.
        self._initial_state = list(self.s)

    def _warm_up(self):
        """Run the fixed key schedule that seeds the register.

        Returns the hash of the empty string, so callers can check it against
        :data:`CHECKVALUE`.
        """
        self.s = [0] * STATE_WORDS
        self.n = 0
        h = 1
        for _ in range(INIT_ROUNDS):
            h = self.add_bit(h & 1)
        self.n = 0
        return h

    def reset(self):
        """Return the register to its seeded state, ready for a new codeword."""
        self.s[:] = self._initial_state
        self.n = 0

    def add_bit(self, b):
        """Fold bit ``b`` into the register and return the new head word."""
        s = self.s
        n = self.n
        t = s[n % STATE_WORDS] ^ (INVERT_MASK if b else 0)
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
