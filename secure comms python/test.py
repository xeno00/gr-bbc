from msilib.schema import BBControl


import BBCCodecOO as bbc

mycodec = bbc.Codec()
s = "hello my name is james"
b = bytearray()
b.extend(s.encode(encoding="ASCII"))
print(mycodec.bbc_decode(mycodec.bbc_encode(s)))

