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

if len(sys.argv) != 2:
    print("Usage: " + sys.argv[0] + " FILENAME")
    print("Example: " + sys.argv[0] + " GPBMP")
    exit()

nm = sys.argv[1] #"GPBMP"

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

valspd = bytearray(16)
while jj < 16:
    valspd[jj] = jj * 17
    jj += 1

jj = 0

if not (os.path.isdir(nm)):
    os.mkdir(nm)

pix = bytearray(1024 * 1024 * 4)

for i in itms:
    nd = mkName(nm, i.arr)
    if nd != prevname:
        if a != None:
            a.close()
        a = open(nd, "rb")
        prevname = nd

    a.seek(i.off)

    itm = readItem(a)


#     s = open(str(i.id), "wb")
#     s.write(itm)
#     s.close()

    w = itm[0] | (itm[1] << 8)
    h = itm[2] | (itm[3] << 8)

    

    xpages = (w + 0xFF) >> 8
    ypages = (h + 0xFF) >> 8

    pxid = 0

    xpg = 0
    while xpg < xpages:
        if xpg == xpages - 1:
            pw = w & 0xFF
        else:
            pw = 0x100

        ypg = 0
        while ypg < ypages:
            if ypg == ypages - 1:
                ph = h & 0xFF
            else:
                ph = 0x100
    
            yy = 0
            while yy < ph:
                xx = 0

                outof = ( ( h - ((ypg << 8) + yy) - 1 ) * w  +  (xpg << 8) ) * 4
                inof = 8 + (pxid + (yy * pw)) * 2
				
                while xx < pw:
    
                    t = itm[inof + 1]
                    r = valspd[(t >> 4) & 0xF]
                    g = valspd[(t & 0xF)]

                    t = itm[inof]
                    b = valspd[(t >> 4) & 0xF]
                    aa = valspd[(t & 0xF)]

                    pix[outof] = r
                    pix[outof + 1] = g
                    pix[outof + 2] = b
                    pix[outof + 3] = aa
					
                    outof += 4
                    inof += 2
					
                    xx += 1
                yy += 1
    
            pxid += pw * ph
    
            ypg += 1

        xpg += 1



    dr = jj // 2000

    if jj % 2000 == 0:
        if not (os.path.isdir(nm + "/" + str(dr))):
            os.mkdir(nm + "/" + str(dr))
	
    img = pimg.frombuffer('RGBA', (w,h), pix)	
    img.save(nm + "/" + str(dr) + "/" + str(i.id) + ".png", format="PNG", compress_level=0)

    del img
    del itm
    
    jj += 1
	
    print("{:d}/{:d}".format(jj - 1, numitems))



#a = open("itm", "wb")
#a.write(d)
#a.close()