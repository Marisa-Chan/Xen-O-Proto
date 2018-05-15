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

