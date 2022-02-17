
#ifndef BBC_C_MAIN_H
#define BBC_C_MAIN_H


// ********* Copied from "The Glowworm hash: Increased Speed and Security for BBC Unkeyed Jam Resistance" *********


// Glowworm - A hash for use with BBC codes
// April 2012, Version 1.0
// Leemon Baird, Leemon@Leemon.com
//
// Call glowwormInit once, which returns the hash of the
// empty string, which should equal CHECKVALUE. Then
// call AddBit to add a new bit to the end, and return the
// hash of the resulting string. DelBit deletes the last
// bit, and must be passed the last bit of the most string
// hashed. The macros should be passed these:
//  uint64 s[32]; //buffer
//  static uint64 n; //current string length
//  uint64 t, i, h; //temporary
//  const uint64 CHECKVALUE = 0xCCA4220FC78D45E0;

typedef unsigned long long uint64; //64-bit unsigned int


#define glowwormAddBit(b, s, n, t) ( \
    t = s[n % 32] ^ ((b) ? 0xffffffff : 0), \
    t = (t|(t>>1)) ^ (t<<1), \
    t ^= (t>>4) ^ (t>>8) ^ (t>>16) ^ (t>>32),\
    n++, \
    s[n % 32] ^= t \
)


#define glowwormDelBit(b, s, n, t) ( \
    n--, \
    glowwormAddBit(b,s,n,t), \
    n--, \
    s[n % 32] \
)
#define glowwormInit(s, n, t, i, h) { \
    h = 1; \
    n = 0; \
    for (i=0; i<32; i++) \
        s[i]=0; \
    for (i=0; i<4096; i++) \
        h=glowwormAddBit(h & 1L,s,n,t); \
    n = 0; \
}


// END: **** Copied from "The Glowworm hash: Increased Speed and Security for BBC Unkeyed Jam Resistance" *********


int foundInArray( uint64 array[], int arrayLength, uint64 value);

void printArray( uint64 array[], int arrayLength );

void DFSDecoder2(int newMarks[], uint64 decodedMsg[], int lenM, int lenK, int totalLength, int badMarksLen, uint64 mask, uint64 s[], uint64 n, uint64 t, uint64 i, uint64 h);

void DFSDecoder(int newMarks[], uint64 decodedMsg[], int lenM, int lenK, int totalLength, int badMarksLen, uint64 mask, uint64 s[], uint64 n, uint64 t, uint64 i, uint64 h);

void basicDecoder(uint64 marks[], uint64 decodedMsg[], int lenM, int lenK, int totalLength, uint64 mask, uint64 s[], uint64 n, uint64 t, uint64 i, uint64 h);


#endif //BBC_C_MAIN_H
