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
    int printPossibleMessages = 0; // do we want to print possible messages in the terminal or no
    float targetMarksDensity = 0.504;
    int totalLength = lenM+lenK;

    // This creates 2^codewordBits combo. It should be at least 1 higher than the minimum required.
    // In this case, the max for codewordBits is 63 due to using the uint64 type.
    int codewordBits = 18;
    //Deprecated: int badMarksLen = 0; // up to 30... see the section on adding erroneous bits
    uint64 mask = (1 << codewordBits) - 1; // This creates a mask with codewordBits number of 1s



    //******************* Encoding *********************

    // Init the "raw" array. This contains M and K bits together as one for the message to go into.
    uint64 raw[lenM+lenK];

    //populate the "raw" array
    createTestMessage(lenM, lenK, raw);

    //DEBUG: Print the raw message
    printf("\n\nRaw message:\n");
    printArray(raw, totalLength);


    //Initialize glowworm and check to see if glowworm was initialized correctly. The value in position 0 should be equal to 'h'
    glowwormInit(gwS, gwN, gwT, gwI, gwH);
    if( gwH != CHECKVALUE ){
        printf("Init Failed: 0x%llx\n", gwH);
    }


    // Deprecated: Create a 'marks' array to store all marks.
    //uint64 marks[ totalLength + badMarksLen ];

    // Create a variable to store the current glowWorm "mark"
    uint64 mark;

    // Create an array to store all the marks
    int newMarks[ mask + 1 ];
    memset(newMarks, 0, sizeof newMarks);


    // The mark is calculated using the last 'codewordBits' of the data in the buffer;
    //      the position of the data within the buffer 's' depends on n%32.
    for (int j = 0; j < totalLength; j++ ){
        glowwormAddBit( (uint64)raw[j] , gwS, gwN, gwT);
        mark = gwS[gwN%32] & mask;
        //printf("%d: %llx with mark %d\n", gwN, gwS[gwN%32], mark);

        // store the mark to the 'marks' array. Deprecated: marks[j] array
        //marks[j] = mark;
        newMarks[mark] = 1;
    }

    // Add extra "bad" marks
    addBadMarks(newMarks, mask+1, targetMarksDensity);



    //******************* Decoding *********************

    runDecoderV3( mask, newMarks, lenM, lenK, printPossibleMessages );

    return 0;
}

/**
 * Runs the DFSDecoder3 function while providing statistics and possible messages if required.
 * @param mask A mask with the number of code word bits. Required for GlowWorm.
 * @param marks The "marks" to decode
 * @param lenM The length of the message
 * @param lenK The length of the check bits (assume all 0)
 * @param printFlag Set to 1 to print the possible messages; 0 to suppress output.
 */
void runDecoderV3( uint64 mask, int marks[], int lenM, int lenK, int printFlag){

    // We know deletion works, so instead of testing the deletion, we re-init glowWorm.
    glowwormInit(gwS, gwN, gwT, gwI, gwH);

    uint64 decodedMsg[lenM+lenK];


/*  This is the implementation for DFS Decoder V3, which returns all the valid decoded messages and depends on main.c
 *  to store the state and resume the decoding */

    int decoderState = 1;
    int decoderMsgBit = 0;
    uint64 decodeMark = 0;
    int decoderStepCount = 0;
    int decoderIsMsgValid = 1;
    int isThereMore = 1;

    int maxIter = 300000;
    int iter = 0;

    int validMsgs = 0;

    clock_t start, end;
    double cpu_time_used = 0;

    while( isThereMore && iter<maxIter ) {

        start = clock();
        DFSDecoder3(marks, decodedMsg, lenM, lenK, mask, &decodeMark, &decoderState, &decoderStepCount,
                    &decoderMsgBit,
                    &decoderIsMsgValid, &isThereMore);
        end = clock();
        cpu_time_used += ((double) (end - start)) / CLOCKS_PER_SEC;

        if (decoderIsMsgValid){
            if(printFlag) {
                printf("\n\nPossible Decoded message:\n");
                printArray(decodedMsg, (lenM+lenK) );
            }
            validMsgs++;
        }

        iter++;
    }

    printf( "total steps: %d\n", decoderStepCount);
    printf( "Number of \"valid\" messages: %d\n", validMsgs);

    printf("Packet Density: %f\n", packetDensity( marks, mask + 1));
    printf("Time used: %f\n", cpu_time_used);

    //print the decoded message
    // printf("\n\nDecoded message:\n");
    // printArray(decodedMsg, totalLength);

}


/**
 * Creates a test message based on a message and check bits length. The message alternates 0 and 1
 * and the check bits are all 0.
 * @param lenM The length of the message
 * @param lenK The number of the check bits
 * @param messageArray The array to insert the message into. This *must* be initialized with size lenM+lenK
 */
void createTestMessage( int lenM, int lenK, uint64* messageArray ){

    // Init message M
    uint64 m[lenM];

    //*** Testing only *** Init M with dummy data (alternating 0s and 1s )
    // This should represent the actual message M when not testing.
    for ( int i = 0; i < lenM; i++ ){
        m[i] = i%2;
    }


    // Init message K
    uint64 k[lenK];

    //*** Testing only *** Init K as several zeroes.
    // This should represent the actual check bits K when not testing.
    for ( int i = 0; i < lenK; i++ ){
        k[i] = 0;
    }

    memcpy(messageArray, &m, sizeof(m));
    memcpy(messageArray+lenM, &k, sizeof(k));

}


/**
 * Packet Density returns the density of marks inside the array.
 * @param newMarks The array containing the marks
 * @param lenMarks The length of the newMarks array
 * @return The density of marks
 */
float packetDensity(int * newMarks, int lenMarks){

    float total = 0;

    for( int i = 0; i < lenMarks; i++ ){
        total += newMarks[i];
    }

    return total/lenMarks;
}

/**
 * Adds "bad" marks to the array containing marks up to a targeted density of totl marks
 * @param newMarks The array containing the marks
 * @param lenMarks THe length of the newMarks array
 * @param targetMarkDensity The target density of marks
 * @return
 */
void addBadMarks(int * newMarks, int lenMarks, float targetMarkDensity){

    for( int i = 0; i < lenMarks; i++ ){
        if( ((float) rand()/ (float) RAND_MAX) < targetMarkDensity )
            newMarks[i] = 1;
    }

}