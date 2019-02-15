#!/usr/bin/python3
import socket
import time
import threading
import binascii
import DNCPacket
import config

pktid = 0
config.NETXORKEY = 0xB244C01E

def CreateCharacter(ID, NAME, X, Y):
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
	p.data.append(0)                       #Acc level or iconID or what? (240+ - has "GM" mark)
	
	#++0x13 (19)
	p.data += X.to_bytes(2, byteorder = "little")  #X coord
	p.data += Y.to_bytes(2, byteorder = "little")  #Y coord
	
	#++0x17 (23)
	p.data += (0x12345678).to_bytes(4, byteorder = "little")  #???Guild ID??
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
	

class connThread(threading.Thread):
	def __init__(self, conn, addr):
		threading.Thread.__init__(self)
		self.conn = conn
		self.addr = addr

	def run(self):
		global pktid

		while(True):
			outbuf = bytearray()
            
			data = self.conn.recv(8192)
			if (len(data) == 0):
				break
			
			data = bytearray(data)
			
			pin = DNCPacket.getPkt(data, True)
            
			while(pin != None):
				if (pin.tp == 0xBF):
					print("Recvd BF : " + pin.data.hex())
					
					#New!
					p = DNCPacket.Packet()
					p.tp = 0xBF
					p.pktid = pktid

					p.data.append(1)               #player object scope (1,2,3). 1 - player type, 2 - monster type, 3 - npc type
					p.data += bytes([1, 1])        #player object ID (for example 0x101 == 257)
					p.data += bytes([2, 0, 0, 0] ) #some timestamp
					
					DNCPacket.placePkt(p, outbuf, self.conn, True)
					pktid += 1					
					
					#Load map
					p = DNCPacket.Packet()
					p.tp = 0xB0
					p.pktid = pktid

					p.data.append(0x11)
					p.data += bytes([84, 0, 0, 0]) #MAPID
					p.data += bytes([100, 0]) #POSX
					p.data += bytes([100, 0]) #POSY

					DNCPacket.placePkt(p, outbuf, self.conn, True)
					pktid += 1
					
					#Show 
					p = DNCPacket.Packet()
					p.tp = 0xB0
					p.pktid = pktid

					p.data.append(0x13)
					
					DNCPacket.placePkt(p, outbuf, self.conn, True)
					pktid += 1
					
					#Set player info
					p = DNCPacket.Packet()
					p.tp = 0xC0
					p.pktid = pktid

					p.data.append(0x0)
				
					p.data += bytes([10, 0, 0, 0]) #Kron
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
					
					DNCPacket.placePkt(p, outbuf, self.conn, True)
					pktid += 1




					#Create player char
					p = CreateCharacter(257, "YourChar", 100, 100)
					p.pktid = pktid
					
					DNCPacket.placePkt(p, outbuf, self.conn, True)
					pktid += 1


					#Create player char
					p = CreateCharacter(256, "AAAAAA", 105, 100)
					p.pktid = pktid
					
					DNCPacket.placePkt(p, outbuf, self.conn, True)
					pktid += 1
					
					
					p = DNCPacket.Packet()
					p.tp = 0xB5
					p.pktid = pktid
					
					p.data.append(0x1A)
					p.data.append(1)
					p.data += (256).to_bytes(2, byteorder = "little")
					
					DNCPacket.placePkt(p, outbuf, self.conn, True)
					pktid += 1
					
					print("OK")
				elif (pin.tp == 0xBA):
					print("Packet 0xBA:")
					if (pin.data[0] == 0x11):
						print("\t Normal msg len == {} : {}".format( str(pin.data[1]), pin.data[2:].decode("utf-8") ) )
						p = DNCPacket.Packet()
						p.tp = 0xBA
						p.pktid = pktid
						
						p.data.append(0x11)
						p.data.append(1) # scope
						p.data += (256).to_bytes(2, byteorder = "little") # obj ID  256 - for another character
						p.data.append( len("Test string of 0x11") ) #msg len
						p.data += "Test string of 0x11".encode("utf-8") #msg
						
						DNCPacket.placePkt(p, outbuf, self.conn, True)
						pktid += 1
					elif (pin.data[0] == 0x12):
						whisplen = pin.data[1]
						print("\t Whisper for \"{}\": {}".format( pin.data[3:3 + whisplen].decode("utf-8"),  pin.data[3 + whisplen:].decode("utf-8") ) )
						p = DNCPacket.Packet()
						p.tp = 0xBA
						p.pktid = pktid
						
						p.data.append(0x12)
						p.data.append(1) # direction (1 - To)
						p.data.append( len("AnotherChar") ) # len name
						p.data.append( len("Test string TO 0x12") ) # len msg
						p.data += "AnotherChar".encode("utf-8") #name
						p.data += "Test string TO 0x12".encode("utf-8") #msg
						
						DNCPacket.placePkt(p, outbuf, self.conn, True)
						pktid += 1
						
						p = DNCPacket.Packet()
						p.tp = 0xBA
						p.pktid = pktid
						
						p.data.append(0x12)
						p.data.append(0) # direction (0 - From)
						p.data.append( len("AnotherChar") ) # len name
						p.data.append( len("Test >_< string FROM 0x12") ) # len msg
						p.data += "AnotherChar".encode("utf-8") #name
						p.data += "Test >_< string FROM 0x12".encode("utf-8") #msg
						
						DNCPacket.placePkt(p, outbuf, self.conn, True)
						pktid += 1
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
						p.pktid = pktid

						#++0x0
						p.data.append(1)
						p.data += bytes([1, 1]) #Player ID
						
						p.data += bytes([pin.data[1], pin.data[2]])
						p.data += bytes([pin.data[3], pin.data[4]])
					
						DNCPacket.placePkt(p, outbuf, self.conn, True)
						pktid += 1
						
				elif (pin.tp == 0xC4): #Guild things requests
					print ("Recvd pkt 0xC4 {}: ".format(hex(pin.data[0])) + pin.data.hex() )
					if (pin.data[0] == 0x10): #Want emblem for guild
						p = DNCPacket.Packet()
						p.tp = 0xC4
						p.pktid = pktid
						
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
					
						DNCPacket.placePkt(p, outbuf, self.conn, True)
						pktid += 1
						
				else:
					print("Recvd pkt {} {} ".format(hex(pin.tp), len(pin.data)) + pin.data.hex())
				
				pin = DNCPacket.getPkt(data, True)
			
			if (len(outbuf) > 0):
				DNCPacket.sendOutBuf(outbuf, self.conn) 

		self.conn.close()
		print("Thread Exit")
		return 0

sock = socket.socket()
sock.bind( ("", 18123) )
sock.listen(10)

print("Ready!")

while(True):
	conn, addr = sock.accept()

	th = connThread(conn, addr)
	print("Connect!")
	th.start()

