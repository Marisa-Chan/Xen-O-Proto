#!/usr/bin/python3
import socket
import time 
import threading
import binascii
import config

class connThread(threading.Thread):
	def __init__(self, conn, addr):
		threading.Thread.__init__(self)
		self.conn = conn
		self.addr = addr

	def run(self):
		
		while(True):
			data = self.conn.recv(8192)
			if (len(data) == 0):
				break
			
			pktlen = data[0] | (data[1] << 8)
			if (pktlen == len(data) - 2):
				if (data[2] == 0xB0):
					print("Recvd B0 {}: ".format(pktlen) + data[2:].hex())
					tmp = bytearray()
					tmp.append(0)
					tmp.append(0)
					tmp.append(0xB1)
					tmp += bytes([0, 0, 0, 0])
					tmp.append(0)
					tmp.append(0)
					tmp.append(0)
					tmp.append(0)
					
					tmp[0] = len(tmp) - 2
					#self.conn.send( tmp )
					#print("Send:")
					#print(tmp)
					del tmp
				else:
					print("Recvd {} ".format(pktlen) + data.hex())

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

