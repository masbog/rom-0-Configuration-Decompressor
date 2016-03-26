#!/usr/bin/env python
# -*- coding: utf-8 -*- 

# Title: ZTE, TP-Link, ZynOS, Huawei rom-0 Configuration Decompressor 
# Author: Osanda Malith Jayathissa (@OsandaMalith)
# Special thanks to Nick Knight
# Use this for educational purposes only
# Author takes no responsibility for any damage you cause

from __future__ import print_function
import re
import collections
import unicodedata
 
class BitReader:
    
    def __init__(self, bytes):
        self._bits = collections.deque()
        
        for byte in bytes:
            byte = ord(byte)
            for n in xrange(8):
                self._bits.append(bool((byte >> (7-n)) & 1))
            
    def getBit(self):
        return self._bits.popleft()
        
    def getBits(self, num):
        res = 0
        for i in xrange(num):
            res += self.getBit() << num-1-i
        return res
        
    def getByte(self):
        return self.getBits(8)
        
    def __len__(self):
        return len(self._bits)
        
class RingList:
    
    def __init__(self, length):
        self.__data__ = collections.deque()
        self.__full__ = False
        self.__max__ = length
 
    def append(self, x):
        if self.__full__:
            self.__data__.popleft()
        self.__data__.append(x)
        if self.size() == self.__max__:
            self.__full__ = True
 
    def get(self):
        return self.__data__
 
    def size(self):
        return len(self.__data__)
 
    def maxsize(self):
        return self.__max__
        
    def __getitem__(self, n):
        if n >= self.size():
            return None
        return self.__data__[n]

print ('''[+] ZTE, TP-Link, ZynOS, Huawei rom-0 Configuration Decompressor
[+] Author: Osanda Malith Jayathissa 
[+] Special thanks to Nick Knight
''')
print ('[*] Opeining rom-0 file')
fpos=8568
fend=8788
fhandle=file('rom-0')
fhandle.seek(fpos)
chunk="*"
amount=221
while fpos < fend:
    if fend-fpos < amount:
        amount = amount
        data = fhandle.read(amount)
        fpos += len(data)
        
reader = BitReader(data)
result = ''
   
window = RingList(2048)
    
while True:
    bit = reader.getBit()
    if not bit:
        char = reader.getByte()
        result += chr(char)
        window.append(char)
    else:
        bit = reader.getBit()
        if bit:
            offset = reader.getBits(7)
            if offset == 0:
                break
        else:
            offset = reader.getBits(11)
        
        lenField = reader.getBits(2)
        if lenField < 3:
            lenght = lenField + 2
        else:
            lenField <<= 2
            lenField += reader.getBits(2)
            if lenField < 15:
                lenght = (lenField & 0x0f) + 5
            else:
                lenCounter = 0
                lenField = reader.getBits(4)
                while lenField == 15:
                    lenField = reader.getBits(4)
                    lenCounter += 1
                lenght = 15*lenCounter + 8 + lenField
        
        for i in xrange(lenght):
            char = window[-offset]
            result += chr(char)
            window.append(char)



def filter_non_printable(str):
  return ''.join([c for c in str if ord(c) > 31 or ord(c) == 9])


def regex(path, text):
    match = re.search(path, text)
    if match:
        return match.group()
    else:
        return None
print (('[+] Dump: \r\n{0}\r\n').format(result))
result = filter_non_printable(result).decode('unicode_escape').encode('ascii','ignore');
print (('[+] Filtered Strings: {0}\n').format(result))

if 'TP-LINK' in result:
    result = ''.join(result.split()).split('TP-LINK', 1)[0] + 'TP-LINK';
    result = result.replace("TP-LINK", "")
    result = result[1:]

if 'ZTE' in result:
    result = ''.join(result.split()).split('ZTE', 1)[0] + 'ZTE';
    result = result.replace("ZTE", "")
    result = result[1:]

if 'tc160' in result:
    result = ''.join(result.split()).split('tc160', 1)[0] + 'tc160';
    result = result.replace("tc160", "")
    result = result[1:]
    
print (('[~] Router Password is: {0}').format(result))
