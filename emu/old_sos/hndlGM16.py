#!/usr/bin/python3
import socket
import time
import threading
import binascii
import DNCPacket
import config


def ItemSlot(ID, CNT):
	bts = bytearray()
	bts += (ID).to_bytes(2, byteorder = "little")
	bts += (CNT).to_bytes(2, byteorder = "little")
	bts += (0).to_bytes(4, byteorder = "little")
	return bts

def CreateNpc():
	p = DNCPacket.Packet()
	p.tp = 0xB1

	#++0x0
	p.data.append(3)                       # SubType

	p.data.append(0)                       # 0 - quite create, 1 - create with sound and splash effect
	p.data += (201).to_bytes(2, byteorder = "little") # Map object ID
	p.data += (61456).to_bytes(2, byteorder = "little") # body id

	p.data.append(1)
	p.data.append(1)

	p.data.append(5) # direction
	p.data.append(1) # script type

	p.data += (12).to_bytes(2, byteorder = "little")  #script id interact

	p.data += (60).to_bytes(2, byteorder = "little")  #X coord
	p.data += (60).to_bytes(2, byteorder = "little")  #Y coord
	name = "Test NPC"
	p.data.append( len(name) )
	p.data += name.encode("UTF-8")

	return p

def CreateCharacter(ID, NAME, X, Y, admin, guild):
	UNKSTR=""
	p = DNCPacket.Packet()
	p.tp = 0xB1
	
	#++0x0
	p.data.append(1)                       # SubType 1 - create player
	
	p.data.append(0)                       # 0 - quite create, 1 - create with sound and splash effect
	p.data += ID.to_bytes(2, byteorder = "little") # Map object ID
				
	#++0x4
	p.data += bytes(10)                    # Charview bytes
				
	#++0xE (14)
	p.data.append(0)                       #Walk mask 
	p.data.append(50)                      #WalkSpeed    0-59
	p.data.append(2)                       #Character direction
	p.data.append(0)                       #state?
	
	if admin:
		p.data.append(250)
	else:
		p.data.append(0)                       #Acc level or iconID or what? (240+ - has "GM" mark)
	
	#++0x13 (19)
	p.data += X.to_bytes(2, byteorder = "little")  #X coord
	p.data += Y.to_bytes(2, byteorder = "little")  #Y coord
	
	#++0x17 (23)
	p.data += (guild).to_bytes(4, byteorder = "little")  #???Guild ID??
	p.data.append(0xCC)                                 #???Something belongs to Guild. May be emblem sequental ID of this guild???    if 0xFF - not in guild or no emblem?, because does not send request for emblem
	
	p.data.append(1)                                 #???
	p.data.append(1)                                 #???
	p.data.append(1)                                 #???
	
	#++0x1F (31)
	p.data.append(1)                                 #???
	p.data += (1).to_bytes(2, byteorder = "little")  #???
	
	p.data.append( len(NAME) )
	p.data.append( len(UNKSTR) ) ## Guild ??
	
	p.data += NAME.encode("UTF-8")
	p.data += UNKSTR.encode("UTF-8")
										
	return p


def CreateCharacter2(ID, NAME, X, Y, admin, guild):
	p = DNCPacket.Packet()
	p.tp = 0xB1
	
	#++0x0
	p.data.append(1)                       # SubType 1 - create player
	
	p.data.append(0)                       # 0 - quite create, 1 - create with sound and splash effect
	p.data += ID.to_bytes(2, byteorder = "little") # Map object ID
				
	#++0x4
	p.data += bytes(10)                    # Charview bytes
				
	#++0xE (14)
	p.data.append(0)                       #Walk mask 
	p.data.append(50)                      #WalkSpeed    0-59
	p.data.append(2)                       #Character direction
	p.data.append(0)                       #state?
	
	# (18)
	if admin:
		p.data.append(250)
	else:
		p.data.append(0)                       #Acc level or iconID or what? (240+ - has "GM" mark)
	
	#++0x13 (19)
	p.data += X.to_bytes(2, byteorder = "little")  #X coord
	p.data += Y.to_bytes(2, byteorder = "little")  #Y coord
	
	#++0x17 (23)
	p.data += (guild).to_bytes(4, byteorder = "little")  #???Guild ID??
	p.data.append(0xCC)                                 #???Something belongs to Guild. May be emblem sequental ID of this guild???    if 0xFF - not in guild or no emblem?, because does not send request for emblem
	
	# (28)
	p.data.append(1)                                 #???
	p.data.append(1)                                 #???
	
	p.data.append(1)                                 #???
	
	#++0x1F (31)
	p.data.append(3)                                 #???
	p.data += (41393).to_bytes(2, byteorder = "little")  #???
	
	# (34)
	p.data.append( len(NAME) )
	p.data.append( 0 ) ## Vis bytes
	
	p.data += NAME.encode("UTF-8")
										
	return p

def Handle(pin):
	retList = list()
	
	if (pin.tp == 0xBF):
		print("Recvd BF : " + pin.data.hex())
		
		#New!
		p = DNCPacket.Packet()
		p.tp = 0xBF

		p.data.append(1)               #player object scope (1,2,3). 1 - player type, 2 - monster type, 3 - npc type
		p.data += bytes([1, 1])        #player object ID (for example 0x101 == 257)
		p.data += bytes([2, 0, 0, 0] ) #some timestamp
		
		retList.append(p)
				
		
		#Load map
		p = DNCPacket.Packet()
		p.tp = 0xB0

		p.data.append(0x11)
		p.data += bytes([84, 0, 0, 0]) #MAPID
		p.data += bytes([100, 0]) #POSX
		p.data += bytes([100, 0]) #POSY

		retList.append(p)
		
		
		#Show 
		p = DNCPacket.Packet()
		p.tp = 0xB0

		p.data.append(0x13)
		
		retList.append(p)
		
		
		#Set player info
		p = DNCPacket.Packet()
		p.tp = 0xC0

		p.data.append(0x0)
	
		p.data += bytes([10, 0, 1, 0]) #Kron
		p.data += bytes([0, 0, 0, 0])
		p.data.append(0x2B) #???
		p.data.append(0x1) #JOB
		p.data.append(0x0) #Hair
		p.data += bytes([0, 1]) #HP
		p.data += bytes([0, 1]) #MP
		p.data.append(250) #Level
		p.data += bytes([17, 17, 17, 17])
		p.data += bytes([240, ]) #POW
		p.data += bytes([239, ]) #STA
		p.data += bytes([238, ]) #AGI
		p.data += bytes([237, ]) #INT
		p.data += bytes([236, ]) #MEN
		p.data += bytes([235, ]) #WIS
		p.data += bytes([0, 0])
		
		p.data += bytes(0x92)
		
		retList.append(p)




		#Create player char
		p = CreateCharacter(257, "YourChar", 100, 100, True, 12345)
		
		retList.append(p)


		#Create player char
		p = CreateCharacter(256, "AAAAAA", 105, 100, False, 0)
		
		retList.append(p)
		
		
		#Create player char
		p = CreateCharacter(255, "AAAAZZ", 107, 102, False, 0)
		
		retList.append(p)
		
		
		#p = DNCPacket.Packet()
		#p.tp = 0xB5
		
		#p.data.append(0x1A)
		#p.data.append(1)
		#p.data += (256).to_bytes(2, byteorder = "little")
		
		#retList.append(p)
		
		
		
		p = CreateNpc()
		retList.append(p)
		
		
		
		
		p = DNCPacket.Packet()
		p.tp = 0xC0
		
		p.data.append(0x33)
		p.data.append(1)
		p.data += bytearray((0xF3,0x0C, 10, 00, 00, 00, 00 ,00))
		
		retList.append(p)
		
		
		
		p = DNCPacket.Packet()
		p.tp = 0xC0
		
		p.data.append(0x32)
		p.data.append(1)
		p.data += bytearray((0x1F,0x71, 0 , 00, 00, 00, 00 ,00))
		
		retList.append(p)

		print("OK")
	elif (pin.tp == 0xB0):
		print("Packet 0xB0: Want disconnect")


		#hide 
		p = DNCPacket.Packet()
		p.tp = 0xB0

		p.data.append(0x12)  
		
		retList.append(p)
		
		
		p = DNCPacket.Packet()
		p.tp = 3

		p.data += (0).to_bytes(2, byteorder = "little")
		p.wait = time.time() + 1 #we must wait because fadeout window will be rerun with this
		retList.append(p)
		
		
	elif (pin.tp == 0xBA):
		print("Packet 0xBA:")
		if (pin.data[0] == 0x11):
			print("\t Normal msg len({}) : {}".format( str(pin.data[1]), pin.data[2:].decode("utf-8") ) )
			p = DNCPacket.Packet()
			p.tp = 0xBA
			
			p.data.append(0x11)
			p.data.append(1) # scope
			p.data += (256).to_bytes(2, byteorder = "little") # obj ID  256 - for another character
			
			mmmmsg = "Msg len({}) : {}".format( str(pin.data[1]), pin.data[2:].decode("utf-8") )
			
			p.data.append( len(mmmmsg) ) #msg len
			p.data += mmmmsg.encode("utf-8") #msg
			
			retList.append(p)
			
			stt = pin.data[2:].decode("utf-8")
			if stt == "1":
											
				p = DNCPacket.Packet()
				p.tp = 0xC2

				p.data.append(0x11)
				
				p.data.append(1)
				p.data.append(3)
				p.data.append(0)
				
				
				p.data += (84).to_bytes(2, byteorder = "little")
				p.data.append(6)
				p.data += "AAAADD".encode("ascii")
				p.data += (84).to_bytes(2, byteorder = "little")
				p.data.append(8)
				p.data += "YourChar".encode("ascii")
				p.data += (0).to_bytes(2, byteorder = "little")
				p.data.append(4)
				p.data += "LOFH".encode("ascii")

				print("Send C2 " + p.data.hex())
				retList.append(p)
			elif stt == "2":
											
				p = DNCPacket.Packet()
				p.tp = 0xC2

				p.data.append(0x12)
				
				p.data.append(6)
				p.data += "AAAAAA".encode("ascii")

				print("Send C2 " + p.data.hex())
				retList.append(p)
			elif stt == "3":
				p = DNCPacket.Packet()
				p.tp = 0xC2

				p.data.append(0x17)
				
				p.data.append(1)
				p.data += (84).to_bytes(2, byteorder = "little")

				print("Send C2 " + p.data.hex())
				retList.append(p)
			elif stt == "4":
				p = DNCPacket.Packet()
				p.tp = 0xC2

				p.data.append(0x18)
				
				p.data.append(8)
				p.data += "YourChar".encode("ascii")

				print("Send C2 " + p.data.hex())
				retList.append(p)
			elif stt == "5":
				p = DNCPacket.Packet()
				p.tp = 0xC2

				p.data.append(0x19)
				
				print("Send C2 " + p.data.hex())
				retList.append(p)
			elif stt == "6":
				p = DNCPacket.Packet()
				p.tp = 0xC2

				p.data.append(0x16)
				p.data.append(0)
				p.data.append(10)
				
				print("Send C2 " + p.data.hex())
				retList.append(p)
			elif stt == "7":
				p = DNCPacket.Packet()
				p.tp = 0xC0
				
				p.data.append(2)
				p.data.append(0)
				
				print("Send C0 " + p.data.hex())
				retList.append(p)
			elif stt == "10":
				# spin roulette
				p = DNCPacket.Packet()
				p.tp = 0xC0

				p.data.append(0xA7)
				p.data.append(1) # 1 or 2 same result
				p.data.append(1)
				p.data.append(1)
				p.data.append(1)
				retList.append(p)

				# normaly I have a 3 second timer after this one to apply the buff when the roulette stops spinning

				# set buff
				p = DNCPacket.Packet()
				p.tp = 0xC0

				p.data.append(0x41) # also tried 0x44
				p.data += (6534).to_bytes(2, byteorder = "little") # super rampage buff 2438 lvl 1
				#p.data += (600000).to_bytes(4, byteorder = "little") # buff time
				retList.append(p)

				# execute roulette script
				p = DNCPacket.Packet()
				p.tp = 0xB0

				p.data.append(0x30)
				p.data.append(1)
				p.data += (7777).to_bytes(2, byteorder = "little")
				retList.append(p)
			elif stt == "trade":
				p = DNCPacket.Packet()
				p.tp = 0xC1
				
				p.data.append(0x23)
				p.data += (222555).to_bytes(4, byteorder="little")
				p.data.append(4)
				p.data += ItemSlot(1120, 0)
				p.data += ItemSlot(14273, 0)
				p.data += ItemSlot(10151, 0)
				p.data += ItemSlot(4, 4)
				
				print("Send C1 " + p.data.hex())
				retList.append(p)
			elif stt == "trade2":
				p = DNCPacket.Packet()
				p.tp = 0xC1
				
				p.data.append(0x24)
				
				print("Send C1 " + p.data.hex())
				retList.append(p)
			elif stt == "trade22":
				p = DNCPacket.Packet()
				p.tp = 0xC1
				
				p.data.append(0x22)
				
				print("Send C1 " + p.data.hex())
				retList.append(p)
			elif stt == "trade25":
				p = DNCPacket.Packet()
				p.tp = 0xC1
				
				p.data.append(0x25)
				
				print("Send C1 " + p.data.hex())
				retList.append(p)
			elif stt == "trade11":
				p = DNCPacket.Packet()
				p.tp = 0xC1
				
				p.data.append(0x11)				
				
				print("Send C1 " + p.data.hex())
				retList.append(p)
			elif stt == "trade12":
				p = DNCPacket.Packet()
				p.tp = 0xC1
				
				p.data.append(0x12)
				p.data.append(1)
				p.data += bytearray((0xF3,0x0C, 2, 00, 00, 00, 00 ,00,     8, 00, 00, 00))
				
				print("Send C1 " + p.data.hex())
				retList.append(p)
			elif stt == "trade13":
				p = DNCPacket.Packet()
				p.tp = 0xC1
				
				p.data.append(0x13)
				p.data.append(2)
				p.data += ItemSlot(1120, 1)
				p.data += (22).to_bytes(4, byteorder="little")
				p.data += ItemSlot(4, 5)
				p.data += (33).to_bytes(4, byteorder="little")
				
				
				print("Send C1 " + p.data.hex())
				retList.append(p)
			elif stt == "trade15":
				p = DNCPacket.Packet()
				p.tp = 0xC1
				
				p.data.append(0x15)
				p.data += (256).to_bytes(2, byteorder="little")
				p.data.append(6)
				p.data += "Jopppa".encode("ascii")
				
				
				print("Send C1 " + p.data.hex())
				retList.append(p)
			elif stt == "tradecc":
				p = DNCPacket.Packet()
				p.tp = 0xB1
				
				p.data.append(5)
				p.data.append(0)
				p.data += (0xDCAC).to_bytes(2, byteorder="little")
				p.data += (95).to_bytes(2, byteorder="little")
				p.data += (90).to_bytes(2, byteorder="little")
				p.data.append(8)
				p.data += "Shoppetz".encode("ascii")				
				
				print("Send B1 " + p.data.hex())
				retList.append(p)
			elif stt == "viz":
				p = DNCPacket.Packet()
				p.tp = 0xB5
				
				p.data.append(35)
				p.data.append(1)
				p.data += (256).to_bytes(2, byteorder="little")
				
				visbuff = bytearray( (9, ) )
				
				p.data.append( len(visbuff) )
				p.data += visbuff
		
				retList.append(p)
			
			elif stt == "mob":
				p = DNCPacket.Packet()
				p.tp = 0xB1
				
				p.data.append(2)
				p.data.append(0)
				p.data += (111).to_bytes(2, byteorder="little")
				p.data += (1).to_bytes(2, byteorder="little")
				
				p.data.append(0)
				p.data.append(30)
				p.data.append(6)
				p.data.append(5)
				
				p.data.append(10)
				
				p.data += (90).to_bytes(2, byteorder="little")
				p.data += (90).to_bytes(2, byteorder="little")
				
				p.data.append(0x80)
				p.data.append(2)
				
				p.data.append(0)
				#p.data.append(0)
		
				retList.append(p)
			elif stt == "chr":
				p = CreateCharacter2(111, "ZZZ", 95, 100, False, 0)
		
				retList.append(p)
			
		elif (pin.data[0] == 0x12):
			whisplen = pin.data[1]
			print("\t Whisper for \"{}\": {}".format( pin.data[3:3 + whisplen].decode("utf-8"),  pin.data[3 + whisplen:].decode("utf-8") ) )
			p = DNCPacket.Packet()
			p.tp = 0xBA
			
			p.data.append(0x12)
			p.data.append(1) # direction (1 - To)
			p.data.append( len("AnotherChar") ) # len name
			p.data.append( len("Test string TO 0x12") ) # len msg
			p.data += "AnotherChar".encode("utf-8") #name
			p.data += "Test string TO 0x12".encode("utf-8") #msg
			
			retList.append(p)
			
			p = DNCPacket.Packet()
			p.tp = 0xBA
			
			p.data.append(0x12)
			p.data.append(0) # direction (0 - From)
			p.data.append( len("AnotherChar") ) # len name
			p.data.append( len("Test >_< string FROM 0x12") ) # len msg
			p.data += "AnotherChar".encode("utf-8") #name
			p.data += "Test >_< string FROM 0x12".encode("utf-8") #msg
			
			retList.append(p)
		else:
			print ("Recvd pkt 0xBA {}: ".format(hex(pin.data[0])) + pin.data.hex())
			
	elif (pin.tp == 0xBC):
		print ("Recvd pkt 0xBC {}: ".format(hex(pin.data[0])) + pin.data.hex())
		
		if (pin.data[0] == 0x16):
			wantX = pin.data[1] | (pin.data[2] << 8)
			wantY = pin.data[3] | (pin.data[4] << 8)
			print("\tGo to {}x{}".format(wantX, wantY))
			
			p = DNCPacket.Packet()
			p.tp = 0xB3

			#++0x0
			p.data.append(1)
			p.data += bytes([1, 1]) #Player ID
			
			p.data += bytes([pin.data[1], pin.data[2]])
			p.data += bytes([pin.data[3], pin.data[4]])
		
			retList.append(p)
		elif (pin.data[0] == 0x24):
			
			smltres = pktid & 1
			
			if smltres:
				p = DNCPacket.Packet()
				p.tp = 0xC0

				#++0x0
				p.data.append(0x4A)
				p.data.append(0xA0)
				p.data += bytearray((0x20,0x71, 0 , 00, 00, 00, 00 ,00))
		
				retList.append(p)
			
			p = DNCPacket.Packet()
			p.tp = 0xC0

			#++0x0
			p.data.append(0x6F)
			
			p.data.append(smltres)
		
			retList.append(p)
			
	elif (pin.tp == 0xC2):
		if (pin.data[0] == 0x16):
			print("NOT WANT1")
		elif (pin.data[0] == 0x17):
			print("WANT1")
		elif (pin.data[0] == 0x18):
			print("Want flags: " + hex(pin.data[1]))
			p = DNCPacket.Packet()
			p.tp = 0xC2

			p.data.append(0x1B)
			
			p.data.append(pin.data[1])

			print("Send C2 " + p.data.hex())
			retList.append(p)
		else:
			print("Recvd pkt {} {} ".format(hex(pin.tp), len(pin.data)) + pin.data.hex())
	elif (pin.tp == 0xC1):
		print("Recvd pkt {} {} ".format(hex(pin.tp), len(pin.data)) + pin.data.hex())
		if (pin.data[0] == 0x20):
			name = pin.data[2:]
			p = DNCPacket.Packet()
			p.tp = 0xC1
			
			p.data.append(0x21)
			p.data.append( len(name) )
			p.data += name
			
			print("Send C1 " + p.data.hex())
			retList.append(p)
		elif (pin.data[0] == 0x13):
			objID = int.from_bytes(pin.data[1:], byteorder="little")
			
			p = DNCPacket.Packet()
			p.tp = 0xC1
			
			p.data.append(0x13)
			p.data.append(2)
			p.data += ItemSlot(1120, 1)
			p.data += (22).to_bytes(4, byteorder="little")
			p.data += ItemSlot(4, 5)
			p.data += (33).to_bytes(4, byteorder="little")
			
			print("Send C1 " + p.data.hex())
			retList.append(p)
			
	elif (pin.tp == 0xC4): #Guild things requests
		print ("Recvd pkt 0xC4 {}: ".format(hex(pin.data[0])) + pin.data.hex() )
		if (pin.data[0] == 0x10): #Want emblem for guild
			p = DNCPacket.Packet()
			p.tp = 0xC4
			
			print("\tWant emblem {} {}".format( hex(pin.data[1] | (pin.data[2] << 8) | (pin.data[3] << 16) | (pin.data[4] << 24) ) ,
											  hex(pin.data[5]) ) 
											  )

			#++0x0
			p.data.append(2) #Send guild emblem
			p.data += bytes([128,127,126,125]) #Guild ID
			p.data.append(124) #Guild ID_2
			
			#Emblem file data
			# 1b Filename string size
			# ++ Filename string in game codepage
			# 2b next data size (compressed size + 3 bytes of header)
			# 1b tex width
			# 1b tex height
			# 1b tex format (looks like it's must be 5 or 6 format, or may be 0-4 can be too, but not 7 or 8)
			# ++ compressed data
			
			# 0 format is GL_RGBA and GL_UNSIGNED_SHORT_4_4_4_4    (internal tex GL_RGBA)
			# 1 format is GL_RGBA and GL_UNSIGNED_SHORT_5_5_5_1    (internal tex GL_RGBA)
			# 2 format is GL_RGBA and GL_UNSIGNED_BYTE    (internal tex GL_RGBA)
			# 3 format is GL_LUMINANCE and GL_UNSIGNED_BYTE   (internal tex GL_LUMINANCE)
			# 4 format is GL_LUMINANCE and GL_UNSIGNED_BYTE   (internal tex GL_INTENSITY)
			# 5 format is GL_BGRA_EXT and GL_UNSIGNED_SHORT_4_4_4_4_REV (internal tex GL_RGBA)  +++
			# 6 format is GL_BGRA_EXT and GL_UNSIGNED_SHORT_1_5_5_5_REV (internal tex GL_RGBA)  +++
			# 7 format is GL_BGRA_EXT and GL_UNSIGNED_BYTE (internal tex GL_RGBA)
			# 8 format is GL_RGBA and GL_UNSIGNED_BYTE (internal tex GL_INTENSITY)
			
			# transferred emblem file will be stored in c:/..../app data/.../Sos/Emblem/xxxxxx.emb
			# name is 8 chars xxxxxxxx.emb
			# where xxxxxxx - hex hash 8 chars
			# calculated from -  sdbm(   GUILDID hex (string 8chars) + GUILDID_2 hex (string 2chars)  )
			
			p.data += bytes((0,1,2,3,4,5,6,7,8,9,10,11,12,13,99)) # Just test bytes
		
			retList.append(p)
		else:
			print("Recvd pkt {} {} ".format(hex(pin.tp), len(pin.data)) + pin.data.hex())
			
	else:
		print("Recvd pkt {} {} ".format(hex(pin.tp), len(pin.data)) + pin.data.hex())
	
	return retList

