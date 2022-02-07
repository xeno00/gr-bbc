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
    // In this case, the max for codewordBits is 63 due to using the uint64 type.
    int codewordBits = 6;
    int badMarksLen = 28; // up to 30... see the section on adding erroneous bits
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
    uint64 marks[ totalLength + badMarksLen ];

    int newMarks[ mask + 1 ];
    memset(newMarks, 0, sizeof newMarks);


    // IDEA: Create an improved 'marks' array to store all marks, but as a flag for presence.
    // We use each position to represent a mark. The issue is, it's pretty hard to have an array that's 2^30 long and
    //  index-able all the way through. Table this for now.


    // The mark is calculated using the last 'codewordBits' of the data in the buffer;
    //      the position of the data within the buffer 's' depends on n%32.
    for (int j = 0; j < totalLength; j++ ){
        glowwormAddBit( (uint64)raw[j] , s, n, t);
        mark = s[n%32] & mask;
        printf("%d: %llx with mark %d\n", n, s[n%32], mark);

        // store the mark to the 'marks' array.
        marks[j] = mark;
        newMarks[mark] = 1;
    }

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
        glowwormAddBit( (uint64)badMarks[j] , s, n, t);
        mark = s[n%32] & mask;
        printf("%d: %llx with mark %d\n", n, s[n%32], mark);

        // store the mark to the 'marks' array.
        marks[totalLength+j] = mark;
        newMarks[mark] = 1;
    }

    // We know deletion works, so instead of testing the deletion, we re-init glowWorm.
    glowwormInit(s, n, t, i, h);
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

    DFSDecoder(newMarks, decodedMsg, lenM, lenK, totalLength, badMarksLen, mask, s, n, t, i , h);


    // print the decoded message
    printf("\n\nDecoded message:\n");
    printArray(decodedMsg, totalLength);

    return 0;
}

int foundInArray( uint64 array[], int arrayLength, uint64 value){

    int found = 0;
    int index = 0;
    while( !found && index < arrayLength ){
        found = array[index] == value;
        index++;
    }

    return found;
}

void printArray( uint64 array[], int arrayLength ){

    if( !arrayLength ){
        printf("Empty Array\n");
        return;
    }
    for( int j = 0; j < arrayLength; j++ ){
        printf("%d", array[j]);
    }
    printf("\n");
}

// ********************************
// *** Proof of concept decoder *** #2 (DFS)
// ********************************
// This will be slightly better, with a closer-to-true DFS algorithm.
// Assume: glowworm is fully initialized with h, s, n, t, and i
// Assume: Marks are stored within a requisite array, 'marks'

// Results: This works quite well. Even with the addition of "bad" marks and
//      using only a codewordBits = 6, we were able to decipher the original
//      message. The "bad" bits are defined in a 1010... manner whereas the message
//      is 0101...
//  The table below shows the number of steps it took for a given number of BadMarks
//        and codewordBits:
//  BadMarksLen     CodewordBits   Steps
//      0           6               69
//      0           7               48
//      0           8               48
//      0           10              45
//      0           20              45
//      0           30              45
//      8           6               72
//      16          6               96
//      20          6               99
//      24          6               99
//      28          6               102
//      30          6               87 (Invalid Msg: Check Bit Error!)
void DFSDecoder(int newMarks[], uint64 decodedMsg[], int lenM, int lenK, int totalLength, int badMarksLen, uint64 mask, uint64 s[], uint64 n, uint64 t, uint64 i, uint64 h){

    // Create a variable to store the current "mark"
    uint64 decodeMark;


    // We should use three states to search for the message:
    // 0: Add 0
    // 1: Add 1
    // 2: Examine Prev Bit and take appropriate action
    int decoderState = 0;
    int msgBit = 0;
    int stepCount = 0;
    while( msgBit < lenM ){
        stepCount++;
        printf("\nCurrent Array: ");
        printArray(decodedMsg, msgBit);
        switch( decoderState ){

            case 0: // Add 0
                // Test the existence of an added 0
                glowwormAddBit( (uint64) 0 , s, n, t);
                decodeMark = s[n%32] & mask;

                // See if the 0-bit was valid. If it wasn't, then remove the zero and go to State 1
                if( !newMarks[ decodeMark ] ) {
                    glowwormDelBit( 0, s, n, t);
                    decoderState = 1;

                    printf("State 0: Didn't find 0 at position %d.\n", msgBit);
                }
                else{
                    decodedMsg[msgBit] = (uint64) 0;
                    msgBit++;

                    printf("State 0: Found 0 at position %d.\n", msgBit);
                }
                break;

            case 1: // Add 1
                // Test the existence of an added 0
                glowwormAddBit( (uint64) 1 , s, n, t);
                decodeMark = s[n%32] & mask;

                // See if the 1-bit was valid. If it wasn't, then remove the one and go to State 2
                if( !newMarks[ decodeMark ] ){
                    glowwormDelBit( 1, s, n, t);
                    decoderState = 2;

                    printf("State 1: Didn't find 1 at position %d.\n", msgBit);
                }
                else{
                    decodedMsg[msgBit] = (uint64) 1;
                    msgBit++;
                    decoderState = 0; // back to 0

                    printf("State 1: Found 1 at position %d.\n", msgBit);
                }
                break;

            case 2: // Examine Prev Bit and backtrack as needed
                if( decodedMsg[--msgBit] ){
                    // Previous bit is a 1
                    glowwormDelBit( 1, s, n, t);
                    printf("Backtrack: Deleting a 1 at position %d.\n", msgBit);
                }
                else{
                    // Previous bit is a 0
                    glowwormDelBit( 0, s, n, t);
                    decoderState = 1;
                    printf("Backtrack: Deleting a 1 at position %d.\n", msgBit);
                }
                break;

            default: break;

        }
    }

    printf("\nSteps: %d\n", stepCount);

    // Then, search for the check bits (assume all 0s)
    for ( int checkBit = lenM; checkBit < totalLength ; checkBit++ ){

        // Test the existence of an added 0
        glowwormAddBit( (uint64) 0 , s, n, t);
        decodeMark = s[n%32] & mask;

        if( !newMarks[ decodeMark ] ) {
            checkBit = totalLength; //break the loop
            printf("********************\n**Check Bit Error***\n********************\nInvalid Message Found!");
        }
        else {
            decodedMsg[checkBit] = (uint64) 0;
            //debug
            //printf("Found check bit 0 at position %d with mark %d\n", checkBit, decodeMark);
        }
    }

    // *********** END ****************
    // *** Proof of concept decoder *** #2
    // ********************************


}


// ********************************
// *** Proof of concept decoder *** #1
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
void basicDecoder(uint64 marks[], uint64 decodedMsg[], int lenM, int lenK, int totalLength, uint64 mask, uint64 s[], uint64 n, uint64 t, uint64 i, uint64 h){


    // To implement a basic decoder, we must implement a depth-first search.
    // The decoder receives a number of "marks" that we will need to process.
    // The decoder will test for the existence of each mark according to the glowworm
    // hash function and decide if a proper message exists.


    // Create a variable to store the current "mark"
    uint64 decodeMark0;
    uint64 decodeMark1;

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

    // *********** END ****************
    // *** Proof of concept decoder *** #1
    // ********************************



}
