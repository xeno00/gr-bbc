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
//      uint64 s[32]; //buffer
//      static uint64 n; //current string length
//      uint64 t, i, h; //temporary
//      const uint64 CHECKVALUE = 0xCCA4220FC78D45E0;

typedef unsigned long long uint64; //64-bit unsigned int

#define glowwormAddBit(b,s,n,t) (            \
    t  = s[n % 32] ˆ ((b) ? 0xffffffff : 0), \
    t  = (t|(t>>1)) ˆ (t<<1),                \
    t ˆ= (t>>4) ˆ (t>>8) ˆ (t>>16) ˆ (t>>32),\
    n++,                                     \
    s[n % 32] ˆ= t                           \
)

#define glowwormDelBit(b,s,n,t) (            \
    n--,                                     \
    glowwormAddBit(b,s,n,t),                 \
    n--,                                     \
    s[n % 32]                                \
)

#define glowwormInit(s,n,t,i,h) {            \
    h = 1;                                   \
    n = 0;                                   \
    for (i=0; i<32; i++)                     \
        s[i]=0;                              \
    for (i=0; i<4096; i++)                   \
        h=glowwormAddBit(h & 1L,s,n,t);      \
    n = 0;                                   \
}
