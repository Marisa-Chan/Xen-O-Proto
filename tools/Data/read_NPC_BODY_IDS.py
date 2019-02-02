#!/usr/bin/python3

import zlib
import EraDra

arc = EraDra.TEra("GNBFC.XBD")

bt1 = set()

for elm in arc.items:
	#itmInf = arc.readItem(elm)
	
	bt1.add((elm.ID >> 8) & 0xFFFF)
	


print("\nNPC_body:")
for j in sorted(bt1):
	print(hex(j))

