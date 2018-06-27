#!/usr/bin/python3

import zlib

def decodeItem(data, off):
	decsz	= int.from_bytes(data[off  :off+4], "little")
	compsz	= int.from_bytes(data[off+4:off+8], "little")
	
	d = None
	
	if b[off+8] == 1:
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

a = open("GITMINF.DRA", "rb")
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
	
	if itemOff < off:
		itmInf = decodeItem(b, itemOff)
	
		###print detected item fields
	
		title = ""
		descr = ""
		price = int.from_bytes(itmInf[0xF:0xF + 4], "little")
	
		if itmInf[0x3D]:
			title = itmInf[0x3E : 0x3E + itmInf[0x3D] ].decode("cp949")
	
		descrOff = 0x3E + itmInf[0x3D]
		if itmInf[descrOff]:
			descr = itmInf[descrOff + 1 : descrOff + 1 + itmInf[descrOff] ].decode("cp949")
	
		print(itemID)
		print(title)
		print("SellPrice: ", price)	
		print(descr)
		print("")
	i += 8



#a = open("itm", "wb")
#a.write(d)
#a.close()