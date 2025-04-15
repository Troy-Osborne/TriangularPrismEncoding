from time import time
from encode import encode_dict
from struct import pack

def bits_to_bytes(Bits):
    Out=b""
    while Bits:
        N=0
        if len(Bits)>7:
            for n in range(8):
                N+=Bits[n]<<(7-n)
            Bits=Bits[8:]
        else:
            for n in range(len(Bits)):
                N+=Bits[n]<<(7-n)
            Bits=Bits[8:]
        Out+=bytes([N])
    return Out
    
def xor_list(L):
    return sum(L) & 1

def test(reps=10000):
    Start=time()
    for i in range(reps):
        encode((1,0,1,1,0,1))
    End=time()
    print(End-Start)
    return End-Start

def encode_func(SixIn):#Just for human reference
    #Don't run this function, instead
    #use the dictionry encode_dict for speed improvements
    L1,L2,L3,R1,R2,R3=SixIn
    Faces=[
        [L1,L2,L3],
        [R1,R2,R3],
        [L1,R1,R2,L2],
        [L2,R2,R3,L3],
        [L3,R3,R1,L1]]
    FiveOut=[xor_list(L) for L in Faces]
    return SixIn+FiveOut

def encode(SixIn):#input must be tuple
    return encode_dict[SixIn]

class encoder:
    def __init__(self,OutFile):
        self.inbuffer=[]
        self.InChunk=6*8#every 6x8
        self.OutChunk=8*11#every 8x11
        self.OutFile=open(OutFile,"wb")
        self.outbuffer=[]
    def add_bits(self,In):
        self.inbuffer+=In
        self.flush()
    def flush(self):
        while len(self.inbuffer)>=self.InChunk:
            for B in range(8):##remove 8 lots of 6 from in buffer
                self.outbuffer+=encode(tuple(self.inbuffer[0:6]))##add 8 lots of 11 to the outbuffer
                self.inbuffer=self.inbuffer[6:]
        while len(self.outbuffer)>=self.OutChunk:
            for B in range(11):##remove 11 lots of 8 from out buffer
                self.OutFile.write(bits_to_bytes(self.outbuffer[0:8]))
                self.outbuffer=self.outbuffer[8:]
    def close(self):
        AddedIn=0
        AddedOut=0
        while len(self.inbuffer)%6!=0:
            self.inbuffer.append(0)
            AddedIn+=1
        while self.inbuffer!=[]:
            self.outbuffer+=encode(tuple(self.inbuffer[0:6]))##add 8 lots of 11 to the outbuffer
            self.inbuffer=self.inbuffer[6:]
            
        while len(self.outbuffer)%8!=0:
            self.outbuffer.append(0)
            AddedOut+=1
        while self.outbuffer!=[]:
            self.OutFile.write(bits_to_bytes(self.outbuffer[0:8]))
            self.outbuffer=self.outbuffer[8:]
        
        Tail=pack("BB",AddedIn,AddedOut)
        self.OutFile.write(Tail)
            
        self.OutFile.close()

        
def bin8(i):
    s=bin(i)[2:]
    l=len(s)
    return [0]*(8-l)+list(map(int,s))

def bits(Bytes):
    out=[]
    for i in Bytes:
        out+=bin8(i)
    return out
    
def encode_string(Encoder,string):
    B=bits(string.encode())
    Encoder.add_bits(B)

def encode_text_file(InFileName,OutFileName):
    Encoder=encoder(OutFileName)
    InF=open(InFileName,'r')
    Text=InF.read()
    encode_string(Encoder,Text)
    InF.close()
    Encoder.close()
    return Encoder

if __name__=='__main__':
    encode_text_file("prism encoding.py","prism encoding encoded.enc")
