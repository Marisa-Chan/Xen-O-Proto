#!/usr/bin/python3

#### File with map IDs
#### One ID on line
#f = open("mapIDs.txt","r")

dd = dict()

def hsh(b):
	v = 5381
	for a in b.encode("ascii"):
		v = (33 * v + a) & 0xFFFFFFFF
	return v

i = 0

while i < 65535:
	dd[hsh(str(i))] = str(i)
	i+=1


f = open("GameSvrNpc.mdlr", "rb")
a = f.read()
f.close()

num = int.from_bytes(a[0x1C:0x20], "little")
i = 0
while i < num:
	of = int.from_bytes(a[0x20:0x24], "little") + i * 4
	hz = int.from_bytes(a[of:of+4], "little")
	if hz in dd:
		of2 = int.from_bytes(a[0x24:0x28], "little") + i * 4 #We use first LCID table
		of2 = int.from_bytes(a[of2:of2+4], "little")
		ln = a[of2]
		st = a[of2 + 1: of2 + 1 + ln].decode("cp1252")
		print(dd[hz], "=", st)
		
		
	
	i += 1
	
