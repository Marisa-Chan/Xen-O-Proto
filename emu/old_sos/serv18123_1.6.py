#!/usr/bin/python3
import socket
import time
import threading
import binascii
import DNCPacket
import config

pktid = 0

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
					p = DNCPacket.Packet()
					p.tp = 0xB1
					p.pktid = pktid

					#++0x0
					p.data.append(1)
					p.data.append(0)
					p.data += bytes([1, 1])
				
					#++0x4
					p.data += bytes(10)
				
					#++18
					p.data.append(0)
					p.data.append(50) #speed    0-59
					p.data.append(0)
					p.data.append(0)
					p.data.append(0)
					
					p.data += bytes([100, 0])
					p.data += bytes([100, 0])
				
					p.data += bytes(13)
										
					DNCPacket.placePkt(p, outbuf, self.conn, True)
					pktid += 1


					
					#Create another char
					p = DNCPacket.Packet()
					p.tp = 0xB1
					p.pktid = pktid

					#++0x0
					p.data.append(1)
					p.data.append(0)
					p.data += bytes([1, 0])
				
					#++0x4
					p.data += bytes(15)

					p.data += bytes([105, 0])
					p.data += bytes([105, 0])
				
					p.data += bytes(13)
					
					DNCPacket.placePkt(p, outbuf, self.conn, True)
					pktid += 1
					
					print("OK")
				elif (pin.tp == 0xBC):
					print ("Recvd pkt 0xBC {}: ".format(hex(pin.data[0])) + pin.data.hex())
					
					if (pin.data[0] == 0x16):
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

