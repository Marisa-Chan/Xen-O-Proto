#!/usr/bin/python3
import socket
import time 
import threading
import binascii
import config
import DNCPacket

class connThread(threading.Thread):
	def __init__(self, conn, addr):
		threading.Thread.__init__(self)
		self.conn = conn
		self.addr = addr

	def run(self):
		
		while(True):
			outbuf = bytearray()
			
			data = self.conn.recv(8192)
			if (len(data) == 0):
				break
			
			data = bytearray(data)
			
			pin = DNCPacket.getPkt(data, False)
			
			while(pin != None):
				if (pin.tp == 0xB0):
					print("Recvd B0 {}: ".format(len(pin.data)) + pin.data.hex())
					p = DNCPacket.Packet()
					p.tp = 0xB0
					p.data += (0).to_bytes(2, byteorder = "little")
					DNCPacket.placePkt(p, outbuf, self.conn, False)
					
					
					p = DNCPacket.Packet()
					p.tp = 0xB1
					p.data += (0).to_bytes(4, byteorder = "little")
					p.data.append( 0 )
					p.data.append( 2 )
					
					p.data.append( 2 ) #num buddy
					
					#buddy
					p.data += bytes((0x41,0x41,0x41,0x41,0x41,0x41,0,0,0,0,0,0,  0,0,0,0,  0, 1, 1, 1))
					p.data += bytes((0x41,0x41,0x41,0x41,0x43,0x42,0,0,0,0,0,0,  0,0,0,0,  0, 0, 2, 0))
					
					
					p.data.append( 1 ) #num groups
					
					#group
					p.data += bytes((1, 0x44,0x44,0x44,0x44,0x44,0x44,0,0,0,0,0,0,  0))
					DNCPacket.placePkt(p, outbuf, self.conn, False)
					
					
					p = DNCPacket.Packet()
					p.tp = 0xBE
					
					nm = "AAAAAA"
					msg = "Fu you ;)"

					p.data.append( len(nm) )
					p.data.append( len(msg) )
					p.data += nm.encode("ascii")
					p.data += msg.encode("ascii")
					
					DNCPacket.placePkt(p, outbuf, self.conn, False)
					
				else:
					print("Recvd pkt {} {} ".format(hex(pin.tp), len(pin.data)) + pin.data.hex())
					
				pin = DNCPacket.getPkt(data, False)
			
			if (len(outbuf) > 0):
				DNCPacket.sendOutBuf(outbuf, self.conn) 

		self.conn.close()	
		print("Thread Exit")
		return 0

sock = socket.socket()
sock.bind( ("", 18124) )
sock.listen(10)

while(True):
	conn, addr = sock.accept()
	
	th = connThread(conn, addr)
	th.start()

