# Copyright 2022-2026 James Morrison
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest

from bbc.codec import DecodeLimitError, Decoder, Encoder, decode, encode


class EncoderTests(unittest.TestCase):
    def test_preserves_reference_vector(self):
        expected = bytes.fromhex(
            "0200000000000000000200000000000000000000200000000400000000000000"
            "0000000000000200002000000000000000000000000100000080000000000000"
        )
        self.assertEqual(Encoder(1, 64).encode(b"A"), expected)

    def test_repeated_calls_do_not_share_state(self):
        encoder = Encoder(1, 64)
        self.assertEqual(encoder.encode(b"A"), encoder.encode(b"A"))

    def test_instances_do_not_share_state(self):
        expected = Encoder(1, 64).encode(b"A")
        Encoder(1, 64).encode(b"Z")
        self.assertEqual(Encoder(1, 64).encode(b"A"), expected)

    def test_rejects_incorrect_message_size(self):
        with self.assertRaisesRegex(ValueError, "exactly 2 bytes"):
            Encoder(2, 64).encode(b"A")

    def test_rejects_nonpositive_lengths(self):
        for message_length, codeword_length in ((0, 1), (1, 0), (-1, 1)):
            with self.subTest(
                message_length=message_length, codeword_length=codeword_length
            ):
                with self.assertRaises(ValueError):
                    Encoder(message_length, codeword_length)


class DecoderTests(unittest.TestCase):
    def test_round_trip(self):
        message = b"BBC"
        codeword = Encoder(len(message), 128).encode(message)
        self.assertIn(message, Decoder(len(message), 128).decode(codeword))

    def test_repeated_calls_reset_search_state(self):
        message = b"A"
        codeword = Encoder(1, 64).encode(message)
        decoder = Decoder(1, 64)
        self.assertIn(message, decoder.decode(codeword))
        self.assertIn(message, decoder.decode(codeword))

    def test_empty_codeword_has_no_candidates(self):
        self.assertEqual(Decoder(1, 64).decode(bytes(64)), [])

    def test_rejects_incorrect_codeword_size(self):
        with self.assertRaisesRegex(ValueError, "exactly 64 bytes"):
            Decoder(1, 64).decode(bytes(63))

    def test_candidate_limit_is_enforced(self):
        candidates = Decoder(
            1, 1, max_candidates=2, max_search_nodes=1_000
        ).decode(b"\xff")
        self.assertEqual(len(candidates), 2)

    def test_search_limit_is_enforced(self):
        with self.assertRaises(DecodeLimitError):
            Decoder(2, 2, max_search_nodes=1).decode(b"\xff\xff")

    def test_convenience_functions(self):
        message = b"A"
        codeword = encode(message, 64)
        self.assertIn(message, decode(codeword, 1))


if __name__ == "__main__":
    unittest.main()
