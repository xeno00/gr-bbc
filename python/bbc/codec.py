"""Pure-Python implementation of the Baird, Bahn, and Collins codec.

This module intentionally has no GNU Radio dependency.  Keeping the codec
separate from the scheduler-facing blocks makes it straightforward to test and
reuse while preserving the bit ordering of the original implementation.
"""

# Copyright 2022-2026 James Morrison
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

from collections.abc import Iterable

_MASK_64 = 0xFFFFFFFFFFFFFFFF
_REGISTER_WORDS = 32
_WARMUP_STEPS = 4096


class DecodeLimitError(RuntimeError):
    """Raised when a codeword exceeds the configured decoder search budget."""


class _ShiftRegister:
    """Reversible shift register used by the BBC tree-code construction."""

    def __init__(self) -> None:
        self.words = [0] * _REGISTER_WORDS
        self.position = 0
        value = 1
        for _ in range(_WARMUP_STEPS):
            value = self.add(value & 1)
        self.position = 0

    def add(self, bit: int) -> int:
        """Append one bit and return the resulting pseudo-random value."""
        value = (
            self.words[self.position % _REGISTER_WORDS]
            ^ (0xFFFFFFFF if bit else 0)
        ) & _MASK_64
        value = ((value | (value >> 1)) ^ ((value << 1) & _MASK_64)) & _MASK_64
        value = (
            value
            ^ (value >> 4)
            ^ (value >> 8)
            ^ (value >> 16)
            ^ (value >> 32)
        ) & _MASK_64
        self.position += 1
        index = self.position % _REGISTER_WORDS
        self.words[index] ^= value
        return self.words[index]

    def remove(self, bit: int) -> int:
        """Undo the most recent :meth:`add` for ``bit``."""
        self.position -= 1
        self.add(bit)
        self.position -= 1
        return self.words[self.position % _REGISTER_WORDS]


def _require_positive_length(name: str, value: int) -> int:
    value = int(value)
    if value <= 0:
        raise ValueError(f"{name} must be a positive integer")
    return value


def _as_bytes(data: bytes | bytearray | memoryview | Iterable[int]) -> bytes:
    if isinstance(data, bytes):
        return data
    if isinstance(data, (bytearray, memoryview)):
        return bytes(data)
    if hasattr(data, "tobytes"):
        return data.tobytes()
    return bytes(data)


def _get_bit(buffer: bytes | bytearray, bit_index: int) -> int:
    return (buffer[bit_index // 8] >> (bit_index % 8)) & 1


def _set_bit(buffer: bytearray, bit_index: int, value: int) -> None:
    mask = 1 << (bit_index % 8)
    byte_index = bit_index // 8
    if value:
        buffer[byte_index] |= mask
    else:
        buffer[byte_index] &= 0xFF ^ mask


class Encoder:
    """Encode fixed-size byte messages as BBC mark codewords.

    Args:
        message_length: Input message length in bytes.
        codeword_length: Output codeword length in bytes.
    """

    def __init__(self, message_length: int, codeword_length: int) -> None:
        self.message_length = _require_positive_length(
            "message_length", message_length
        )
        self.codeword_length = _require_positive_length(
            "codeword_length", codeword_length
        )
        self.message_bits = self.message_length * 8
        self.codeword_bits = self.codeword_length * 8

    def encode(
        self, message: bytes | bytearray | memoryview | Iterable[int]
    ) -> bytes:
        """Return the codeword for one exactly sized message."""
        message_bytes = _as_bytes(message)
        if len(message_bytes) != self.message_length:
            raise ValueError(
                f"message must contain exactly {self.message_length} bytes; "
                f"received {len(message_bytes)}"
            )

        register = _ShiftRegister()
        codeword = bytearray(self.codeword_length)
        for bit_index in range(self.message_bits):
            mark = register.add(_get_bit(message_bytes, bit_index))
            _set_bit(codeword, mark % self.codeword_bits, 1)
        return bytes(codeword)


class Decoder:
    """Recover candidate messages from fixed-size BBC codewords.

    BBC decoding is a tree search. ``max_candidates`` and
    ``max_search_nodes`` prevent a malformed or extremely dense codeword from
    monopolizing a GNU Radio worker thread.
    """

    def __init__(
        self,
        message_length: int,
        codeword_length: int,
        *,
        max_candidates: int = 64,
        max_search_nodes: int = 1_000_000,
    ) -> None:
        self.message_length = _require_positive_length(
            "message_length", message_length
        )
        self.codeword_length = _require_positive_length(
            "codeword_length", codeword_length
        )
        self.max_candidates = _require_positive_length(
            "max_candidates", max_candidates
        )
        self.max_search_nodes = _require_positive_length(
            "max_search_nodes", max_search_nodes
        )
        self.message_bits = self.message_length * 8
        self.codeword_bits = self.codeword_length * 8

    def decode(
        self, codeword: bytes | bytearray | memoryview | Iterable[int]
    ) -> list[bytes]:
        """Return every candidate discovered within the configured limits."""
        packet = _as_bytes(codeword)
        if len(packet) != self.codeword_length:
            raise ValueError(
                f"codeword must contain exactly {self.codeword_length} bytes; "
                f"received {len(packet)}"
            )

        register = _ShiftRegister()
        message = bytearray(self.message_length)
        candidates: list[bytes] = []
        bit_index = 0
        visited = 0

        while True:
            visited += 1
            if visited > self.max_search_nodes:
                raise DecodeLimitError(
                    "BBC decoder exceeded max_search_nodes; the codeword may "
                    "contain too many false marks"
                )

            proposed_bit = _get_bit(message, bit_index)
            mark = register.add(proposed_bit) % self.codeword_bits
            mark_present = _get_bit(packet, mark) == 1

            if mark_present:
                if bit_index == self.message_bits - 1:
                    candidates.append(bytes(message))
                    if len(candidates) >= self.max_candidates:
                        return candidates
                else:
                    bit_index += 1
                    _set_bit(message, bit_index, 0)
                    continue

            while bit_index >= 0 and _get_bit(message, bit_index) == 1:
                register.remove(1)
                _set_bit(message, bit_index, 0)
                bit_index -= 1

            if bit_index < 0:
                return candidates

            register.remove(0)
            _set_bit(message, bit_index, 1)


def encode(message: bytes, codeword_length: int) -> bytes:
    """Convenience function for encoding one byte string."""
    return Encoder(len(message), codeword_length).encode(message)


def decode(
    codeword: bytes,
    message_length: int,
    *,
    max_candidates: int = 64,
    max_search_nodes: int = 1_000_000,
) -> list[bytes]:
    """Convenience function for decoding one byte string."""
    return Decoder(
        message_length,
        len(codeword),
        max_candidates=max_candidates,
        max_search_nodes=max_search_nodes,
    ).decode(codeword)
