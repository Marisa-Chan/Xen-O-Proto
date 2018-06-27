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

bt1 = set()

i = 0
while i < len(c):
	itemID  = int.from_bytes(c[i  :i+4], "little")
	itemOff = int.from_bytes(c[i+4:i+8], "little")
	
	itmInf = decodeItem(b, itemOff)
	
	bt1.add((itemID >> 8) & 0xFFFF)
	
	###print detected item fields
	
	#print(hex(itemID))
	i += 8

print("\nNPC_body:")
for j in sorted(bt1):
	print(hex(j))

#a = open("itm", "wb")
#a.write(d)
#a.close()