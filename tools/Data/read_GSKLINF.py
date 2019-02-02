#!/usr/bin/python3

import EraDra
import os
import io


fl = "GSKLINF.DRA"

arc = EraDra.TEra(fl)

dr = "extract_" + fl

if not (os.path.isdir(dr)):
    os.mkdir(dr)

for elm in arc.items:

	itm = arc.readItem(elm)
	itmInf = io.BytesIO( itm )
	
	s = open(dr + "/" + str(elm.ID) +".raw", "wb")
	s.write(itm)
	s.close()
	
# 	
	title = ""
	descr = ""
	itmInf.seek(4)
	tp = itmInf.read(1)[0]
	
	of1 = int.from_bytes(itmInf.read(2), "little")
	of2 = int.from_bytes(itmInf.read(2), "little")
	
	itmInf.seek(of1)
	sz = itmInf.read(1)[0]
	if sz:
		title = itmInf.read(sz).decode("cp949")
	
	itmInf.seek(of2)
	sz = itmInf.read(1)[0]
	if sz:
		descr = itmInf.read(sz).decode("cp949")
	
	print(elm.ID)
	print("Type: " + hex(tp))
	print(title)
	print(descr)
	print()

