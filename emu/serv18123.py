#!/usr/bin/python3
import socket
import time
import threading
import binascii
import DNCPacket
import config
import random

pktid = 0		
dront = 0	

class connThread(threading.Thread):
	def __init__(self, conn, addr):
		threading.Thread.__init__(self)
		self.conn = conn
		self.addr = addr

	def run(self):
		global pktid
		global dront

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

					p.data.append(1)
					p.data += bytes([1, 1])
					p.data += bytes([1, 0, 0, 0] )
					
					DNCPacket.placePkt(p, outbuf, self.conn, True)
					pktid += 1				
				
				
				
					#Load map
					p = DNCPacket.Packet()
					p.tp = 0xB0
					p.pktid = pktid

					p.data.append(0x11)
					p.data += bytes([0x28, 1, 0, 0]) #MAPID
					p.data += bytes([20, 0]) #POSX
					p.data += bytes([20, 0]) #POSY

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
					#p.data += bytes([17, 17, 17, 17])
					#p.data += bytes([240, ]) #POW
					#p.data += bytes([239, ]) #STA
					#p.data += bytes([238, ]) #AGI
					#p.data += bytes([237, ]) #INT
					#p.data += bytes([236, ]) #MEN
					#p.data += bytes([235, ]) #WIS
					#p.data += bytes([0, 0])
					#ii = 0
					#while (ii < 0x92):
					#	tmp.append(0)
					#	ii += 1
					p.data += bytes(204-0xf)
					
					DNCPacket.placePkt(p, outbuf, self.conn, True)
					pktid += 1
					
								

					#Create player char
					p = DNCPacket.Packet()
					p.tp = 0xB1
					p.pktid = pktid

					#++0x0
					p.data.append(1)
					p.data.append(1)
					p.data += bytes([1, 1])
				
					#++0x4
					p.data += bytes(14)
				
					#++18
					p.data.append(21)
					p.data.append(20) #speed    0-59
					p.data.append(22)
					p.data.append(23)
					p.data.append(24)
					
					p.data += bytes([20, 0])
					p.data += bytes([20, 0])
				
					p.data += bytes(20)
					p.data.append(0)
					p.data.append(0)
					
					DNCPacket.placePkt(p, outbuf, self.conn, True)
					pktid += 1
					
					
					### Add items
					p = DNCPacket.Packet()
					p.tp = 0xC0
					p.pktid = pktid

					#++0x0
					p.data.append(0x31)
					p.data.append(0x1)
					p.data += bytes((1, 0, 10, 0))
					p.data += bytes((0, 0, 0, 0))

					DNCPacket.placePkt(p, outbuf, self.conn, True)
					pktid += 1
					
					
					### Set skills
					p = DNCPacket.Packet()
					p.tp = 0xC0
					p.pktid = pktid

					#++0x0
					p.data.append(0x50)
					p.data.append(2)
					p.data += bytes([12, 0])
					p.data += bytes([13, 0])

	
					DNCPacket.placePkt(p, outbuf, self.conn, True)
					pktid += 1



					#Create another char
					p = DNCPacket.Packet()
					p.tp = 0xB1
					p.pktid = pktid

					#++0x0
					p.data.append(1)
					p.data.append(1)
					p.data += bytes([1, 0])
				
					#++0x4
					p.data += bytes(14)
				
					#++18
					p.data += bytes(5)
					
					p.data += bytes([25, 0])
					p.data += bytes([25, 0])
				
					p.data += bytes(20)
					p.data.append(0)
					p.data.append(0)
					
					DNCPacket.placePkt(p, outbuf, self.conn, True)
					pktid += 1
				
					print("OK")
				elif (pin.tp == 0xBC):
					print ("Recvd pkt 0xBC {}: ".format(hex(pin.data[0])) + pin.data.hex())
					
					if (pin.data[0] == 0x11 or pin.data[0] == 0x12):
# 						if (dront & 1) == 0:
# 							p = DNCPacket.Packet()
# 							p.tp = 0xC0
# 							p.pktid = pktid
#
# 							#++0x0
# 							p.data.append(0x41)
# 							p.data += bytes([12, 0])
#
# 							print(dront)
# 							dront += 1
# 				
# 							DNCPacket.placePkt(p, outbuf, self.conn, True)
# 							pktid += 1
# 						else:
						p = DNCPacket.Packet()
						p.tp = 0xC0
						p.pktid = pktid

						#++0x0
						p.data.append(0x71)
						
						p.data += bytes([70, 0, 0, 0])
						p.data += bytes([25, 0, 35, 0])
						
						print(dront)
						dront += 1
		
						DNCPacket.placePkt(p, outbuf, self.conn, True)
						pktid += 1
						
					elif (pin.data[0] == 0x16):
						wantX = pin.data[1] | (pin.data[2] << 8)
						wantY = pin.data[3] | (pin.data[4] << 8)
						print("Go to {}x{}".format(wantX, wantY))
						
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
					elif (pin.data[0] == 0x19):
						emote = pin.data[1]
						print("Emote {}".format(emote))
						
						p = DNCPacket.Packet()
						p.tp = 0xB5
						p.pktid = pktid

						#++0x0
						p.data.append(0x16)
						p.data.append(1) #player scope
						p.data += bytes([1, 1]) #Player ID
						
						p.data.append(emote)
						
						DNCPacket.placePkt(p, outbuf, self.conn, True)
						pktid += 1
					elif (pin.data[0] == 0xAA):
						p = DNCPacket.Packet()
						p.tp = 0xB5
						p.pktid = pktid

						#++0x0
						p.data.append(0xFE)
						p.data.append(1)
						p.data += bytes([1, 1]) #Player ID
						
						#print(dront)
						#dront += 1
					
						DNCPacket.placePkt(p, outbuf, self.conn, True)
						pktid += 1
				elif (pin.tp == 0xBA):
					print ("Recvd pkt 0xBA {}: ".format(hex(pin.data[0])) + pin.data.hex())
					
					if (pin.data[0] == 0x11 and pin.data[1] == len(pin.data) - 2):
						line = pin.data[2:]
						if (line[:2].decode("ascii") == "op"):
							bb = int(line[2:])
						
							p = DNCPacket.Packet()
							p.tp = 0xB5
							p.pktid = pktid

							#++0x0
							p.data.append(0x18)
							p.data.append(1)
							p.data += bytes([1, 1]) #Player ID
							p.data += bytes([bb, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
						
							print(bb)
					
							DNCPacket.placePkt(p, outbuf, self.conn, True)
						elif (line[:2].decode("ascii") == "b0"):
							p = DNCPacket.Packet()
							p.tp = 0x03
							p.pktid = pktid

							#++0x0
							p.data += bytes([0xFF, 0x0F]) #word
					
							DNCPacket.placePkt(p, outbuf, self.conn, True)	
						
				elif (pin.tp == 0xB0):
					print ("Recvd pkt 0xB0 (Want disconnect): " + pin.data.hex())
					
					p = DNCPacket.Packet()
					p.tp = 0x03
					p.pktid = pktid

					#++0x0
					p.data += bytes([0, 0]) #word
					
					DNCPacket.placePkt(p, outbuf, self.conn, True)	
					
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

while(True):
	conn, addr = sock.accept()

	th = connThread(conn, addr)
	print("Connect!")
	th.start()

