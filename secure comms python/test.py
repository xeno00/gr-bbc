from msilib.schema import BBControl


import BBCCodecIterative as bbc
import sys

sys.setrecursionlimit(1028)
#s = "hello my name is james. I wrote this encoder in python. This codec uses the BBC encoding scheme. If I wanted to share keys, this is how I would do it." # 150 bytes
#s = "hello my name is james. I wrote this encoder in python. This codec uses the BBC encoding scheme to share keys." # 110 bytes
# s1 = "AB"
# s2 = "DF"
s1 = "AB"
s2 = "DF"
MSG_LEN=len(s1)*8  # needs to be in bits for BBCCodecOO.py
COD_LEN = 2**10    # needs to be in bits for BBCCodecOO.py
CHK_LEN = 0

mycodec = bbc.Codec(MSG_LEN, COD_LEN, CHK_LEN)
#b = bytearray()  # what is this for?
#b.extend(s.encode(encoding="ASCII")) # what is this for?

# Encode
bbcencoded1 = mycodec.bbc_encode(s1)
bbcencoded2 = mycodec.bbc_encode(s2)
# OR the two codewords together to synthesize a new code word
bbcencoded = (int.from_bytes(bbcencoded1,"little") | int.from_bytes(bbcencoded2,"little")).to_bytes(len(bbcencoded1),"little")

# rearrange the codeword to be more visually appealing
bbcencodedcorr1 =  ' '.join([format(bbcencoded1[i],'#010b')[2:] for i in range(int(COD_LEN/8)-1,-1,-1)])
bbcencodedcorr2 =  ' '.join([format(bbcencoded2[i],'#010b')[2:] for i in range(int(COD_LEN/8)-1,-1,-1)])
bbcencodedcorr  =  ' '.join([format(bbcencoded[i], '#010b')[2:] for i in range(int(COD_LEN/8)-1,-1,-1)])
#print("Codeword1 is: " + str(bbcencodedcorr1))
#print("Codeword2 is: " + str(bbcencodedcorr2))
#print("Codeword0 is: " + str(bbcencodedcorr))

#Decode
bbcdecoded = mycodec.bbc_decode(bbcencoded)
for msg in range(len(bbcdecoded)):
    try:
        print("Possible decoded Message is: " + bbcdecoded[msg].decode("ASCII") )
    except:
        print("Possible decoded Message is: " + str(bbcdecoded[msg]))


