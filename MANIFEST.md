title: gr-bbc  
brief: The event stream scheduler  
tags:  
  - secure communications  
  - codec  
  - bbc  
author:  
  - James Morrison <jamescmorrison00@gmail.com>
copyright_owner:  
  - James Morrison <jamescmorrison00@gmail.com>
dependencies:  
  - gnuradio (>= 3.10.0)
repo: https://github.com/xeno00/gr-bbc  
stable_release: HEAD  
---


This project implements Baird, Bahn, and Collins' **BBC codec** in GNURaduio
See the [GRCon22 events page](https://events.gnuradio.org/event/18/contributions/278/) for background information and use-case explanation.
If you want, watch our GRCon22 presentation, [here](https://youtu.be/I3QmZwdsavE&t=7h38m45s).

The BBC algorithm assumes an asymmetric Z channel, where a mark (bit with value 1) can be added, but cannot be removed. Naturally, OOK is a straightforward implementation for such a channel. 

These blocks conduct BBC encoding/decoding before physical-layer transmission/reception. 

* bbc_encoder encodes a byte message by hashing substrings and placing marks in a psuedo-random location within the codeword
* bbc_decoder reverses the process by using an iterative substring reconstruction process


Some examples of use-cases for BBC are included,
    - bbc_gr_base.grc:     demonstrates encoding/decoding to reproduce an encoded message.
                           The most basic use case.
    - bbc_gr_ook.grc:      Combines bbc_gr_base.grc with OOK modulation for TX/RX testing
    - bbc_gr_ook_fhss.grc: Simulates a low-bandwidth BBC-encoded OOK signal that triggers a 
                           frequency hop for another signal
