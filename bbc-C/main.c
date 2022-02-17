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



#include "main.h"
#include <time.h>

int main (int argc, char *argv[]) {

    int lenM = 1016; // Number of message bits.
    int lenK = 8; // Number of check bits.
    float targetMarksDensity = 0.499;
    int totalLength = lenM+lenK;

    // This creates 2^codewordBits combo. It should be at least 1 higher than the minimum required.
    // In this case, the max for codewordBits is 63 due to using the uint64 type.
    int codewordBits = 18;
    int badMarksLen = 0; // up to 30... see the section on adding erroneous bits
    uint64 mask = (1 << codewordBits) - 1; // This creates a mask with codewordBits number of 1s

    // Init message M
    uint64 m[lenM];

    //*** Testing only *** Init M with dummy data (alternating 0s and 1s )
    // This should represent the actual message M when not testing.
    for ( int i = 0; i < lenM; i++ ){
        m[i] = i%2;
    }


    // Init message K
    uint64 k[lenK];

    //*** Testing only *** Init K as two zeroes.
    // This should represent the actual check bits K when not testing.
    for ( int i = 0; i < lenK; i++ ){
        k[i] = 0;
    }

    // Init the "raw" array. This contains M and K together as one.
    uint64 raw[lenM+lenK];
    memcpy(&raw, &m, sizeof(m));
    memcpy(&raw[lenM], &k, sizeof(k));

    //Initialize glowworm
    glowwormInit(gwS, gwN, gwT, gwI, gwH);


    // Check to see if glowworm was initialized correctly. The value in position 0 should be equal to 'h'
    if( gwH == CHECKVALUE ){
        //printf("Init Works: 0x%llx\n", gwH);
    }


    // Create a variable to store the current "mark"
    uint64 mark;

    // Create a 'marks' array to store all marks.
    uint64 marks[ totalLength + badMarksLen ];

    int newMarks[ mask + 1 ];
    memset(newMarks, 0, sizeof newMarks);


    // IDEA: Create an improved 'marks' array to store all marks, but as a flag for presence.
    // We use each position to represent a mark. The issue is, it's pretty hard to have an array that's 2^30 long and
    //  index-able all the way through. Table this for now.


    // The mark is calculated using the last 'codewordBits' of the data in the buffer;
    //      the position of the data within the buffer 's' depends on n%32.
    for (int j = 0; j < totalLength; j++ ){
        glowwormAddBit( (uint64)raw[j] , gwS, gwN, gwT);
        mark = gwS[gwN%32] & mask;
        //printf("%d: %llx with mark %d\n", gwN, gwS[gwN%32], mark);

        // store the mark to the 'marks' array.
        marks[j] = mark;
        newMarks[mark] = 1;
    }


    /*
    //Create erroneous marks. The current pattern is 0101..., so let's just create a few marks at 1010...
    uint64 badMarks[30] = {1,0,1,0, \
                            1,0,1,0, \
                           1,0,1,0, \
                           1,0,1,0, \
                           1,0,1,0, \
                           1,0,1,0, \
                           1,0,1,0, \
                            1, 0};
    for (int j = 0; j < badMarksLen; j++ ){
        glowwormAddBit( (uint64)badMarks[j] , gwS, gwN, gwT);
        mark = gwS[gwN%32] & mask;
        printf("%d: %llx with mark %d\n", gwN, gwS[gwN%32], mark);

        // store the mark to the 'marks' array.
        marks[totalLength+j] = mark;
        newMarks[mark] = 1;
    }

*/
    addBadMarks(newMarks, mask+1, targetMarksDensity);

    // We know deletion works, so instead of testing the deletion, we re-init glowWorm.
    glowwormInit(gwS, gwN, gwT, gwI, gwH);
/*
    // Test the deletion of bits using glowWorm.
    //  We should end up with the same hashes in reverse order given the same input string.
    for (int j = totalLength - 1 ; j >= 0; j-- ){
        glowwormDelBit( (uint64)raw[j] , s, n, t);
        printf("%d: %llx\n", n, s[n%32]);
    }
*/



    uint64 decodedMsg[totalLength];
    //basicDecoder(marks, decodedMsg, lenM, lenK, totalLength, mask, s, n, t, i ,h);



    clock_t start, end;
    double cpu_time_used;

    start = clock();
    int steps = DFSDecoder2(newMarks, decodedMsg, lenM, lenK, totalLength, badMarksLen, mask);
    end = clock();
    cpu_time_used = ((double) (end - start)) / CLOCKS_PER_SEC;

    printf("Time used: %f\n", cpu_time_used);

    printf( "total steps: %d\n", steps);

    printf("Packet Density: %f\n", packetDensity( newMarks, mask + 1));

    // print the decoded message
    //printf("\n\nDecoded message:\n");
    //printArray(decodedMsg, totalLength);

    return 0;
}

float packetDensity(int * newMarks, int lenMarks){

    float total = 0;

    for( int i = 0; i < lenMarks; i++ ){

        total += newMarks[i];
    }
    return total/lenMarks;
}

float addBadMarks(int * newMarks, int lenMarks, float targetMarkDensity){


    for( int i = 0; i < lenMarks; i++ ){
        if( ((float) rand()/ (float) RAND_MAX) < targetMarkDensity )
            newMarks[i] = 1;
    }

}