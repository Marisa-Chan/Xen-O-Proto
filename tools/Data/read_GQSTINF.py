#!/usr/bin/python3

import EraDra
import sys
import os
import io

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

StatTitle = {
	0x11: "POW",
	0x12: "INT",
	0x13: "STA",
	0x14: "AGI",
	0x15: "MEN",
	0x16: "WIS",
	0x17: "Max HP",
	0x18: "Max MP",
	0x19: "Max weight",
	0x1A: "HP recovery amount",
	0x1B: "MP recovery amount",
	0x21: "Attack",
	0x22: "Magic",
	0x23: "Def",
	0x24: "Magic Def",
	0x25: "Successful attack rate",
	0x26: "Successful dodge rate",
	0x27: "Crit",
	0x28: "Attack range",
	0x29: "Pre-defense rate",
	0x2E: "Attack_L",
	0x2F: "Attack_R",
	0x31: "Movement rate",
	0x32: "Delay attack",
	0x33: "Attack rate",
	0x34: "Magic interval",
	0x35: "Summoning time",
	0x36: "HP recovery time",
	0x37: "MP recovery time",
	0x39: "Skill crit",
	0x81: "HP",
	0x82: "MP",
	0x83: "HP&MP",
}

def getJOB(a):
	if a in JOBS:
		return JOBS[a]
	return "???"

def getStat(a):
	if a in StatTitle:
		return StatTitle[a]
	return "???"

def criter(a, b):
	if (a == 0):
		return "Kron >= {:d}".format(b)
	elif (a == 1):
		return "Kron <= {:d}".format(b)
	elif (a == 2):
		return "Item ({:d}) >= {:d}".format( (b & 0xFFFF), ((b >> 16) & 0xFFFF) )
	elif (a == 3):
		return "Item ({:d}) < {:d}".format( (b & 0xFFFF), ((b >> 16) & 0xFFFF) )
	elif (a == 4):
		return "Level >= {:d}".format(b)
	elif (a == 5):
		return "Level <= {:d}".format(b)
	elif (a == 6):
		return "JOB == {:s}({:d})".format(getJOB(b), b)
	elif (a == 7):
		return "JOB != {:s}({:d})".format(getJOB(b), b)
	elif (a == 8):
		return "Skill ({:d}) lvl >= {:d}".format( (b & 0xFFF), ((b >> 12) & 0xF) )
	elif (a == 9):
		return "Skill ({:d}) lvl < {:d}".format( (b & 0xFFF), ((b >> 12) & 0xF) )
	elif (a == 10):
		return "Stat {:s} >= {:d}".format(getStat(b & 0xFF), (b >> 16) & 0xFFFF)
	elif (a == 11):
		return "Stat {:s} <= {:d}".format(getStat(b & 0xFF), (b >> 16) & 0xFFFF)
	elif (a == 12):
		return "Has Quest? {:d}".format(b)
	elif (a == 13):
		return "Has NOT Quest? {:d}".format(b)
	elif (a == 14):
		return "Party size != 0"
	elif (a == 15):
		return "Party size == 0"
	elif (a == 16):
		return "Has Buff ({:d})".format( (b & 0xFFF) )
	elif (a == 17):
		return "Has NOT Buff ({:d})".format( (b & 0xFFF) )
	elif (a == 24):
		if (b != 0):
			return "Sex == Male"
		else:
			return "Sex == Female"
	elif (a == 25):
		if (b != 0):
			return "Sex != Male"
		else:
			return "Sex != Female"
	elif (a == 26):
		return "Equipped Item ({:d}) in Slot({:d})".format( (b >> 16) & 0xFFFF , (b & 0xFF))
	elif (a == 27):
		return "NOT Equipped Item ({:d}) in Slot({:d})".format( (b >> 16) & 0xFFFF , (b & 0xFF))
	elif (a == 37):
		return "ScriptMain result of script({:d}) != 0".format(b)
	elif (a == 38):
		return "Guild size? != 0"
	elif (a == 39):
		return "Guild size? == 0"
	return ""

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
	
	mm.seek(24)
	sz = mm.read(1)[0]
	if sz:
		req = "\tConditions: "
		reqoff = int.from_bytes(mm.read(2), byteorder = "little")
		mm.seek(reqoff)
		
		while(sz > 0):
			ra = mm.read(1)[0]
			rb = int.from_bytes(mm.read(4), byteorder = "little")
			crit = criter(ra, rb)
			
			if crit != "":
				req += crit
				if (sz > 1):
					req += ", "
			sz -= 1
			
		print(req)
		print()
	
	i += 1