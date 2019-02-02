#!/usr/bin/python3

import EraDra
from PIL import Image as pimg
import os
import sys

class bdid:
	bodyID = 0
	bid = 0
	frameID = 0

def makeNPC_BodyList(eye, state):
	arc = EraDra.TEra( "GNBFC.XBD" )

	items = list()

	for elm in arc.items:
		if (elm.ID & 0xE0) == ((eye << 5) | (state & 0x1F)):
			itmInf = arc.readItem(elm)
			t = bdid()			
			t.bodyID = (elm.ID >> 8) & 0xFFFF
			t.bid = int.from_bytes(itmInf[:4], byteorder="little")
			
			items.append(t)

	return items


def makeFrameIDS(st, frame):
	arc = EraDra.TDra( "GNBID.DRA" )

	for elm in arc.items:
		for n in st:
			if elm.ID == n.bid:
				mm = arc.readItem(elm)
				
				if (frame < mm[0]):
					n.frameID = int.from_bytes(mm[1 + frame * 4 : 1 + frame * 4 + 4], byteorder="little")
				else:
					n.frameID = int.from_bytes(mm[1:5], byteorder="little")


nm = "GNBMP"

d = makeNPC_BodyList(6, 0)
makeFrameIDS(d, 0)

arc = EraDra.TLst( nm )

outDIR = "NPC_help"

jj = 0

if not (os.path.isdir(outDIR)):
    os.mkdir(outDIR)

num = len(d)

for elm in arc.items:
	skip = True
	
	i = None
	
	for n in d:
		if (n.frameID == elm.ID):
			skip = False
			i = n
			break
	
	if skip:
		continue
	
	d.remove(i)

	itm = arc.readItem(elm)

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
					r = ((t & 0xF0) >> 4) * 17
					g = (t & 0xF) * 17

					t = itm[8 + (pxid + (yy * pw + xx)) * 2]
					b = ((t & 0xF0) >> 4) * 17
					aa = (t & 0xF) * 17

					pix[(xpg << 8) + xx, (ypg << 8) + yy] = (r, g, b, aa)
					xx += 1
				yy += 1

			pxid += pw * ph

			ypg += 1

		xpg += 1

	img.save(outDIR + "/" + str(i.bodyID) + ".png")

	jj += 1

	print("{:d}/{:d}".format(jj, num))






