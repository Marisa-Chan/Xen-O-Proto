#!/usr/bin/python3

import zlib
from PIL import Image as pimg
import os
import sys

class bdid:
	bodyID = 0
	bid = 0
	frameID = 0
	off = 0
	arr = 0

def decodeItem(data, off):
	decsz	= int.from_bytes(data[off  :off+4], "little")
	compsz	= int.from_bytes(data[off+4:off+8], "little")
	
	d = None
	
	if data[off+8] == 1:
		d = bytearray(zlib.decompress(data[off+9 : off+9+compsz]))
	else:
		d = bytearray(data[off+9 : off+9+decsz])
	
	if data[0x1e]:
		shift = data[0x1e] % 7 + 1
		i = 0
		while (i + 4) <= len(d):
			e = int.from_bytes(d[i: i + 4], "little")
			e = e >> shift | ((e << (32-shift)) & 0xFFFFFFFF)
			d[i] = e & 0xFF
			d[i + 1] = (e >> 8) & 0xFF
			d[i + 2] = (e >> 16) & 0xFF
			d[i + 3] = (e >> 24) & 0xFF
			i += 4
	
		while i < len(d):
			e = d[i]
			e = e >> shift | ((e << (8-shift)) & 0xFF)
			d[i] = e & 0xFF
			i += 1
	
	return d

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

def makeNPC_BodyList(eye, state):
	a = open("GNBFC.XBD", "rb")
	b = a.read()
	a.close()

	off = int.from_bytes(b[0x18:0x1C], "little")
	sz = int.from_bytes(b[0x14:0x18], "little")

	dec = zlib.decompressobj()

	c = None

	if (b[0x1C] == 1):
		c = dec.decompress(b[off:], sz * 8)
	else:
		c = b[off:off + sz * 8]

	items = list()

	i = 0
	while i < len(c):
		itemID  = int.from_bytes(c[i  :i+4], "little")
		itemOff = int.from_bytes(c[i+4:i+8], "little")
	
		if (itemID & 0xE0) == ((eye << 5) | (state & 0x1F)):
			itmInf = decodeItem(b, itemOff)
			t = bdid()			
			t.bodyID = (itemID >> 8) & 0xFFFF
			t.bid = int.from_bytes(itmInf[:4], "little")
			
			items.append(t)

		i += 8

	return items


def makeFrameIDS(st, frame):
	a = open("GNBID.DRA","rb")

	d = a.read(0x15)
	num = int.from_bytes(d[0x10:0x14], byteorder='little')

	i = 0
	while i < num:
		a.seek(0x15 + i * 8)
		d = a.read(8)
		iid = int.from_bytes(d[0:4], byteorder='little')
		off = int.from_bytes(d[4:8], byteorder='little')
	
		for n in st:
			if iid == n.bid:
				a.seek(off)
				mm = readItem(a)
				
				if (frame < mm[0]):
					n.frameID = int.from_bytes(mm[1 + frame * 4 : 1 + frame * 4 + 4], "little")
				else:
					n.frameID = int.from_bytes(mm[1:5], "little")
	
		i += 1
	
	a.close()


def mkName(z, id):
    if (id):
        return "{:s}.{:03x}".format(z, id)
    else:
        return nm + ".DRA"

def findNeededArr(st, nm):
	
	a = open(nm + ".LST", "rb")
	a.seek(0x10,0)
	numitems = int.from_bytes( a.read(4) , "little" )

	a.seek(2, 1)

	i = 0
	while i < numitems:
		id  = int.from_bytes( a.read(4) , "little" )
		off = int.from_bytes( a.read(4) , "little" )
		arr = a.read(1)[0]
	
		for n in st:
			if (n.frameID == id):
				n.off = off
				n.arr = arr
	
		i += 1

	a.close()


nm = "GNBMP"

d = makeNPC_BodyList(6, 0)
makeFrameIDS(d, 0)
findNeededArr(d, nm)

outDIR = "NPC_help"
prevname=""
a = None

jj = 0

if not (os.path.isdir(outDIR)):
    os.mkdir(outDIR)

for i in d:
    nd = mkName(nm, i.arr)
    if nd != prevname:
        if a != None:
            a.close()
        a = open(nd, "rb")
        prevname = nd

    a.seek(i.off)

    itm = readItem(a)
#    if (i.bodyID == 62306):
#        s = open(str(i.bodyID), "wb")
#        s.write(itm)
#        s.close()

    w = itm[0] | (itm[1] << 8)
    h = itm[2] | (itm[3] << 8)

    img = pimg.new('RGBA', (w,h))
    pix = img.load()

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
                while xx < pw:
    
                    t = itm[8 + (pxid + (yy * pw + xx)) * 2 + 1]
                    r = t & 0xF0
                    g = (t << 4) & 0xF0

                    t = itm[8 + (pxid + (yy * pw + xx)) * 2]
                    b = t & 0xF0
                    aa = (t << 4) & 0xF0

                    pix[(xpg << 8) + xx, (ypg << 8) + yy] = (r, g, b, aa)
                    xx += 1
                yy += 1
    
            pxid += pw * ph
    
            ypg += 1

        xpg += 1

    img.save(outDIR + "/" + str(i.bodyID) + ".png")
    
    jj += 1
	
    print("{:d}/{:d}".format(jj - 1, len(d)))






