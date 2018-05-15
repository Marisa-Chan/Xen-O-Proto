#!/usr/bin/python3
import socket
import time 
import threading
import binascii
import config

def genChar(strm, charnumber, name, var):
	#0
	strm += bytes([charnumber, ]) #Char slot
	#+0x1
	strm += name.ljust(13, chr(0)).encode("UTF-8") ##Charname 13 max
	#+0xE
	strm += bytes([250, ]) #LVL
	strm += socket.inet_aton(config.SERVIP) ## Server IP
	#+0x13
	strm += bytes([240, ]) #POW
	strm += bytes([239, ]) #STA
	strm += bytes([238, ]) #AGI
	strm += bytes([237, ]) #INT
	strm += bytes([236, ]) #MEN
	strm += bytes([235, ]) #WIS
	#+0x19
	strm += bytes([0, ]) #JOB and SEX 0x80 - male, 00 - Female
	strm += bytes([var, ]) #?????
	strm += bytes([0, ]) #Outfit?
	strm += bytes([0, ]) #Hair + 3 colors. 0x0-0x2, 0xa-0xc, 0x14-0x16
	strm += bytes([0, ]) 
	#+0x1E
	strm += bytes([0, ]) #Face accessory
	strm += bytes([0x00, 0x00, 0x00, 0x00, 0x00])
	#+0x24
	strm += bytes([0, 0, 0, 0, 0, 0])
	#+0x2A
	strm += bytes([0, 0, 0])


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
				if (data[2] == 0xD3):
					print("Recvd D3 {}: ".format(pktlen) + data[2:].hex())
					tmp = bytearray()
					tmp.append(0)
					tmp.append(0)
					tmp.append(0xD3)
					tmp.append(0)
					tmp[0] = len(tmp) - 2
					self.conn.send( tmp )
					#print("Send:")
					#print(tmp)
					del tmp
				elif (data[2] == 0xD4):
					print("Recvd D4 {}: ".format(pktlen) + data[2:].hex())
					tmp = bytearray()
					tmp.append(0)
					tmp.append(0)
					tmp.append(0xD4)
					tmp += socket.inet_aton(config.SERVIP) # msg server?
					
					tmp.append(4) #Num of characters, MAX == 5
					genChar(tmp, 0, "Char1", 0)
					genChar(tmp, 1, "Char2", 1)
					genChar(tmp, 2, "Char3", 2)
					genChar(tmp, 3, "Char4", 3)

					tmp[0] = len(tmp) - 2
					self.conn.send( tmp )
					#print("Send:")
					#print(tmp)
					del tmp
				elif (data[2] == 0xD7):
					print("Recvd D7 {}: ".format(pktlen) + data[2:].hex())
					tmp = bytearray()
					tmp.append(0)
					tmp.append(0)
					tmp.append(0xD7)
					tmp.append(0)
					tmp[0] = len(tmp) - 2
					self.conn.send( tmp )
					#print("Send:")
					#print(tmp)
					del tmp
				else:
					print("Recvd {} ".format(pktlen) + data.hex())

		self.conn.close()	
		print("Thread Exit")
		return 0

sock = socket.socket()
sock.bind( ("", 1819) )
sock.listen(10)

while(True):
	conn, addr = sock.accept()
	
	th = connThread(conn, addr)
	th.start()

