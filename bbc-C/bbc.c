//
// Created by felix on 17/02/2022.
//

#include "bbc.h"

uint64 gwS[32];       //buffer to store the hash. This is on a rotating basis, mod 32.
uint64 gwN;    //current string length counter
uint64 gwT, gwI, gwH;     //temporary variables
uint64 CHECKVALUE = 0xCCA4220FC78D45E0;   // This should be the value of 'h' when glowworm is initialized.

// DFS Decoder 3 improves on DFSDecoder2 and returns every true message!
int DFSDecoder3(int newMarks[], uint64 decodedMsg[], int lenM, int lenK, uint64 mask, uint64* decodeMark,
                int* decoderState, int* stepCount, int* msgBit, int* isMsgValid, int* isThereMore){

    // Create a variable to store the current "mark"
    //uint64 decodeMark;

    /* We'll use 8 states:
     * 1: Add 0 and check for mark
     * 2: Remove 0 (flows into case 3)
     * 3: then add 1 and check for mark
     * 4: Remove 1 (flows into case 5)
     * 5: Examine Previous bit (check if 1)
     * 6: Remove 1 and check message length
     * 7: Check if message length reached
     * 8: Check message and examine previous bit.
     *
     * While some states can be combined, this requires only checking one state variable.
     */

    //int decoderState = 1;
    //int msgBit = 0;
    //int stepCount = 0;
    //int validCount = 0;

    *isThereMore = *msgBit <= lenM+lenK && *msgBit >= 0;

    while( *isThereMore ){

        // save/print statistics
        ++*stepCount;
        //printf("\nCurrent Array: ");
        //printUint64Array(decodedMsg, msgBit);
        //printf("Current bit: %d\n", msgBit);


        switch( *decoderState ){

            case 1: // Add 0
                // Test the existence of an added 0
                glowwormAddBit( (uint64) 0 , gwS, gwN, gwT);
                *decodeMark = gwS[gwN%32] & mask;

                // See if the 0-bit was valid. If it wasn't, then go to state 3; if it was, state 7
                if( !newMarks[ *decodeMark ] ) {

                    *decoderState = 2;

                    //printf("State 1: Didn't find 0 at position %d.\n", msgBit);
                }
                else{
                    decodedMsg[*msgBit] = (uint64) 0;
                    ++*msgBit;

                    *decoderState = 7;

                    //printf("State 1: Found 0 at position %d.\n", msgBit);
                }
                break;

            case 2: // Remove 0 (flows into case 3)
                glowwormDelBit( 0, gwS, gwN, gwT);
                //printf("State 2: Removing 0 at position %d.\n", msgBit);
                *decoderState = 3;

            case 3:  // Add 1 and check for mark


                // Test the existence of an added 1
                glowwormAddBit( (uint64) 1 , gwS, gwN, gwT);
                *decodeMark = gwS[gwN%32] & mask;

                // See if the 1-bit was valid. If it wasn't, then go to state 4; if it was, state 7
                if( !newMarks[ *decodeMark ] ){

                    *decoderState = 4;

                    //printf("State 3: Didn't find 1 at position %d.\n", msgBit);
                }
                else{
                    decodedMsg[*msgBit] = (uint64) 1;
                    ++*msgBit;

                    *decoderState = 7;

                    //printf("State 3: Found 1 at position %d.\n", msgBit);
                }
                break;


            case 4: // Remove 1 (flows into case 5)
                glowwormDelBit( 1, gwS, gwN, gwT);
                //printf("State 4: Removing 1 at position %d.\n", msgBit);
                *decoderState = 5;

            case 5:// Examine Prev Bit and backtrack as needed

                if( decodedMsg[--*msgBit] ){
                    // Previous bit is a 1

                    *decoderState = 6;
                    //printf("Backtrack 5: Found a 1 at position %d.\n", msgBit);
                }
                else{
                    // Previous bit is a 0
                    *decoderState = 2;
                    //printf("Backtrack 5: Found a 0 at position %d.\n", msgBit);
                }
                break;

            case 6: // Remove 1 and check for len = 0

                glowwormDelBit( 1, gwS, gwN, gwT);

                if( *msgBit == 0 ){
                    //printf("State 6: Msg Length %d.\n", msgBit);
                    return *stepCount; // need a better way to do this
                }
                else{
                    //printf("State 6: Msg Length %d.\n", msgBit);
                    *decoderState = 5;
                }

                break;

            case 7: // Check if msg length reached

                if( *msgBit != (lenM+lenK) ){
                    //printf("State 7: Msg length %d.\n", msgBit);
                    *decoderState = 1;
                    break;
                }
                // else flow into case 8
                //printf("State 7: Msg length reached @ %d.\n", msgBit);
                *decoderState = 8;

            case 8: //check valid message
                //printf("\nSteps: %d\n", stepCount);

                //printf("Current Array: ");
                //printUint64Array(decodedMsg, msgBit);


                //assume message is valid, then see if it's not
                *isMsgValid = 1;
                for( int j = 0; j < lenK && *isMsgValid; j++){
                    //printf("\nChecking Possible Message at position %d: %d\n", lenM+j, decodedMsg[lenM+j] );
                    *isMsgValid = ( decodedMsg[lenM+j] == 1 );
                }

                if( decodedMsg[--*msgBit] ){
                    // Previous bit is a 1
                    *decoderState = 6;
                    //printf("Backtrack 8(5): Found a 1 at position %d.\n", msgBit);
                }
                else{
                    // Previous bit is a 0
                    *decoderState = 2;
                    //printf("Backtrack 8(5): Found a 0 at position %d.\n", msgBit);
                }

                // Print valid message
                if( *isMsgValid ) {
                    //printf("Found Possible Message ");//#%4d: ", ++validCount);
                    //printUint64Array(decodedMsg, *msgBit);

                    return *stepCount;
                }
                break;

            default: break;

        }

        *isThereMore = (*msgBit <= lenM+lenK) && (*msgBit >= 0);
    }

    return *stepCount;

}




// DFS Decoder 2 implements true DFS covering all valid branches!
int DFSDecoder2(int newMarks[], uint64 decodedMsg[], int lenM, int lenK, int totalLength, int badMarksLen, uint64 mask){




    //******************* To Run DFSDecoder2, use *******************
    /* This is the implementation for DFS Decoder V2, which only returns the latest decoded message
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
    //printUint64Array(decodedMsg, totalLength);

    */
    //***************************************************************



    // Create a variable to store the current "mark"
    uint64 decodeMark;

    /* We'll use 8 states:
     * 1: Add 0 and check for mark
     * 2: Remove 0 (flows into case 3)
     * 3: then add 1 and check for mark
     * 4: Remove 1 (flows into case 5)
     * 5: Examine Previous bit (check if 1)
     * 6: Remove 1 and check message length
     * 7: Check if message length reached
     * 8: Check message and examine previous bit.
     *
     * While some states can be combined, this requires only checking one state variable.
     */

    int decoderState = 1;
    int msgBit = 0;
    int stepCount = 0;
    int isMsgValid;
    int validCount = 0;

    while( msgBit <= lenM+lenK && msgBit >= 0){

        // save/print statistics
        stepCount++;
        //printf("\nCurrent Array: ");
        //printUint64Array(decodedMsg, msgBit);
        //printf("Current bit: %d\n", msgBit);


        switch( decoderState ){

            case 1: // Add 0
                // Test the existence of an added 0
                glowwormAddBit( (uint64) 0 , gwS, gwN, gwT);
                decodeMark = gwS[gwN%32] & mask;

                // See if the 0-bit was valid. If it wasn't, then go to state 3; if it was, state 7
                if( !newMarks[ decodeMark ] ) {

                    decoderState = 2;

                    //printf("State 1: Didn't find 0 at position %d.\n", msgBit);
                }
                else{
                    decodedMsg[msgBit] = (uint64) 0;
                    msgBit++;

                    decoderState = 7;

                    //printf("State 1: Found 0 at position %d.\n", msgBit);
                }
                break;

            case 2: // Remove 0 (flows into case 3)
                glowwormDelBit( 0, gwS, gwN, gwT);
                //printf("State 2: Removing 0 at position %d.\n", msgBit);
                decoderState = 3;

            case 3:  // Add 1 and check for mark


                // Test the existence of an added 1
                glowwormAddBit( (uint64) 1 , gwS, gwN, gwT);
                decodeMark = gwS[gwN%32] & mask;

                // See if the 1-bit was valid. If it wasn't, then go to state 4; if it was, state 7
                if( !newMarks[ decodeMark ] ){

                    decoderState = 4;

                    //printf("State 3: Didn't find 1 at position %d.\n", msgBit);
                }
                else{
                    decodedMsg[msgBit] = (uint64) 1;
                    msgBit++;

                    decoderState = 7;

                    //printf("State 3: Found 1 at position %d.\n", msgBit);
                }
                break;


            case 4: // Remove 1 (flows into case 5)
                glowwormDelBit( 1, gwS, gwN, gwT);
                //printf("State 4: Removing 1 at position %d.\n", msgBit);
                decoderState = 5;

            case 5:// Examine Prev Bit and backtrack as needed

                if( decodedMsg[--msgBit] ){
                    // Previous bit is a 1

                    decoderState = 6;
                    //printf("Backtrack 5: Found a 1 at position %d.\n", msgBit);
                }
                else{
                    // Previous bit is a 0
                    decoderState = 2;
                    //printf("Backtrack 5: Found a 0 at position %d.\n", msgBit);
                }
                break;

            case 6: // Remove 1 and check for len = 0

                glowwormDelBit( 1, gwS, gwN, gwT);

                if( msgBit == 0 ){
                    //printf("State 6: Msg Length %d.\n", msgBit);
                    return stepCount; // need a better way to do this
                }
                else{
                    //printf("State 6: Msg Length %d.\n", msgBit);
                    decoderState = 5;
                }

                break;

            case 7: // Check if msg length reached

                if( msgBit != (lenM+lenK) ){
                    //printf("State 7: Msg length %d.\n", msgBit);
                    decoderState = 1;
                    break;
                }
                // else flow into case 8
                //printf("State 7: Msg length reached @ %d.\n", msgBit);
                decoderState = 8;

            case 8: //check valid message
                //printf("\nSteps: %d\n", stepCount);

                //printf("Current Array: ");
                //printUint64Array(decodedMsg, msgBit);

                isMsgValid = 1;
                for( int j = 0; j < lenK && isMsgValid; j++){
                    //printf("\nChecking Possible Message at position %d: %d\n", lenM+j, decodedMsg[lenM+j] );
                    isMsgValid = ( decodedMsg[lenM+j] == 0 );
                }

                // Print valid message
                if( isMsgValid ) {
                    //printf("Found Possible Message #%4d: ", ++validCount);
                    //printUint64Array(decodedMsg, msgBit);
                }

                if( decodedMsg[--msgBit] ){
                    // Previous bit is a 1
                    decoderState = 6;
                    //printf("Backtrack 8(5): Found a 1 at position %d.\n", msgBit);
                }
                else{
                    // Previous bit is a 0
                    decoderState = 2;
                    //printf("Backtrack 8(5): Found a 0 at position %d.\n", msgBit);
                }
                break;

            default: break;

        }
    }

    return stepCount;

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


//Note: Requires "Marks" array.
// Deprecated: Create a 'marks' array to store all marks.
//uint64 marks[ totalLength + badMarksLen ];

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
        printUint64Array(decodedMsg, msgBit);
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

int foundInArray( uint64 array[], int arrayLength, uint64 value){

    int found = 0;
    int index = 0;
    while( !found && index < arrayLength ){
        found = array[index] == value;
        index++;
    }

    return found;
}


void printUint64Array(uint64 array[], int arrayLength ){

    if( !arrayLength ){
        printf("Empty Array\n");
        return;
    }
    for( int j = 0; j < arrayLength; j++ ){
        printf("%d", array[j]);
    }
    printf("\n");
}


void printIntArray(int array[], int arrayLength ){

    if( !arrayLength ){
        printf("Empty Array\n");
        return;
    }
    for( int j = 0; j < arrayLength; j++ ){
        printf("%d", array[j]);
    }
    printf("\n");
}