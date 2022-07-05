from msilib.schema import BBControl


import BBCCodecOO as bbc
import sys

sys.setrecursionlimit(1028)
#s = "hello my name is james. I wrote this encoder in python. This codec uses the BBC encoding scheme. If I wanted to share keys, this is how I would do it." # 150 bytes
#s = "hello my name is james. I wrote this encoder in python. This codec uses the BBC encoding scheme to share keys." # 110 bytes
s = "AB"
MSG_LEN=len(s)*8  # needs to be in bits for BBCCodecOO.py
COD_LEN = 2**7    # needs to be in bits for BBCCodecOO.py

mycodec = bbc.Codec(MSG_LEN, COD_LEN)
#b = bytearray()  # what is this for?
#b.extend(s.encode(encoding="ASCII")) # what is this for?

# Encode
bbcencoded = mycodec.bbc_encode(s)

# rearrange the codeword to be more visually appealing
bbcencodedcorr =  ' '.join([format(bbcencoded[i],'#010b')[2:] for i in range(int(COD_LEN/8)-1,-1,-1)])
print("Codeword is: " + str(bbcencodedcorr))

#Decode
bbcdecoded = mycodec.bbc_decode(bbcencoded)
for msg in range(len(bbcdecoded)):
    print("Possible decoded Message is: " + bbcdecoded[msg] )


