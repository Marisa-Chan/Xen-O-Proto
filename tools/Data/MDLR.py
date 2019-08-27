#!/usr/bin/python3

import sys

ENCODING = {
	437 : "cp437",
	932 : "cp932",
	936 : "cp936",
	949 : "cp949",
	950 : "cp950",
	1033 : "cp1252", #LANG ID
	1048 : "cp1250", #LANG ID
	1252 : "cp1252",
}

LANG = {
	437 : "USA",
	932 : "JAPAN",
	936 : "CHINA",
	949 : "KOR",
	950 : "Big5",
	1033 : "EN",
	1048 : "RO",
	1252 : "EN",
}

def SDBM(b):
	v = 5381
	for a in b.encode("ascii"):
		v = (33 * v + a) & 0xFFFFFFFF
	return v

def GETENC(i):
	if i in ENCODING:
		return ENCODING[i]
	return "ascii"

def GETLANG(i):
	if i in LANG:
		return LANG[i]
	return "???"

class MDLRTXT:
	H = 0 # sdbm hash
	STR = None #list
	
	def __init__(self, H):
		self.H = H
		self.STR = list()

class MDLR:
	Langs = None
	Items = None
	
	def __init__(self, fpath):
		self.Langs = list()
		self.Items = dict()
		
		fl = open(fpath, "rb")
		fl.seek(0x14)
		
		NumLangs = int.from_bytes(fl.read(4), byteorder = "little")
		LCIDOFF = int.from_bytes(fl.read(4), byteorder = "little")
		NumStrings = int.from_bytes(fl.read(4), byteorder = "little")
		HashTableOFF = int.from_bytes(fl.read(4), byteorder = "little")
		LCIDTableOFF = int.from_bytes(fl.read(4), byteorder = "little")
		
		fl.seek(LCIDOFF)
		
		i = NumLangs
		while(i > 0):
			self.Langs.append( int.from_bytes(fl.read(4), byteorder = "little") )
			i -= 1
		
		HashTable = list()
		
		fl.seek(HashTableOFF)
		
		i = NumStrings
		while(i > 0):
			h = int.from_bytes(fl.read(4), byteorder = "little")
			txt = MDLRTXT(h)
			self.Items[h] = txt
			HashTable.append(txt)
			i -= 1
		
		lastoff = LCIDTableOFF
		
		i = 0
		while(i < NumLangs):
			enc = GETENC(  self.Langs[i]  )
			
			j = 0
			while(j < NumStrings):
				fl.seek(lastoff)
				stroff = int.from_bytes(fl.read(4), byteorder = "little")
				lastoff = fl.tell()
				
				fl.seek( stroff )
				sz = fl.read(1)[0]
				string = ""
				if sz:
					string = fl.read(sz).decode(enc)
					string = string.translate(str.maketrans( {"\n":  r"\n",
															  "\r":  r"\r",
															  "\t":  r"\r"} ) )
				HashTable[j].STR.append( string )
				
				j += 1
			
			i += 1
		
		fl.close()



def main():
	if len(sys.argv) == 1:
		print("script.py Filename.mdlr langID [lookupfile]")
		print("")
		exit(-1)

	mdlr = MDLR(sys.argv[1])
	
	if len(sys.argv) == 2:
		print("script.py Filename.mdlr langID [lookupfile]")
		print("Langs in this mdlr:")
		i = 0
		while ( i < len(mdlr.Langs) ):
			print( "{:d}:\t{}".format( i, GETLANG( mdlr.Langs[i] ) ) )
			i += 1
		
		print("")
		exit(-1)
	
	
	DICT = dict()
	
	if (len(sys.argv) == 4):
		f = open(sys.argv[3], "r")
		
		for l in f:
			l = l.strip()
			DICT[ SDBM(l) ] = l
		
		f.close()
	
	A = list()
	B = list()
	
	for h in mdlr.Items:
		if h in DICT:
			A.append( "{} = {}".format( DICT[h],mdlr.Items[h].STR[0] ) )
		else:
			B.append( "{:08X} = {}".format( h, mdlr.Items[h].STR[0] ) )
	
	A.sort()
	B.sort()
	
	for i in A:
		print(i)
	for i in B:
		print(i)
		

if __name__ == "__main__":
	main()
