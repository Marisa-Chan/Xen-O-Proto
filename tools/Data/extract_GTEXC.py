#!/usr/bin/python3

import EraDra
from PIL import Image as pimg
import os
import sys


nm = "extract_GTEXC"

arc = EraDra.TLst( "GTEXC" )

if not (os.path.isdir(nm)):
    os.mkdir(nm)

jj = 0
for elm in arc.items:

    itm = arc.readItem(elm)

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
        img.save(nm + "/" + str(dr) + "/" + str(elm.ID) + ".png")
    
    jj += 1
	
    print( "{:d}/{:d}".format(jj, len(arc.items) ) )



#a = open("itm", "wb")
#a.write(d)
#a.close()