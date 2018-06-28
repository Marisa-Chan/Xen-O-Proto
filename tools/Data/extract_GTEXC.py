#!/usr/bin/python3

import zlib
from PIL import Image as pimg
import os
import sys

class lst:
	id = 0
	off = 0
	arr = 0

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

def mkName(z, id):
    if (id):
        return "{:s}.{:03x}".format(z, id)
    else:
        return nm + ".DRA"

nm = "GTEXC"

itms = list()

a = open(nm + ".LST", "rb")
a.seek(0x10,0)
numitems = int.from_bytes( a.read(4) , "little" )

a.seek(2, 1)

i = 0
while i < numitems:
	k = lst()
	k.id  = int.from_bytes( a.read(4) , "little" )
	k.off = int.from_bytes( a.read(4) , "little" )
	k.arr = a.read(1)[0]
	itms.append(k)
	i += 1

a.close()

prevname=""
a = None

jj = 0

if not (os.path.isdir(nm)):
    os.mkdir(nm)

for i in itms:
    nd = mkName(nm, i.arr)
    if nd != prevname:
        if a != None:
            a.close()
        a = open(nd, "rb")
        prevname = nd

    a.seek(i.off)

    itm = readItem(a)


    w = itm[0] | (itm[1] << 8)
    h = itm[2] | (itm[3] << 8)
    tp = itm[4]

    img = pimg.new('RGBA', (w,h))
    pix = img.load()

    xpages = (w + 0xFF) >> 8
    ypages = (h + 0xFF) >> 8

    pxid = 0
    btoff = 8

    yy = 0
    while yy < h:
        xx = 0
        while xx < w:

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
                    #print("Tp " + str(tp))
                    cr = 0
                    cg = 0
                    cb = 0
                    ca = 0
                    pass

            pix[xx, yy] = (cr, cg, cb, ca)
            xx += 1
        yy += 1

    dr = jj // 2000

    if jj % 2000 == 0:
        if not (os.path.isdir(nm + "/" + str(dr))):
            os.mkdir(nm + "/" + str(dr))
	
    if tp != 3 and tp != 4:
        img.save(nm + "/" + str(dr) + "/" + str(i.id) + ".png")
    
    jj += 1
	
    print("{:d}/{:d}".format(jj - 1, numitems))



#a = open("itm", "wb")
#a.write(d)
#a.close()