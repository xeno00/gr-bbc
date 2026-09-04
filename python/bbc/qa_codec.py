#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright 2022 James Morrison.
#
# SPDX-License-Identifier: GPL-3.0-or-later
#
"""Tests for the pure-Python codec. These do not need GNU Radio."""

import os
import random
import sys
import unittest

if __package__ in (None, ''):
    # Running the file directly from the source tree: make `python/` importable
    # so `bbc` resolves the same way it will once installed.
    sys.path.insert(
        0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bbc.codec import (Encoder, Decoder, BbcError, checksum_bits,
                       CHECKSUM_ZEROS, CHECKSUM_SHA256,
                       DEFAULT_CHECKSUM_MODE)
from bbc.glowworm import Glowworm, CHECKVALUE, INVERT_MASK, MASK64

MSG_LEN = 8
COD_LEN = 2**12


def jam(codeword, fraction, seed):
    """Add marks to `fraction` of the codeword's bit positions."""
    rng = random.Random(seed)
    jammed = bytearray(codeword)
    for _ in range(int(len(jammed) * 8 * fraction)):
        bit = rng.randrange(len(jammed) * 8)
        jammed[bit >> 3] |= 1 << (bit & 7)
    return jammed


class TestGlowwormConformance(unittest.TestCase):
    """Baird et al., MILCOM 2012, Fig. 4 published a self-test constant.

    glowwormInit() returns the hash of the empty string, which must equal
    CHECKVALUE. Nothing asserted this before, which is how a one-character
    change to the inversion mask silently altered every mark location.
    """

    def test_init_hash_matches_published_checkvalue(self):
        self.assertEqual(Glowworm().init_hash, CHECKVALUE,
                         "glowworm does not match the published CHECKVALUE; "
                         "the wire format is not interoperable")

    def test_inversion_mask_is_32_bits(self):
        # The register words are 64-bit but the set-bit inversion is not, and
        # widening it is exactly the mistake CHECKVALUE catches.
        self.assertEqual(INVERT_MASK, 0xFFFFFFFF)
        self.assertEqual(MASK64, 0xFFFFFFFFFFFFFFFF)

    def test_widening_the_mask_breaks_the_checkvalue(self):
        """Guard the guard: prove the test would catch the regression."""
        state = [0] * 32
        n = 0
        h = 1
        for _ in range(4096):
            t = state[n % 32] ^ (MASK64 if (h & 1) else 0)
            t = ((t | (t >> 1)) ^ ((t << 1) & MASK64)) & MASK64
            t = (t ^ (t >> 4) ^ (t >> 8) ^ (t >> 16) ^ (t >> 32)) & MASK64
            n += 1
            state[n % 32] ^= t
            h = state[n % 32]
        self.assertNotEqual(h, CHECKVALUE)


class TestGlowworm(unittest.TestCase):

    def test_reset_restores_seed_state(self):
        gw = Glowworm()
        seed_state, seed_n = list(gw.s), gw.n
        for bit in (1, 0, 1, 1, 0):
            gw.add_bit(bit)
        self.assertNotEqual(gw.s, seed_state)
        gw.reset()
        self.assertEqual(gw.s, seed_state)
        self.assertEqual(gw.n, seed_n)

    def test_del_bit_inverts_add_bit(self):
        gw = Glowworm()
        before = list(gw.s)
        for bit in (1, 0, 0, 1):
            gw.add_bit(bit)
        for bit in (1, 0, 0, 1)[::-1]:
            gw.del_bit(bit)
        self.assertEqual(gw.s, before)
        self.assertEqual(gw.n, 0)

    def test_instances_do_not_share_state(self):
        # The register used to live in module globals, so two blocks in one
        # flowgraph corrupted each other.
        a, b = Glowworm(), Glowworm()
        a.add_bit(1)
        self.assertNotEqual(a.s, b.s)


class TestRoundTrip(unittest.TestCase):

    def test_single_message(self):
        enc = Encoder(MSG_LEN, COD_LEN)
        dec = Decoder(MSG_LEN, COD_LEN)
        msg = b"GRCon26!"
        self.assertEqual(dec.decode(enc.encode(msg)), [msg])

    def test_consecutive_messages_reuse_one_codec(self):
        # This is the regression that mattered most: state carried over
        # between packets, so only the first message ever decoded.
        enc = Encoder(MSG_LEN, COD_LEN)
        dec = Decoder(MSG_LEN, COD_LEN)
        for msg in (b"AAAAAAAA", b"GRCon26!", b"\x00" * 8, b"\xff" * 8):
            self.assertEqual(dec.decode(enc.encode(msg)), [msg], msg)

    def test_encoder_is_deterministic(self):
        enc = Encoder(MSG_LEN, COD_LEN)
        msg = b"repeated"
        self.assertEqual(enc.encode(msg), enc.encode(msg))

    def test_concurrent_codes(self):
        # Two messages OR'd into one codeword must both come back out.
        enc = Encoder(MSG_LEN, COD_LEN)
        dec = Decoder(MSG_LEN, COD_LEN)
        a, b = b"message1", b"message2"
        merged = bytearray(x | y for x, y in zip(enc.encode(a), enc.encode(b)))
        self.assertCountEqual(dec.decode(merged), [a, b])

    def test_all_message_sizes_round_trip(self):
        for msg_len, cod_len in ((1, 256), (4, 1024), (16, 2**13)):
            enc = Encoder(msg_len, cod_len)
            dec = Decoder(msg_len, cod_len)
            msg = bytes(range(msg_len))
            self.assertIn(msg, dec.decode(enc.encode(msg)),
                          "%dB message / %dB codeword" % (msg_len, cod_len))


class TestJamResistance(unittest.TestCase):

    def test_survives_added_marks(self):
        enc = Encoder(MSG_LEN, COD_LEN)
        dec = Decoder(MSG_LEN, COD_LEN)
        msg = b"jamme.me"
        codeword = enc.encode(msg)
        for fraction in (0.1, 0.3, 0.5, 0.7):
            decoded = dec.decode(jam(codeword, fraction, seed=1))
            self.assertIn(msg, decoded, "jammed to %.0f%%" % (fraction * 100))

    def test_checksum_suppresses_false_decodes(self):
        msg = b"jamme.me"
        jammed_no_check = jam(Encoder(MSG_LEN, COD_LEN, 0).encode(msg), 0.8, 2)
        # Raised past the default so the flood is measurable rather than
        # truncated -- see test_uncheckedsummed_flood_can_hide_the_message.
        without = Decoder(MSG_LEN, COD_LEN, 0,
                          max_candidates=100000).decode(jammed_no_check)

        jammed_check = jam(Encoder(MSG_LEN, COD_LEN, 32).encode(msg), 0.8, 2)
        with_check = Decoder(MSG_LEN, COD_LEN, 32).decode(jammed_check)

        self.assertIn(msg, without)
        self.assertGreater(len(without), 100)
        self.assertEqual(with_check, [msg])

    def test_unchecksummed_flood_can_hide_the_message(self):
        # The search enumerates prefixes in order, so once a heavily jammed
        # codeword overflows max_candidates the real message may never be
        # reached. This is the strongest argument for keeping a checksum on.
        msg = b"jamme.me"
        jammed = jam(Encoder(MSG_LEN, COD_LEN, 0).encode(msg), 0.8, 2)
        dec = Decoder(MSG_LEN, COD_LEN, 0)
        decoded = dec.decode(jammed)
        self.assertTrue(dec.truncated)
        self.assertNotIn(msg, decoded)

    def test_saturated_codeword_is_bounded(self):
        # An all-marks codeword makes every branch look plausible. The decoder
        # must give up rather than run away with the flowgraph.
        dec = Decoder(MSG_LEN, COD_LEN, 0, max_candidates=16, max_steps=50000)
        dec.decode(b"\xff" * COD_LEN)
        self.assertTrue(dec.truncated)
        # Truncating must still leave the codec usable for the next packet.
        self.assertEqual(
            dec.decode(Encoder(MSG_LEN, COD_LEN, 0).encode(b"recovery")),
            [b"recovery"])


class TestChecksum(unittest.TestCase):

    def test_default_mode_is_zero_fill(self):
        # The published description appends zeros; anything else is a private
        # wire format. Keep the interoperable one as the default.
        self.assertEqual(DEFAULT_CHECKSUM_MODE, CHECKSUM_ZEROS)
        self.assertEqual(checksum_bits(b"abc", 8), [0] * 8)
        self.assertEqual(Encoder(MSG_LEN, COD_LEN).checksum_mode,
                         CHECKSUM_ZEROS)
        self.assertEqual(Decoder(MSG_LEN, COD_LEN).checksum_mode,
                         CHECKSUM_ZEROS)

    def test_zero_fill_prunes_as_well_as_a_hash(self):
        # Measured equal: what prunes is the mark location moving with the
        # prefix, not the check-bit values.
        msg = b"jamme.me"
        counts = []
        for mode in (CHECKSUM_ZEROS, CHECKSUM_SHA256):
            codeword = Encoder(MSG_LEN, COD_LEN, 32, mode).encode(msg)
            decoded = Decoder(MSG_LEN, COD_LEN, 32,
                              checksum_mode=mode).decode(jam(codeword, 0.8, 2))
            self.assertEqual(decoded, [msg], mode)
            counts.append(len(decoded))
        self.assertEqual(counts[0], counts[1])

    def test_modes_do_not_interoperate(self):
        msg = b"mismatch"
        codeword = Encoder(MSG_LEN, COD_LEN, 32, CHECKSUM_ZEROS).encode(msg)
        self.assertEqual(
            Decoder(MSG_LEN, COD_LEN, 32,
                    checksum_mode=CHECKSUM_SHA256).decode(codeword), [])

    def test_sha256_bits_are_deterministic(self):
        self.assertEqual(checksum_bits(b"abc", 16, CHECKSUM_SHA256),
                         checksum_bits(b"abc", 16, CHECKSUM_SHA256))
        self.assertNotEqual(checksum_bits(b"abc", 16, CHECKSUM_SHA256),
                            checksum_bits(b"abd", 16, CHECKSUM_SHA256))

    def test_zero_length_checksum(self):
        self.assertEqual(checksum_bits(b"abc", 0), [])

    def test_sha256_longer_than_digest_rejected(self):
        self.assertRaises(BbcError, checksum_bits, b"abc", 257,
                          CHECKSUM_SHA256)

    def test_unknown_mode_rejected(self):
        self.assertRaises(BbcError, checksum_bits, b"abc", 8, 'crc32')
        self.assertRaises(BbcError, Encoder, MSG_LEN, COD_LEN, 32, 'crc32')


class TestValidation(unittest.TestCase):

    def test_codeword_must_exceed_message(self):
        self.assertRaises(BbcError, Encoder, 128, 128)
        self.assertRaises(BbcError, Encoder, 128, 64)

    def test_wrong_message_length_rejected(self):
        enc = Encoder(MSG_LEN, COD_LEN)
        self.assertRaises(BbcError, enc.encode, b"short")

    def test_wrong_codeword_length_rejected(self):
        dec = Decoder(MSG_LEN, COD_LEN)
        self.assertRaises(BbcError, dec.decode, b"\x00" * 16)


if __name__ == '__main__':
    unittest.main()
