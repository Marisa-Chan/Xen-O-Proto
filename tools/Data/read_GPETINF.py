#!/usr/bin/python3

import EraDra
import io

arc = EraDra.TEra ("GPETINF.DRA")

for elm in arc.items:
	itmInf = io.BytesIO( arc.readItem(elm) )

	bodyID = int.from_bytes(itmInf.read(2), byteorder = "little")
	
	nameOff = int.from_bytes(itmInf.read(2), byteorder = "little")
	
	itmInf.seek(8)
	flags = itmInf.read(1)[0]
	
	
	itmInf.seek(nameOff)
	namelen = itmInf.read(1)[0]
	name = ""
	if namelen:
		name = itmInf.read(namelen).decode("cp437")
	
	print("ID: ", elm.ID)
	print("Name: ", name)
	print("Flags: ", flags)
	print("BodyID: ", bodyID ) 
	print("")
