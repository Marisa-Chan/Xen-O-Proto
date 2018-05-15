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
				if (data[2] == 0xD0): 
					print("Recvd D0 ({}) :".format(len(data)) + data[2:].hex())
					tmp = bytearray()
					tmp.append(0)
					tmp.append(0)
					tmp.append(0xD0)
					tmp.append(0)
					tmp += bytes([0, 0, 0, 0])
					tmp += bytes([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 8, 0, 0, 3])
					tmp += bytes([2, 0xFF, 0xFF])
					tmp[0] = len(tmp) - 2
					self.conn.send( tmp )
					#print("Send:")
					#print(tmp)
					del tmp

				elif (data[2] == 0xD1):
					print("Recvd D1 :" + data[2:].hex())
					tmp = bytearray()
					tmp.append(0)
					tmp.append(0)
					tmp.append(0xD1)
					
					tmp.append(5) #Num of servers, MAX == 10
					tmp += bytes([0, ])
					tmp += "Server1".ljust(13, chr(0)).encode("UTF-8")
					tmp += socket.inet_aton(config.SERVIP) + bytes([0, 0])
					
					tmp += bytes([0, ])
					tmp += "Server2".ljust(13, chr(0)).encode("UTF-8")
					tmp += socket.inet_aton(config.SERVIP) + bytes([0, 0])
					
					tmp += bytes([0, ])
					tmp += "Server3".ljust(13, chr(0)).encode("UTF-8")
					tmp += socket.inet_aton(config.SERVIP) + bytes([0, 0])
					
					tmp += bytes([0, ])
					tmp += "Server4".ljust(13, chr(0)).encode("UTF-8")
					tmp += socket.inet_aton(config.SERVIP) + bytes([0, 0])
					
					tmp += bytes([0, ])
					tmp += "Server5".ljust(13, chr(0)).encode("UTF-8")
					tmp += socket.inet_aton(config.SERVIP) + bytes([0, 0])
					
					tmp[0] = len(tmp) - 2
					self.conn.send( tmp )
					#print("Send:")
					#print(tmp)
					del tmp

				else:
					print("Recvd " + data.hex())

		self.conn.close()	
		print("Thread Exit")
		return 0

sock = socket.socket()
sock.bind( ("", 1818) )
sock.listen(10)

while(True):
	conn, addr = sock.accept()
	
	th = connThread(conn, addr)
	th.start()

