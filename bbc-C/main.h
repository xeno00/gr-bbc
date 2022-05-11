
#ifndef BBC_C_MAIN_H
#define BBC_C_MAIN_H

#include "bbc.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

void runDecoderV3( uint64 mask, int newMarks[], int lenM, int lenK, int printFlag );
void createTestMessage( int lenM, int lenK, uint64* messageArray );
float packetDensity(int * newMarks, int lenMarks);
void addBadMarks(int * newMarks, int lenMarks, float targetMarkDensity);

#endif //BBC_C_MAIN_H
