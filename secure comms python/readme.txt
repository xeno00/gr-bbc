Project Description:
    The purpose of these files is to encode and decode a message using the BBC algorithm as described by 
    Bahn, Baird, and Carlisle. The BBC algorithm is an unkeyed approach to jamming resistance. Without
    the use of keys, omnidirectional communication may be achieved with relatively low power and high
    speed. In BBC, codewords are binary strings with length 2^len(message+num_checksum_bits). Since the
    mark (represented as a '1' in codeword) density is low, the transmit power requirement is low. 

Manifest:
    BBCCodecNum.py - The BBC codec with messages and codewords represented as numbers (integers/binary). For use with glowworm.c.
    BBCCodecArray.py - The BBC codec with messages and codewords represented as arrays. For use with glowworm.py. Sacrifices speed for clarity.
    glowworm.c - The original implementation in c of the glowworm hash provided by Dr. Bahn.
    glowworm.py - The python implementation of the glowworm hash. Sacrifices speed for clarity.