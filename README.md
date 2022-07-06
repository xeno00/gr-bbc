# **BBC Anti-Jam Communications**: sturdy-train

## Overview
##### Project Description
The purpose of this repo is to implement a codec using the **BBC codec** as described by Bahn, Baird, and Carlisle. 
This codec is a jam-resistant, unkeyed approach to wireless communicatoins. Without the use of keys,
omnidirectional communication may be achieved with relatively low power and high speed. This implementation is designed for
messages formatted as binary arrays with length 2\*\*10 and codewords with length 2\*\*20. Since the mark (represented as a
'1' in codeword) density is low, the transmit power requirement is low. Though BBC does not protect confidentiality or 
authenticity, it preserves integrety, and when used to share public keys, it may reinforce all aspects of secure communication.
Since the codeword is sparse relative to the message, a low SNR will contribute to message "hallucinations," rather than 
corruption of the original key/message. For key-sharing, the end user may then distinguish the original public key based on
prior mission assumptions. 
    
##### Document Manifest

1. `bbc-C`: Felix's `c`  implemetation of BBC
    - TODO

3. `gnuRadio`: Includes GNURadio implementation of the codec for testing, built using the object oriented python code
    - `BBCCodecGRC.grc`: the working block diagram for the BBC implementation

5. `secure comms python`: James' `python` implementation of the codec. Most up-to-date version
    - `BBCCodecArray.py`: The BBC codec with messages and codewords represented as arrays. For use with glowworm.py. Sacrifices speed for clarity.
    - `BBCCodecNum.py`: The BBC codec with messages and codewords represented as numbers (integers/binary). For use with glowworm.c.
    - `BBCCodecOO.py`: 
    - `glowworm.c`: The original implementation in c of the glowworm hash provided by Dr. Bahn.
    - `glowworm.py`: The python implementation of the glowworm hash. Sacrifices speed for clarity.



## Python



## C



## GNURadio
**Error in Work when output_items[0] has no length, that is there is nothing to output**
> gr::log :ERROR: thread_body_wrapper - ERROR thread[thread-per-block[6]: <block BBC Decoder(2)>]: TypeError: int() argument must be a string, a bytes-like object or a number, not 'NoneType'

