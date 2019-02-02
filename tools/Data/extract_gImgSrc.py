#!/usr/bin/python3

import EraDra
from PIL import Image as pimg
import sys
import os


def szpow2(sz):
	tmp = 1;
	if sz >= 1024:
		return 512
	
	while tmp < sz:
		tmp <<= 1
	
	if tmp != sz:
		return tmp >> 1
	return tmp
	
if len(sys.argv) != 2:
    print("Usage: " + sys.argv[0] + " gImgSrc.era")
    exit()
    
fl = sys.argv[1]

arc = EraDra.TEra( fl, False)

dr = "gImgSrc"

if not (os.path.isdir(dr)):
    os.mkdir(dr)

i = 0
for elm in arc.items:
	print ("{}/{}".format(i + 1, len(arc.items)) )

	itm = arc.readItem(elm)
	
	
	w = itm[4] | (itm[5] << 8)
	h = itm[6] | (itm[7] << 8)
	parts = itm[2] | (itm[3] << 8)
	tp = itm[0] | (itm[1] << 8)
	
	img = pimg.new('RGBA', (w,h))
	pix = img.load()
	
	wrkw = w
	wrkh = h
	partN = 0
	btoff = 8
	
	xx = 0
	yy = 0
	
	while wrkw > 0:
		pw = szpow2(wrkw)
		
		while wrkh > 0:
			ph = szpow2(wrkh)
			
			ty = 0
			while ty < ph:
				tx = 0
				while tx < pw:
					
					if tp == 7:
						cb = itm[btoff]
						cg = itm[btoff + 1]
						cr = itm[btoff + 2]
						ca = itm[btoff + 3]
						btoff += 4
					elif tp == 0:
						ca = (itm[btoff] & 0xF) * 17
						cb = ((itm[btoff] >> 4) & 0xF) * 17
						cg = (itm[btoff + 1] & 0xF) * 17
						cr = ((itm[btoff + 1] >> 4) & 0xF) * 17
						btoff += 2
					elif tp == 1:
						clr = int.from_bytes(itm[btoff : btoff + 2], "little")
						ca = (clr & 1) * 0xFF
						cb = int(((clr >> 1) & 0x1F) * 8.23)
						cg = int(((clr >> 6) & 0x1F) * 8.23)
						cr = int(((clr >> 11) & 0x1F) * 8.23)
						btoff += 2
					elif tp == 2:
						cr = itm[btoff]
						cg = itm[btoff + 1]
						cb = itm[btoff + 2]
						ca = itm[btoff + 3]
						btoff += 4
					elif tp == 5:
						cb = (itm[btoff] & 0xF) * 17
						cg = ((itm[btoff] >> 4) & 0xF) * 17
						cr = (itm[btoff + 1] & 0xF) * 17
						ca = ((itm[btoff + 1] >> 4) & 0xF) * 17
						btoff += 2
					else:
						print("Tp " + str(tp))
						cr = 0
						cg = 0
						cb = 0
						ca = 0
						pass
										
					pix[ xx + tx, yy + ty] = (cr, cg, cb, ca)
					
					tx += 1
					
				ty += 1
			
			partN += 1
			
			if partN >= parts:
				break
			
			yy += ph
			wrkh -= ph
		
		if partN >= parts:
			break
		
		xx += pw
		wrkw -= pw
		yy = 0
		wrkh = h
	
	img.save(dr + "/" + str(elm.ID) + ".png")
		
	
	###print detected item fields
	
	#print(elm.ID)
	i += 1

#a = open("itm", "wb")
#a.write(d)
#a.close()