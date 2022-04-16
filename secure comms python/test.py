from msilib.schema import BBControl


import BBCCodecOO as bbc

mycodec = bbc.Codec()
s = "hello my name is james. I wrote this encoder in python. This codec uses the BBC encoding scheme. If I wanted to share keys, this is how I would do it."
b = bytearray()
b.extend(s.encode(encoding="ASCII"))
print(mycodec.bbc_decode(mycodec.bbc_encode(s)))

