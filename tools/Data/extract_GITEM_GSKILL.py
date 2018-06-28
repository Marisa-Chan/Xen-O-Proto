#!/usr/bin/python3

import zlib
import sys
import os
from PIL import Image as pimg

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

pix = bytearray(1024 * 1024 * 4)

i = 0
while i < num:
	a.seek(0x15 + i * 8)
	d = a.read(8)
	iid = int.from_bytes(d[0:4], byteorder='little')
	off = int.from_bytes(d[4:8], byteorder='little')
	
	a.seek(off)
	itm = readItem(a)
	
	w = itm[0] | (itm[1] << 8)
	h = itm[2] | (itm[3] << 8)
	#tp = itm[4]
	
	btoff = 8
	outoff = 0
	
	yy = 0
	while yy < h:
		xx = 0
		outoff = (h - yy - 1) * w * 4
		while xx < w:

			ca = (itm[btoff] & 0xF) * 17
			cb = ((itm[btoff] >> 4) & 0xF) * 17
			cg = (itm[btoff + 1] & 0xF) * 17
			cr = ((itm[btoff + 1] >> 4) & 0xF) * 17
			btoff += 2

			pix[outoff] = cr
			pix[outoff + 1] = cg
			pix[outoff + 2] = cb
			pix[outoff + 3] = ca
			outoff += 4
		
			xx += 1
		yy += 1

	img = pimg.frombuffer('RGBA', (w,h), pix)	
	img.save(dr + "/" + str(iid) + ".png", format="PNG", compress_level=0)

	del img
	del itm

	print(iid)	
	
	i += 1