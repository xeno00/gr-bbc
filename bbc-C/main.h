
#ifndef BBC_C_MAIN_H
#define BBC_C_MAIN_H

#include "bbc.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

float packetDensity(int * newMarks, int lenMarks);
float addBadMarks(int * newMarks, int lenMarks, float targetMarkDensity);

#endif //BBC_C_MAIN_H
