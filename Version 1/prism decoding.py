from correction import correct
from valid import valid
from struct import unpack

def decode(ElevenIn):##Assume no errors Exist
    return ElevenIn[0:6]

def check_and_decode(ElevenIn):##must be tuple
    if ElevenIn in valid:
        TrueVal=ElevenIn
        Trustworthy=True
    else:
        print("Value Corrupted")
        print("Attempting Repair")
        try:
            TrueVal=correct(ElevenIn)
            print("Successful Repair")
            Trustworthy=True
        except:
            print("Can't repair value. Over Corrupted, continuing anyway.\n Repair manually with context clues")
            TrueVal=correct(ElevenIn)
            Trustworthy=False
    return decode(TrueVal),Trustworthy

def bits(B):
    L=[B&1]
    B=B>>1
    for i in range(7):
        L.append(B&1)
        B=B>>1
    return L

def to_bytes(Bits):
    Out=b""
    while Bits:
        N=0
        if len(Bits)>7:
            for n in range(8):
                N+=Bits[7-n]<<n
            Bits=Bits[8:]
        else:
            for n in range(len(Bits)):
                N+=Bits[n]<<n
            Bits=Bits[8:]
        Out+=bytes([N])
    return Out
    
    

class decoder:
    def __init__(self,InFile):
        self.InChunk=8*11#every 6x8
        self.OutChunk=6*8#every 8x11
        self.InFile=open(InFile,"rb")
        self.inbuffer=[]
        self.outbuffer=[]
    def load_to_memory(self):
        while 1:
            Data=self.InFile.read(11)
            if Data:
                for i in Data:
                    currentByte=i
                    currentBits=bits(currentByte)
                    self.inbuffer+=currentBits
                if len(Data)>=2:
                    self.last2=Data[-2:]
                elif len(Data)==1:
                    self.last2=self.last2[-1:]+Data
            else:
                break
        self.extrabits=unpack("BB",self.last2)#Last 2 bytes represent how many bits padding were required to fit into 8 bit chunks
        self.inbuffer=self.inbuffer[:-(16+self.extrabits[0])]
        return 1
    def decode_memory(self):
        while self.inbuffer:
            self.outbuffer+=self.inbuffer[:6]
            self.inbuffer=self.inbuffer[11:]
        if self.extrabits[1]>0:
            self.outbuffer=self.outbuffer[:0-self.extrabits[1]]
    def check_decode_memory(self):
        Error=False
        while len(self.inbuffer)>11:
            Outchunk,Repaired=check_and_decode(tuple(self.inbuffer[:11]))
            self.outbuffer+=Outchunk
            Error=Error or Repaired
            self.inbuffer=self.inbuffer[11:]
        self.outbuffer+=self.inbuffer[:6]
        if self.extrabits[1]>0:
            self.outbuffer=self.outbuffer[:0-self.extrabits[1]]

def Decode_File(filename):
    D=decoder(filename)
    D.load_to_memory()
    D.decode_memory()
    return to_bytes(D.outbuffer)

def Check_And_Decode_File(filename):
    D=decoder(filename)
    D.load_to_memory()
    D.check_decode_memory()
    return to_bytes(D.outbuffer)


if __name__=='__main__':
    B=Check_And_Decode_File("prism encoding encoded.enc")
    Decoded=B.decode()
    print(Decoded)
