import math


class OpenBaseNumber:
    def __init__(self,base_chars:str,*args, **kwargs):
        self.BASE:int = len(base_chars)
        self.CHARS_ARR:list[str] = list(base_chars)
        self.NUM_OBJ:dict[str,int] = { chr:i for i,chr in enumerate(self.CHARS_ARR)}
    #------------------
    def convert(self,num:int):
        builder:str = ''
        while(num > 0):
            index = num % self.BASE
            builder = self.CHARS_ARR[index] + builder
            num = math.floor(num/self.BASE)
        #------------------
        return builder
    #------------------
    def getNumber(self,converted_number:str):
        sum = 0
        strLength = len(converted_number) - 1
        for i,char in enumerate(converted_number):
            sum += self.NUM_OBJ[char] * (self.BASE ** (strLength - i))
        #------------------
        return sum
#------------------

class Base36(OpenBaseNumber):
    def __init__(self):
        super().__init__("0123456789abcdefghijklmnobqrstuvwxyz")
    #------------------
#------------------