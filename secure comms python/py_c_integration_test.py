import BBCCodecNum as bbc
import ctypes
#gw = ctypes.CDLL("secure comms python/glowworm.so")

#print(type(gw))
#cw = bbc.encode_BBC(message="hello world", num_checksum=2)
#print(bin(cw))
#print(gw.add1())
#print(windll.kernel32.add1) 

#gw[1] refrences the first real function in the c file, in this case, add1
#print(gw[1]())

# __________
print("running")
message = 0b0110
cw1 = bbc.encode_BBC(message)
print(cw1)
print("completed")
