#!/usr/bin/python3

import zlib

def decodeItem(data, off):
	decsz	= int.from_bytes(data[off + 4 : off + 8], "little")
	compsz	= int.from_bytes(data[off + 8 : off + 12], "little")
	
	d = None
	
	if data[off + 12] == 1:
		d = bytearray(zlib.decompress(data[off+13 : off+13+compsz]))
	else:
		d = bytearray(data[off+13 : off+13+decsz])
	
	return d

a = open("GCTAI.DRA", "rb")
b = a.read()
a.close()

cnt = int.from_bytes(b[0x10:0x14], "little")

i = 0
while i < cnt:
	off = 0x15 + i * 8
	itemID  = int.from_bytes(b[off + 0 : off + 4], "little")
	itemOff = int.from_bytes(b[off + 4 : off + 8], "little")
	
	itmInf = decodeItem(b, itemOff)
	
	s = open("GCTAI/" + str(itemID) +".raw", "wb")
	s.write(itmInf)
	s.close()
	
	print(itemID)
	
	i += 1



#a = open("itm", "wb")
#a.write(d)
#a.close()