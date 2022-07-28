from msilib.schema import BBControl
import BBCCodecIterative as bbc
import sys
class Harness:
    MSG_LEN = 2*8   #2**10
    COD_LEN = 2**10 #2**20
    CHK_LEN = 0
    mycodec = bbc.Codec(MSG_LEN, COD_LEN, CHK_LEN)
    s1 = "AB"
    s2 = "CD"
    s3 = "EF"
    s4 = "GH"
    s5 = "AH"
    s_110_B = "hello my name is james. I wrote this encoder in python. This codec uses the BBC encoding scheme to share keys."
    s_150_B = "hello my name is james. I wrote this encoder in python. This codec uses the BBC encoding scheme. If I wanted to share keys, this is how I would do it."
######################################################################################################################################################################
    def main_test(self):                # W R I T E    Y O U R     T E S T     H E R E 
        self.test_encode_decode(self.s1, self.s2, self.s3, self.s4, self.s5)




######################################################################################################################################################################
                                                   # B A C K     E N D

    # Pass, since we're using static variables rather than instance
    def init():
        pass

    # Pass a codeword and variable name to have it printed to the terminal
    def print_codeword(codeword, name="Codeword"):
        formatted = ' '.join([format(codeword[i],'#010b')[2:] for i in range(int(COD_LEN/8)-1,-1,-1)])
        print(name + " is: " + str(formatted))

    # Use built-in codec to test encoding
    def test_encode(self, message):
        return self.mycodec.bbc_encode(message)

    # Use built-in codec to test decoding
    def test_decode(self, codeword):
        decoded = self.mycodec.bbc_decode(codeword)
        for msg in range(len(decoded)):
            try:
                print("Possible decoded Message is: " + decoded[msg].decode("ASCII") )
            except:
                print("Possible decoded Message is: " + str(decoded[msg]))
        return decoded

    # Use built-in codec to test encoding, then decoding
    def test_encode_decode(self, *args):
        # encode each given message
        encodes = []
        for x in args:
            encodes.append(self.test_encode(x))
        # Combine resulting codewords
        master_codeword = self.combine_codewords(encodes)
        # Decode this "master codeword"
        return self.test_decode(master_codeword)
    
    def find_max_length(vector):
        max = 0
        for e in vector:
            if len(e)>max:
                max = len(e)
        return max

    def combine_codewords(self, words):
        result = 0
        for x in words:
            result |= int.from_bytes(x,"little")
        
        result = result.to_bytes(len(words[0]),"little")
        return result





test = Harness()
test.main_test()