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

		while(True):
			outbuf = bytearray()
            
			data = self.conn.recv(8192)
			if (len(data) == 0):
				break
			
			data = bytearray(data)
			
			pin = DNCPacket.getPkt(data, True)
            
			while(pin != None):
				
				importlib.reload(hndlGM16)
				
				pkt = hndlGM16.Handle(pin)
				
				for p in pkt:
					p.pktid = pktid
					DNCPacket.placePkt(p, outbuf, self.conn, True)
					pktid += 1
				
								
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

