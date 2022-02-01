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

    int lenM = 30; // Number of message bits.
    int lenK = 2; // Number of check bits.
    int totalLength = lenM+lenK;

    // This creates 2^codewordBits combo. It should be at least 1 higher than the minimum required.
    // Consider the formula: [ log(lenM+lenK) / log (2) ]+ 1
    int codewordBits = 30;

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


    // Init Glowworm hash
    uint64 s[32];       //buffer to store the hash. This is on a rotating basis, mod 32.
    static uint64 n;    //current string length counter
    uint64 t, i, h;     //temporary variables
    const uint64 CHECKVALUE = 0xCCA4220FC78D45E0;   // This should be the value of 'h' when glowworm is initialized.

    //Initialize glowworm
    glowwormInit(s, n, t, i, h);


    // Check to see if glowworm was initialized correctly. The value in position 0 should be equal to 'h'
    if( h == CHECKVALUE ){
        printf("Init Works: 0x%llx\n", h);
    }


    // Create a variable to store the current "mark"
    uint64 mark;

    // Create a 'marks' array to store all marks.
    uint64 marks[totalLength];

    // The mark is calculated using the last 'codewordBits' of the data in the buffer;
    //      the position of the data within the buffer 's' depends on n%32.
    for (int j = 0; j < totalLength; j++ ){
        glowwormAddBit( (uint64)raw[j] , s, n, t);
        mark = s[n%32] & mask;
        printf("%d: %llx with mark %d\n", n, s[n%32], mark);

        // store the mark to the 'marks' array.
        marks[j] = mark;
    }


    // Test the deletion of bits using glowWorm.
    //  We should end up with the same hashes in reverse order given the same input string.
    for (int j = totalLength - 1 ; j >= 0; j-- ){
        glowwormDelBit( (uint64)raw[j] , s, n, t);
        printf("%d: %llx\n", n, s[n%32]);
    }

    // To implement a basic decoder, we must implement a depth-first search.
    // The decoder receives a number of "marks" that we will need to process.
    // The decoder will test for the existence of each mark according to the glowworm
    // hash function and decide if a proper message exists.


    // ********************************
    // *** Proof of concept decoder ***
    // ********************************
    // This test will be inefficient -- streamlining will come in the future.
    // Here, we will search through the array linearly.
    // Assume: glowworm is fully initialized with h, s, n, t, and i
    // Assume: Marks are stored within a requisite array, 'marks'
    // Assume: lenK and lenM are initialized properly.
    // Assume: a full and valid message is received, no more, no less
    // Assume: there are no 'extra' bits that will result in backtracking more than one level

    // Result: The decoder works with a 30-bit message of (0101010...) and two check bits (00) with a mask of 10 bits.
    // Testing showed that with 30-bits of 1s (1111....) and two (00), the decoder encountered a false positive,
    //  marking a 0 when it should not have. This will need to be fixed in future iterations.


    // Create a variable to store the current "mark"
    uint64 decodeMark0;
    uint64 decodeMark1;

    uint64 decodedMsg[ totalLength ];

    // search for the message first.
    for( int msgBit = 0; msgBit < lenM; msgBit++ ){

        // Test the existence of an added 0
        glowwormAddBit( (uint64) 0 , s, n, t);
        decodeMark0 = s[n%32] & mask;

        if( !foundInArray( marks, totalLength, decodeMark0 ) )
        {
            // didn't find 0... let's backtrack.
            glowwormDelBit( 0 , s, n, t);

            // it must be a 1 (assuming no additional backtracking
            glowwormAddBit( (uint64) 1 , s, n, t);
            decodedMsg[msgBit] = (uint64) 1;
            decodeMark1 = s[n%32] & mask;

            //debug
            printf("Found a 1 at position %d with mark %d\n", msgBit, decodeMark1);
        }
        else
        {
            // found a 0... let's set the bit and move on.
            decodedMsg[msgBit] = (uint64) 0;

            //debug
            printf("Found a 0 at position %d with mark %d\n", msgBit, decodeMark0);
        }
    }

    // Then, search for the check bits (assume all 0s)
    for ( int checkBit = lenM; checkBit < totalLength ; checkBit++ ){

        // Test the existence of an added 0
        glowwormAddBit( (uint64) 0 , s, n, t);
        decodeMark0 = s[n%32] & mask;

        if( !foundInArray( marks, totalLength, decodeMark0 ) ) {
            checkBit = totalLength; //break the loop
        }
        else {
            decodedMsg[checkBit] = (uint64) 0;
            //debug
            printf("Found check bit 0 at position %d with mark %d\n", checkBit, decodeMark0);
        }
    }


    // print the decoded message
    for( int j = 0; j < lenM + lenK; j++ ){
        printf("%d", decodedMsg[j]);
    }
    printf("\n");

    return 0;
}

int foundInArray( uint64* array, int arrayLength, uint64 value){

    int found = 0;
    int index = 0;
    while( !found && index < arrayLength ){
        found = array[index] == value;
        index++;
    }

    return found;
}


