#!/usr/bin/python3

#### File with string identifiers from client
f = open("clientSTRids.txt","r")

dd = dict()

def hsh(b):
	v = 5381
	for a in b.encode("ascii"):
		v = (33 * v + a) & 0xFFFFFFFF
	return v

for l in f:
	l = l.strip()
	dd[hsh(l)] = l

f.close()

f = open("XenStrs.mdlr", "rb")
a = f.read()
f.close()

num = int.from_bytes(a[28:32], "little")
i = 0
while i < num:
	of = int.from_bytes(a[32:36], "little") + i * 4
	hz = int.from_bytes(a[of:of+4], "little")
	if hz in dd:
		of2 = int.from_bytes(a[36:40], "little") + i * 4
		of2 = int.from_bytes(a[of2:of2+4], "little")
		ln = a[of2]
		st = a[of2 + 1: of2 + 1 + ln].decode("ascii")
		print(dd[hz], "=", st)
		
		
	
	i += 1
	
