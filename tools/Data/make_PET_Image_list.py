#!/usr/bin/python3

import EraDra
from PIL import Image as pimg
import os
import sys
import io

class bdid:
	baseID = 0
	ID = 0


def LoadMobsInfo():
	arc = EraDra.TEra( "GPETINF.DRA" )

	items = list()

	for elm in arc.items:
		itmInf = arc.readItem(elm)
		t = bdid()
		t.ID = elm.ID
		t.baseID = int.from_bytes( itmInf[:2], byteorder="little" )
		
		items.append(t)
	
	return items

def LoadMobsBodyInfo():
	arc = EraDra.TEra( "GMBFC.XBD" )

	items = dict()

	for elm in arc.items:
		itmInf = arc.readItem(elm)
		
		items[elm.ID] = itmInf
	
	return items

def LoadMobsSeq():
	arc = EraDra.TDra( "GMBID.DRA" )

	items = dict()

	for elm in arc.items:
		itmInf = arc.readItem(elm)
		
		items[elm.ID] = itmInf
	
	return items

mobs = LoadMobsInfo()
mbody = LoadMobsBodyInfo()
mseq = LoadMobsSeq()

arc = EraDra.TLst( "GMBMP" )

mframes = dict()

for elm in arc.items:
	mframes[elm.ID] = elm

STATE = 5
EYE = 6
FRAME = 0

outDIR = "PET_help"

if not (os.path.isdir(outDIR)):
    os.mkdir(outDIR)

num = len(mobs)
ii = 0

for mob in mobs:
	ii += 1
	
	print( "{:d}/{:d}".format(ii, num) )
	
	bodyID = (STATE & 0x1F) | ((EYE & 7) << 5) | ((mob.baseID & 0xFFFF) << 8)
		
	if not bodyID in mbody:
		print("No body ID for mob:", mob.ID)
		continue
	
	seqID = int.from_bytes( mbody[bodyID][:4], byteorder="little")
	
	if not seqID in mseq:
		print("No Sequence for mob:", mob.ID)
		continue
	
	seq = mseq[seqID]
	
	frameID = int.from_bytes( seq[1:5], byteorder="little")
	
	if not frameID in mframes:
		print("No frame for mob:", mob.ID)
		continue
	
	
	itm = arc.readItem( mframes[frameID] )

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

	img.save(outDIR + "/" + str(mob.ID) + "_(" + str(mob.baseID) + ").png")
