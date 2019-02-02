#!/usr/bin/python3

import EraDra
import sys
import os
import io

fl = "GQSTINF.DRA"

arc = EraDra.TEra(fl)

dr = "extract_" + fl

if not (os.path.isdir(dr)):
    os.mkdir(dr)

i = 0
for elm in arc.items:
	bytes = arc.readItem(elm)
	mm = io.BytesIO( bytes )

	s = open(dr + "/" + str(elm.ID) + ".raw", "wb")
	s.write(bytes)
	s.close()

	mm.seek(0x2A)
	title = ""
	sz = mm.read(1)[0]
	if sz:
		title = mm.read(sz).decode("cp949")

	print(str(elm.ID) + " = " +  title)
	
	i += 1