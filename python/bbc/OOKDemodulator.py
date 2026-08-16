#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright 2022 James Morrison.
#
# SPDX-License-Identifier: GPL-3.0-or-later
#
"""On-off keying demodulator for BBC codewords.

Complex baseband in, packed bytes out.  The chain band-pass filters around the
carrier, takes magnitude squared, integrates over exactly one symbol, slices,
and packs the bits MSB first to mirror
:class:`~bbc.OOKModulator.OOKModulator`.

Symbol timing is open loop.  There is no timing recovery, so the block instead
discards exactly the band-pass filter's group delay before decimating.  That
does two things: the integrator window lands on symbol boundaries instead of
straddling two symbols (which would smear every mark into its neighbours), and
the output byte stream lines up one-for-one with the modulator's input.  That
second property is what lets a flowgraph slice the demodulated stream back into
codeword vectors without any framing.  The previous revision did neither -- it
centred the band-pass on a hard-coded 50 kHz and ignored its delay entirely.

The cost is the filter warm-up: the last ``ceil(group_delay / sps)`` symbols of
a finite stream are not produced.

A note on the slicer threshold: BBC assumes a Z channel, where marks are added
but never removed.  A spurious 1 costs the decoder a little search effort, but
a *dropped* 1 breaks the message outright.  So ``threshold`` deliberately sits
below the halfway point -- bias toward declaring a mark.  It is an absolute
energy, matched to the unit-amplitude carrier the modulator produces; raise it
if the channel has a noise floor, lower it for a weak signal.
"""

from gnuradio import blocks
from gnuradio import filter as gr_filter
from gnuradio import gr
from gnuradio.fft import window
from gnuradio.filter import firdes

#: A quarter of the nominal energy of a mark, for a unit-amplitude carrier.
DEFAULT_THRESHOLD = 0.25


class OOKDemodulator(gr.hier_block2):

    def __init__(self, carrier_freq=20e3, samp_rate=128e3, symbol_rate=500,
                 bandwidth=None, threshold=DEFAULT_THRESHOLD):
        gr.hier_block2.__init__(
            self, "OOK Demodulator",
            gr.io_signature(1, 1, gr.sizeof_gr_complex * 1),
            gr.io_signature(1, 1, gr.sizeof_char * 1),
        )

        self.carrier_freq = carrier_freq
        self.samp_rate = samp_rate
        self.symbol_rate = symbol_rate
        # Wide enough to pass the keying sidebands; the OOK envelope occupies
        # roughly +/- symbol_rate around the carrier.
        self.bandwidth = (4.0 * symbol_rate) if bandwidth is None else bandwidth
        self.threshold = threshold

        # Validate before touching firdes, which reports a bad sample rate as
        # an opaque IndexError.
        sps = self._samples_per_symbol()
        taps = self._taps()

        self.band_pass_filter_0 = gr_filter.fir_filter_ccc(1, taps)
        self.blocks_complex_to_mag_squared_0 = blocks.complex_to_mag_squared(1)
        # Integrate over a symbol so the decimator below sees accumulated
        # symbol energy rather than one, possibly badly timed, instant.
        self.symbol_integrator = gr_filter.fir_filter_fff(
            1, self._integrator_taps())
        self.blocks_skiphead_0 = blocks.skiphead(
            gr.sizeof_float * 1, self._alignment_skip(len(taps)))
        self.blocks_threshold_ff_0 = blocks.threshold_ff(
            threshold, threshold, 0)
        self.blocks_keep_one_in_n_0 = blocks.keep_one_in_n(
            gr.sizeof_float * 1, sps)
        self.blocks_float_to_char_0 = blocks.float_to_char(1, 1)
        self.blocks_unpacked_to_packed_xx_0 = blocks.unpacked_to_packed_bb(
            1, gr.GR_MSB_FIRST)

        self.connect((self, 0), (self.band_pass_filter_0, 0))
        self.connect((self.band_pass_filter_0, 0),
                     (self.blocks_complex_to_mag_squared_0, 0))
        self.connect((self.blocks_complex_to_mag_squared_0, 0),
                     (self.symbol_integrator, 0))
        self.connect((self.symbol_integrator, 0),
                     (self.blocks_skiphead_0, 0))
        self.connect((self.blocks_skiphead_0, 0),
                     (self.blocks_threshold_ff_0, 0))
        self.connect((self.blocks_threshold_ff_0, 0),
                     (self.blocks_keep_one_in_n_0, 0))
        self.connect((self.blocks_keep_one_in_n_0, 0),
                     (self.blocks_float_to_char_0, 0))
        self.connect((self.blocks_float_to_char_0, 0),
                     (self.blocks_unpacked_to_packed_xx_0, 0))
        self.connect((self.blocks_unpacked_to_packed_xx_0, 0), (self, 0))

    @staticmethod
    def _alignment_skip(ntaps):
        """Samples to discard so the sampler lands on symbol boundaries.

        ``fir_filter`` output ``i`` corresponds to input ``i - D``, where
        ``D = (ntaps - 1) // 2``.  The integrator then averages original
        samples ``[i - D - sps + 1, i - D]`` and ``keep_one_in_n`` keeps the
        *last* entry of each group of ``sps``.  Dropping exactly ``D`` samples
        makes kept sample ``j`` cover symbol ``j`` -- so the phase is right and
        the byte stream is aligned with the modulator's input.

        Dropping ``D mod sps`` instead would fix the phase but leave a constant
        whole-symbol offset, which is enough to misalign codeword vectors.
        """
        return (ntaps - 1) // 2

    def _samples_per_symbol(self):
        sps = int(self.samp_rate / self.symbol_rate)
        if sps < 1:
            raise ValueError(
                "samp_rate (%g) must be at least symbol_rate (%g)"
                % (self.samp_rate, self.symbol_rate))
        return sps

    def _integrator_taps(self):
        sps = self._samples_per_symbol()
        return [1.0 / sps] * sps

    def _taps(self):
        # Centred on the carrier rather than on a hard-coded 50 kHz, which was
        # simply wrong for any carrier the modulator was actually using.
        return firdes.complex_band_pass(
            1, self.samp_rate,
            self.carrier_freq - self.bandwidth / 2.0,
            self.carrier_freq + self.bandwidth / 2.0,
            self.bandwidth / 4.0, window.WIN_HAMMING, 6.76)

    def get_carrier_freq(self):
        return self.carrier_freq

    def _retune(self):
        # The alignment skiphead is fixed once the flowgraph starts, so these
        # setters only stay correct while the filter length does not change.
        # Changing samp_rate or symbol_rate enough to resize the band-pass
        # needs the block rebuilt, not retuned.
        self.band_pass_filter_0.set_taps(self._taps())
        self.symbol_integrator.set_taps(self._integrator_taps())
        self.blocks_keep_one_in_n_0.set_n(self._samples_per_symbol())

    def set_carrier_freq(self, carrier_freq):
        self.carrier_freq = carrier_freq
        self._retune()

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self._retune()

    def get_symbol_rate(self):
        return self.symbol_rate

    def set_symbol_rate(self, symbol_rate):
        self.symbol_rate = symbol_rate
        self._retune()

    def get_threshold(self):
        return self.threshold

    def set_threshold(self, threshold):
        self.threshold = threshold
        self.blocks_threshold_ff_0.set_hi(threshold)
        self.blocks_threshold_ff_0.set_lo(threshold)
