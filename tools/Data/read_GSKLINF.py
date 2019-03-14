#!/usr/bin/python3

import EraDra
import os
import io
import struct


JOBS = {
	0: "Xenian",
	1: "Squire",
	2: "Apprentice",
	3: "Neophyte",
	4: "Acolyte",
	5: "Knight",
	6: "Mage",
	7: "Archer",
	8: "Templar",
	9: "Warrior",
	10: "Wizard",
	11: "Assassin",
	12: "Priest",
	13: "Warlord",
	14: "Archmage",
	15: "Shadow Master",
	16: "Paladin",
	17: "Rogue",
	18: "Cleric",
	19: "Scout",
	20: "Disciple",
	21: "Ranger",
	22: "Holy Avenger",
	23: "Archer Lord",
	24: "Saint Guardian",
}


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
	tp = itmInf.read(1)[0] #4
	
	of1 = int.from_bytes(itmInf.read(2), "little") #5
	of2 = int.from_bytes(itmInf.read(2), "little") #7
	
	itmInf.seek(0xA)
	jobs_cnt = itmInf.read(1)[0] #0x0A
	jobs_off = int.from_bytes(itmInf.read(2), "little") #0x0B
	
	
	itmInf.seek(of1)
	sz = itmInf.read(1)[0]
	if sz:
		title = itmInf.read(sz).decode("cp949")
	
	itmInf.seek(of2)
	sz = itmInf.read(1)[0]
	if sz:
		descr = itmInf.read(sz).decode("cp949")
	
	if jobs_cnt:
		itmInf.seek(jobs_off)
		jobs_str = ""
		while itmInf.tell() < jobs_off + jobs_cnt:
			jb = itmInf.read(1)[0]
			if (jb in JOBS):
				jobs_str += " {},".format( JOBS[jb] )
			else:
				jobs_str += " 0x{:02x},".format( jb )
	
	
	
	C1EffectID = None
	
	if tp >= 0x12:
		itmInf.seek(0x18 + 0xA)
		bz = int.from_bytes( itmInf.read(2), byteorder = "little")
		if bz:
			C1EffectID = str( bz )
			
			
	
	C0EffectID = None
	C0Prep = None
	
	if tp >= 0x12:
		itmInf.seek(0x1A)
		bz = int.from_bytes( itmInf.read(2), byteorder = "little")
		if bz:
			C0EffectID = str( bz )
		
		itmInf.seek(0x18 + 0x24)
		
		bz = itmInf.read(1)[0]
		if ((bz & 4) != 4):
			itmInf.seek(0x18 + 0x31)
			f1 = struct.unpack('<f', itmInf.read(4))[0]
			f2 = struct.unpack('<f', itmInf.read(4))[0]
			f3 = struct.unpack('<f', itmInf.read(4))[0]
			if ( f1 > 0.0 or f2 > 0.0 or f3 > 0.0):
				C0Prep = "(SkillLVL * {:0.3f} + 1.0) * {:0.3f} + {:0.3f} + BE.word4B".format(f2, f1, f3)
	
	
	
	C2EffectID = None
	
	if tp >= 0x12:
		itmInf.seek(0x1E)
		bz = int.from_bytes( itmInf.read(2), byteorder = "little")
		if bz:
			C2EffectID = str( bz )
	
	TP31Eff = None
	itmInf.seek(0x18 + 0x12)
	bz = int.from_bytes( itmInf.read(2), byteorder = "little")
	if bz:
		TP31Eff = str( bz )
	
	
	EFEff = None
	itmInf.seek(0x18 + 0x0E)
	bz = int.from_bytes( itmInf.read(2), byteorder = "little")
	if bz:
		EFEff = str( bz )
	
	
	print(elm.ID)
	print("Type: " + hex(tp))
	print(title)
	if jobs_cnt:
		print("Jobs: ", jobs_str)
	if C0EffectID:
		print("C0 Effect ID: " + C0EffectID)
	if C0Prep:
		print("C0 Prep time: " + C0Prep)
	if C1EffectID:
		print("C1 Effect ID: " + C1EffectID)
	
	if C2EffectID:
		print("C2 Effect ID: " + C2EffectID)
	
	if TP31Eff:
		print("C3 Event Effect ID: " + TP31Eff)
	
	if EFEff:
		print("C3 Effect ID: " + EFEff)
		
	print(descr)
	print()

