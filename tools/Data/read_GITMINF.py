#!/usr/bin/python3

import EraDra
import io

ItemTypes = {
	0x00: "Other items",
	0x01: "Stat Jewelry",
	0x02: "Property Jewelry",
	0x03: "Arrow",
	0x04: "Skill book",
	0x10: "Consumable Item",
	0x20: "Costumes",
	0x30: "Helmet",
	0x40: "Gear for eyes",
	0x50: "Gear for face",
	0x60: "Gear for left-arm",
	0x61: "Shield",
	0x62: "Left-arm dagger",
	0x63: "Left-arm sword",
	0x70: "Gear for right-arm",
	0x71: "Dagger", 
	0x72: "One-handed sword",
	0x73: "Two hand sword",
	0x74: "Short arrow",
	0x75: "Long arrow",
	0x76: "One arm ax",
	0x77: "Two hand ax",
	0x78: "Wand",
	0x79: "Mace",
	0x80: "Backpack",
	0x90: "Gloves",
	0xA0: "Shoes",
	0xB0: "Accessory",
	0xB1: "Accessory",
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

SEX = {
	0: "F",
	1: "M"
	}

arc = EraDra.TEra ("GITMINF.DRA")

for elm in arc.items:
	itmInf = io.BytesIO( arc.readItem(elm) )

	###print detected item fields

	title = ""
	descr = ""

	itemIcon = int.from_bytes(itmInf.read(2), byteorder = "little")
	titleOff = int.from_bytes(itmInf.read(2), byteorder = "little")
	descrOff = int.from_bytes(itmInf.read(2), byteorder = "little")

	intweight = int.from_bytes(itmInf.read(2), byteorder = "little")
	fractweight = itmInf.read(1)[0]
	
	weight = intweight
	if (fractweight):
		weight += fractweight * 0.01
	
	itmInf.seek(0xA)
	itype = itmInf.read(1)[0]
	itypeStr = ""
	if (itype in ItemTypes):
		itypeStr = ItemTypes[itype]
	
	itmInf.seek(0xF)
	price = int.from_bytes(itmInf.read(4), byteorder = "little") 
	tradeInf = itmInf.read(1)[0] #0x13
	
	itmInf.seek(0x15)
	itemUseFlags = int.from_bytes(itmInf.read(2), byteorder = "little") 

	MntExcInfo = itmInf.read(1)[0] #0x17
	MntImgID = itmInf.read(1)[0] #0x18
	sex = itmInf.read(1)[0] #0x19
	lvl = itmInf.read(1)[0] #0x1A
	#itmInf.seek(0x1B)
	numJobs = itmInf.read(1)[0] #0x1B
	jobsOff = int.from_bytes(itmInf.read(2), byteorder = "little")
	
	itmInf.seek(0x1E)
	numStats = itmInf.read(1)[0]
	statsOff = int.from_bytes(itmInf.read(2), byteorder = "little") #0x1F
	
	smeltCount = itmInf.read(1)[0] #0x21
	smeltOff  = int.from_bytes(itmInf.read(2), byteorder = "little") #0x22
	
	skillcnt = itmInf.read(1)[0] #0x24
	skillOff = int.from_bytes(itmInf.read(2), byteorder = "little") #0x25

	
	itmInf.seek(0x2A)
	UseQuestID = int.from_bytes(itmInf.read(2), byteorder = "little") #0x2A
	
	
	itmInf.seek(0x39)
	grade = itmInf.read(1)[0]
	
	
	
	itmInf.seek(jobsOff)
	jobsStr = ""
	while numJobs > 0:
		jb = itmInf.read(1)[0]
		if (jb in JOBS):
			jobsStr += " {},".format(JOBS[jb])
		else:
			jobsStr += " {:02x},".format(jb)
		numJobs -= 1
		
	
	
	itmInf.seek(statsOff)
	statStr = ""
	while numStats > 0:
		sid = int.from_bytes(itmInf.read(2), byteorder = "little")
		sval = int.from_bytes(itmInf.read(4), byteorder = "little", signed = True)
		
		if (sid in StatTitle):
			statStr += StatTitle[sid]
		else:
			statStr += hex(sid)
		
		if (sid >= 0x32 and sid < 0x39):
			statStr += " {:.1f}S, ".format( (sval // 100) / 10.0 )
		else:
			statStr += " {:+d}, ".format(sval)
		
		numStats -= 1
	
	itmInf.seek(titleOff)
	sz = itmInf.read(1)[0]
	if sz:
		title = itmInf.read(sz).decode("cp437")

	itmInf.seek(descrOff)
	sz = itmInf.read(1)[0]
	
	if sz:
		descr = itmInf.read(sz).decode("cp437")
	
	if (smeltCount):
		i = smeltCount
		smltstr = ""
		itmInf.seek(smeltOff)
		while i > 0:
			a = int.from_bytes(itmInf.read(2), byteorder = "little")
			b = int.from_bytes(itmInf.read(2), byteorder = "little")
			c = int.from_bytes(itmInf.read(2), byteorder = "little")
			d = int.from_bytes(itmInf.read(2), byteorder = "little")
			smltstr += "( {}, {}, {}, {} ),".format(a,b,c,d)
			i -= 1
	
	if (skillcnt):
		i = skillcnt
		skillstr = ""
		itmInf.seek(skillOff)
		while i > 0:
			skillstr += " {},".format( int.from_bytes(itmInf.read(2), byteorder = "little") )
			i -= 1

	print(elm.ID)
	print(title)
	print("Weight: ", weight)
	print("Type: 0x{:02x} ({})".format(itype, itypeStr) ) 
	print("SellPrice: ", price, " Trade inf: ", tradeInf)	
	print("Stats: ", statStr)
	print("For jobs: ", jobsStr)
	if (lvl):
		print("Req level: ", lvl)
	if (sex in SEX):
		print("Sex: ", SEX[sex] )
	print ("Grade: ", grade)
	print ("MntExcInfo: ", MntExcInfo, "MntImgID: ", MntImgID)
	if (UseQuestID):
		print ("UseQuestID: ", UseQuestID)
	if (smeltCount):
		print ("Smelt: ", smltstr)
	if (skillcnt):
		print ("Skills: ", skillstr)
	print("IconID: ", itemIcon)
	print(repr(descr)[1:-1])
	print("")
