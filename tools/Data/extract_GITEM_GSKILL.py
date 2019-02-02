#!/usr/bin/python3

import EraDra
import sys
import os
from PIL import Image as pimg



if len(sys.argv) != 2:
	print("Filename!")
	exit(-1)

fl = sys.argv[1]

arc = EraDra.TDra( fl )


dr = "extract_" + fl

if not (os.path.isdir(dr)):
    os.mkdir(dr)

pix = bytearray(1024 * 1024 * 4)

i = 0
for elm in arc.items:
	print ("{}/{}".format(i + 1, len(arc.items)) )

	itm = arc.readItem(elm)
	
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
	img.save(dr + "/" + str(elm.ID) + ".png", format="PNG", compress_level=0)

	del img
	del itm
	
	i += 1