#!/usr/bin/python3

import zlib
import sys
import os

def readItem(a):
	a.seek(4, 1)
	b = a.read(4)
	decsz	= int.from_bytes(b, "little")
	b = a.read(4)
	compsz	= int.from_bytes(b, "little")
	
	b = a.read(1)
	
	d = None
	
	if b[0] == 1:
		d = bytearray(zlib.decompress(a.read(compsz)) )
	else:
		d = bytearray(a.read(compsz))
	
	return d

if len(sys.argv) != 2:
	print("Filename!")
	exit(-1)

fl = sys.argv[1]

a = open(fl, "rb")

d = a.read(0x15)
num = int.from_bytes(d[0x10:0x14], byteorder='little')


dr = "extract_" + fl

if not (os.path.isdir(dr)):
    os.mkdir(dr)

i = 0
while i < num:
	a.seek(0x15 + i * 8)
	d = a.read(8)
	iid = int.from_bytes(d[0:4], byteorder='little')
	off = int.from_bytes(d[4:8], byteorder='little')
	
	a.seek(off)
	mm = readItem(a)
	
	s = open(dr + "/" + str(iid) + ".raw", "wb")
	s.write(mm)
	s.close()
	
	print(iid)	
	
	i += 1