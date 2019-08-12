#!/usr/bin/python3
import socket
import time
import threading
import binascii
import DNCPacket
import config
import importlib
import hndlGM16

pktid = 0
config.NETXORKEY = 0xB244C01E



class connThread(threading.Thread):
	def __init__(self, conn, addr):
		threading.Thread.__init__(self)
		self.conn = conn
		self.addr = addr

	def run(self):
		global pktid
		
		pktwait = list()
		self.conn.setblocking(0)

		while(True):
			outbuf = bytearray()
			time.sleep(0.01)
            
			try:
				data = self.conn.recv(8192)
			except:
				pktwait2 = list()
				for p in pktwait:
					#print(hex(p.tp))
					if p.wait < time.time():
						p.pktid = pktid
						DNCPacket.placePkt(p, outbuf, self.conn, True)
						
						pktid += 1
					else:
						pktwait2.append(p)
				
				if (len(outbuf) > 0):
					DNCPacket.sendOutBuf(outbuf, self.conn) 
				
				pktwait = pktwait2
			else:
				if len(data) == 0:
					break
				else:
					data = bytearray(data)
			
					pin = DNCPacket.getPkt(data, True)
            
					while(pin != None):
				
						importlib.reload(hndlGM16)
				
						pkt = hndlGM16.Handle(pin)
				
						for p in pkt:
							if p.wait == 0:
								p.pktid = pktid
								DNCPacket.placePkt(p, outbuf, self.conn, True)
								pktid += 1
							else:
								pktwait.append(p)
				
								
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

