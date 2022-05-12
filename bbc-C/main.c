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

    //******************* Setup *********************

    int lenM = 1016; // Number of message bits.
    int lenK = 8; // Number of check bits.
    int printPossibleMessages = 1; // do we want to print possible messages in the terminal or no
    int printStats = 0;
    float targetMarksDensity = 0.000;

    // Code Word Bits creates a 2^codewordBits combo. It should be at least 1 higher than the minimum required.
    // In this case, the max for codewordBits is 63 due to using the uint64 type.
    int codewordBits = 14;
    //Deprecated: int badMarksLen = 0; // up to 30... see the section on adding erroneous bits
    uint64 mask = (1 << codewordBits) - 1; // This creates a mask with codewordBits number of 1s



    //******************* Encoding *********************

    // Init the "raw" array. This contains M and K bits together as one for the message to go into.
    uint64* raw = (uint64*) malloc((lenM+lenK) * sizeof(uint64));
    //uint64 raw[lenM+lenK];

    //populate the "raw" array
    createTestMessage(lenM, lenK, raw);

    //DEBUG: Print the raw message
    printf("\n\nRaw message:\n");
    printUint64Array(raw, lenM + lenK);

    // Create an array to store all the marks
    int newMarks[ mask + 1 ];
    memset(newMarks, 0, sizeof newMarks);


    // Encode!
    encodeMessage( lenM, lenK, codewordBits, mask, raw, newMarks );

    // Add extra "bad" marks
    addBadMarks(newMarks, mask+1, targetMarksDensity);


    //******************* Decoding *********************

    // runDecoderV3( mask, newMarks, lenM, lenK, printPossibleMessages );

    // Let's test decoding a rolling array...

    int totalValidMsgs = 0;
    int stepCount = 0;

    for( int i = 0; i < mask+1; i++ ){

        int* rollingDecodeMarks = (int*) calloc(((mask + 1)), sizeof(int) );

        // this pretty much simulates a ring buffer (but is a poor implementation)!
        memcpy(rollingDecodeMarks+i, newMarks, sizeof(newMarks)-sizeof(int)*i);
        memcpy( rollingDecodeMarks, newMarks, sizeof(int)*i);

        totalValidMsgs += runDecoderV3( mask, rollingDecodeMarks, lenM, lenK, &stepCount, printPossibleMessages, printStats );

        free(rollingDecodeMarks);

        // prints every 1000 iterations to display progress to user.
        if(!(i%1000)) {
            printf("\n%d... steps: %d", i, stepCount);
        }
    }

    printf("totalValidMessages: %d", totalValidMsgs);

    return 0;
}

void encodeMessage( int lenM, int lenK, int numCodewordBits, uint64 mask, uint64 raw[], int encodedArray[] ){

    //Initialize glowworm and check to see if glowworm was initialized correctly. The value in position 0 should be equal to 'h'
    glowwormInit(gwS, gwN, gwT, gwI, gwH);

    if( gwH != CHECKVALUE ){
        printf("Init Failed: 0x%llx\n", gwH);
    }

    // Create a variable to store the current glowWorm "mark"
    uint64 mark;

    // The mark is calculated using the last 'codewordBits' of the data in the buffer;
    //      the position of the data within the buffer 's' depends on n%32.
    for (int j = 0; j < (lenM+lenK); j++ ){
        glowwormAddBit( (uint64)raw[j] , gwS, gwN, gwT);
        mark = gwS[gwN%32] & mask;
        //printf("%d: %llx with mark %d\n", gwN, gwS[gwN%32], mark);

        // store the mark to the 'marks' array. Deprecated: marks[j] array
        //marks[j] = mark;
        encodedArray[mark] = 1;
    }

}

/**
 * Runs the DFSDecoder3 function while providing statistics and possible messages if required.
 * @param mask A mask with the number of code word bits. Required for GlowWorm.
 * @param marks The "marks" to decode
 * @param lenM The length of the message
 * @param lenK The length of the check bits (assume all 0)
 * @param printMessageFlag Set to 1 to print the possible messages; 0 to suppress output.
 * @param printStatsFlag Set to 1 to print the stats; 0 to suppress output.
 * @return number of valid messages
 */
int runDecoderV3( uint64 mask, int marks[], int lenM, int lenK, int *stepCount, int printMessageFlag, int printStatsFlag){

    // We know deletion works, so instead of testing the deletion, we re-init glowWorm.
    glowwormInit(gwS, gwN, gwT, gwI, gwH);

    uint64 decodedMsg[lenM+lenK];
    memset(decodedMsg, 0, sizeof(decodedMsg));


/*  This is the implementation for DFS Decoder V3, which returns all the valid decoded messages and depends on main.c
 *  to store the state and resume the decoding */

    int decoderState = 1;
    int decoderMsgBit = 0;
    uint64 decodeMark = 0;
    int * decoderStepCount = stepCount;
    int decoderIsMsgValid = 0;
    int isThereMore = 1;

    int maxIter = 300000;
    int iter = 0;

    int validMsgs = 0;

    clock_t start, end;
    double cpu_time_used = 0;

    //for checking if all 0s in decoded message
    uint64 isNotAll0=0;

    while( isThereMore && iter<maxIter ) {

        start = clock();
        DFSDecoder3(marks, decodedMsg, lenM, lenK, mask, &decodeMark, &decoderState, decoderStepCount,
                    &decoderMsgBit,
                    &decoderIsMsgValid, &isThereMore);
        end = clock();
        cpu_time_used += ((double) (end - start)) / CLOCKS_PER_SEC;

        //check if message is all 0; if yes, assume invalid.
        // NOTE: This also excludes a leading '1' in the first three positions such as 001000000...
        for (int i = 3; i < lenM && isNotAll0 != 1; i++ ){
            isNotAll0 |= decodedMsg[i];
        }

        if (decoderIsMsgValid && isNotAll0 ){
            if(printMessageFlag) {
                printf("\n\nPossible Decoded message:\n");
                printUint64Array(decodedMsg, (lenM + lenK));
            }
            validMsgs++;
            decoderIsMsgValid = 0;
        }

        iter++;
    }

    if( isNotAll0 && printStatsFlag ) {
        printf("total steps: %d\n", &decoderStepCount);
        printf("Number of \"valid\" messages: %d\n", validMsgs);
        printf("Packet Density: %f\n", packetDensity(marks, mask + 1));
        printf("Time used: %f\n", cpu_time_used);
    }
    //print the decoded message
    // printf("\n\nDecoded message:\n");
    // printUint64Array(decodedMsg, totalLength);

    return validMsgs;
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

    //*** Testing only *** Init K as several zeroes or ones.
    // This should represent the actual check bits K when not testing.
    for ( int i = 0; i < lenK; i++ ){
        k[i] = 1;
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