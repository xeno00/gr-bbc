# Author: James C Morrison
# Date: 1/1//2022
# Project: ECE-499 Secure Communications
# 
# Description:
# Run a test using BBC encryption

from BBCcodec import decode_BBC
from BBCcodec import encode_BBC

codeword = encode_BBC('a')
print(decode_BBC(codeword))