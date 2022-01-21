mylist=['a','b','c','d','e','f','g','h','i']
newlist = mylist[:-2]
print(newlist)
print(1<<2)
if 0:
    print("it evaluated to true")

print([n for n in range(3)])
print([1 for n in range(0)])

print("test commmencing")
item = [0, 1, 2]
for n in range(len(item)):
        # Build out the hash for each substring
        for j in range(n+1):
            print(item[j])
        print()

str1 = "hello world"
int1 = int.from_bytes(str1.encode(encoding='ascii'), byteorder='little')
int1 = int1>>2
int1 = int1<<2
str2 = int1.to_bytes(11, byteorder='little').decode(encoding='ascii')
print(str1, " len=", len(str1))
print(str2, " len=", len(str2))

import os
print(os.getcwd())


