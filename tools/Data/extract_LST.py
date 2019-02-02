#!/usr/bin/python3

import EraDra
from PIL import Image as pimg
import os
import sys

if len(sys.argv) != 2:
    print("Usage: " + sys.argv[0] + " FILENAME")
    print("Example: " + sys.argv[0] + " GPBMP")
    exit()

nm = sys.argv[1] #"GPBMP"

arc = EraDra.TLst( nm )

if not (os.path.isdir(nm)):
    os.mkdir(nm)

pix = bytearray(1024 * 1024 * 4)

jj = 0
for elm in arc.items:

    itm = arc.readItem(elm)


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
                    r = ((t >> 4) & 0xF) * 17
                    g = (t & 0xF) * 17

                    t = itm[inof]
                    b = ((t >> 4) & 0xF) * 17
                    aa = (t & 0xF) * 17

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
    img.save(nm + "/" + str(dr) + "/" + str(elm.ID) + ".png", format="PNG", compress_level=0)

    del img
    del itm
    
    jj += 1
	
    print("{:d}/{:d}".format(jj, len(arc.items)))



#a = open("itm", "wb")
#a.write(d)
#a.close()