/*===================================================================
 |	Assignment: BBC Encoder/Decoder
 |	Author: Felix Zheng
 |
 +-------------------------------------------------------------------
 |	Description: tbd
 |
 |	Known Bugs: tbd
 |
 |  Supporting Files: tbd
 |
 *===================================================================/*/


#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "main.h"



int main (int argc, char *argv[]) {

    int lenM = 30;
    int lenK = 2;
    int codewordBits = 7;

    uint64 mask = (1 << codewordBits) - 1;


    uint64 m[lenM];
    // Init M with dummy data (all 1s)
    for ( int i = 0; i < lenM; i++ ){
        m[i] = 1;
    }

    uint64 k[lenK];
    // Init k with zeroes as checksum
    for ( int i = 0; i < lenK; i++ ){
        k[i] = 0;
    }

    uint64 raw[lenM+lenK];
    // Init encoded with zeroes
    memcpy(&raw, &m, sizeof(m));
    memcpy(&raw[lenM], &k, sizeof(k));

    // Init Glowworm
    uint64 s[32]; //buffer
    static uint64 n; //current string length
    uint64 t, i, h; //temporary
    const uint64 CHECKVALUE = 0xCCA4220FC78D45E0;

    glowwormInit(s, n, t, i, h);

    if( h == CHECKVALUE ){

        printf("Init Works: 0x%llx\n", h);
    }

    uint64 mark;

    for (int j = 0; j < lenM + lenK; j++ ){

        glowwormAddBit( (uint64)raw[j] , s, n, t);
        mark = s[n%32] & mask;
        printf("%d: %llx with mark %d\n", n, s[n%32], mark);

    }

    for (int j = lenM + lenK -1 ; j >= 0; j-- ){

        glowwormDelBit( (uint64)raw[j] , s, n, t);
        printf("%d: %llx\n", n, s[n%32]);

    }


    return 0;
}


