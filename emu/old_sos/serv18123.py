#!/usr/bin/python3
import socket
import time
import threading
import binascii
import config

pktid = 0

def sub_37A2FC(a1, a2):
	v2 = a2 % 8
	if ( v2 > 0 ):
		a1 = ((a1 >> v2) | (a1 << (16 - v2))) & 0xFFFF
	return a1

def sub_37A348(a1, a2):
	v2 = a2 % 8
	if ( v2 > 0 ):
		a1 = ((a1 << v2) | (a1 >> (16 - v2))) & 0xFFFF
	return a1

def decrPktLen(pkt):
	v6 = sub_37A2FC((pkt[0] | (pkt[1] << 8)), pkt[2] % 7 + 1) ^ 0xEF25
	v6 = sub_37A348(v6, pkt[3] % 7 + 1)
	pkt[0] = v6 & 0xFF
	pkt[1] = (v6 >> 8) & 0xFF

def encrPktLen(pkt):
	v6 = sub_37A2FC((pkt[0] | (pkt[1] << 8)), pkt[3] % 7 + 1) ^ 0xEF25
	v6 = sub_37A348(v6, pkt[2] % 7 + 1)
	pkt[0] = v6 & 0xFF
	pkt[1] = (v6 >> 8) & 0xFF

def r8r(val, shft):
	v2 = shft % 8
	if ( v2 > 0 ):
		val = ((val >> v2) | (val << (8 - v2))) & 0xFF
	return val

def l8r(val, shft):
	v2 = shft % 8
	if ( v2 > 0 ):
		val = ((val << v2) | (val >> (8 - v2))) & 0xFF
	return val

def r32r(val, shft):
	v2 = shft % 8
	if ( v2 > 0 ):
		val = ((val >> v2) | (val << (32 - v2))) & 0xFFFFFFFF
	return val

def l32r(val, shft):
	v2 = shft % 8
	if ( v2 > 0 ):
		val = ((val << v2) | (val >> (32 - v2))) & 0xFFFFFFFF
	return val

def sub_37A744(pkt, shft):
	v2 = 0
	if ( shft - 1 >= 0 ):
		v4 = shft
		v5 = 0
		while(True):
			v2 = ((v2 << 16) + (v2 << 6) + pkt[v5] - v2) & 0xFFFFFFFF
			v5 += 1
			v4 -= 1
			if ( v4 == 0 ):
				break
	return v2

def decrPkt(pkt):
	pktlen = pkt[0] | (pkt[1] << 8)
	if (pktlen >= 6): 
		pkt[2] = r8r(pkt[2], pkt[3])
		v24 = (pkt[3] | (pkt[4] << 8) | (pkt[5] << 16) | (pkt[6] << 24)) % 7 + 1
		v3 = (pktlen - 5) // 4
		v23 = v3
		
		if ( v3 - 1 >= 0 ):
			v4 = v3
			v5 = 0
			while(True):
				tmp = r32r( (pkt[4 * v5 + 7] | (pkt[4 * v5 + 8]<<8) | (pkt[4 * v5 + 9]<<16) | (pkt[4 * v5 + 10]<<24)), v24)
				pkt[4 * v5 + 7] = tmp & 0xFF
				pkt[4 * v5 + 8] = (tmp >> 8) & 0xFF
				pkt[4 * v5 + 9] = (tmp >> 16) & 0xFF
				pkt[4 * v5 + 10] = (tmp >> 24) & 0xFF
				v5 += 1
				v4 -= 1
				if (v4 == 0):
					break
		
		v23 *= 4
		v6 = v23
		v7 = (pktlen - 5) % 4 + v23 - 1
		if ( v7 - v23 >= 0 ):
			v10 = v7 - v23 + 1
			while(True):
				pkt[v6 + 7] = r8r(pkt[v6 + 7], v24)
				v6 += 1
				v10 -= 1
				if (v10 == 0):
					break
		
		if ( sub_37A744(pkt[7:], pktlen - 5) == (pkt[3] | (pkt[4] << 8)| (pkt[5] << 16)| (pkt[6] << 24))):
			v12 = pkt[1] ^ pkt[0] ^ 0x25
			pkt[7] ^= v12
			v13 = pkt[7] ^ v12
			pkt[2] ^= v13
			
			if ( pktlen > 6 ):
				v25 = v13 | (v13 << 8) | (v13 << 16) | (v13 << 24)
				v25 ^= 0xC08AEF25
				v14 = (pktlen - 6) // 4
				v23 = v14
				if ( v14 - 1 >= 0 ):
					v15 = v14
					v16 = 0
					while(True):
						pkt[4 * v16 + 8] ^= (v25 & 0xFF)
						pkt[4 * v16 + 9] ^= ((v25 >> 8) & 0xFF)
						pkt[4 * v16 + 10] ^= ((v25 >> 16) & 0xFF)
						pkt[4 * v16 + 11] ^= ((v25 >> 24) & 0xFF)
						v25 = l32r(v25, 1)
						v16 += 1
						v15 -= 1
						if (v15 == 0):
							break
				
				v23 *= 4
				if ( (pktlen - 6) % 4 - 1 >= 0):
					v17 = (pktlen - 6) % 4
					v18 = 0
					while(True):
						pkt[v23 + 8 + v18] ^= (v25 >> (v18 * 8) & 0xFF )
						v18 += 1
						v17 -= 1
						if (v17 == 0):
							break

def encr(msg):
	pktlen = msg[0] | (msg[1] << 8)
	if (pktlen >= 6):
		v2 = msg[1] ^ msg[0] ^ 0x25
		v3 = v2 ^ msg[7]
		msg[2] ^= v3
		msg[7] ^= v2
		
		if ( pktlen > 6 ):
			v26 = v3 | (v3 << 8) | (v3 << 16) | (v3 << 24)
			v26 ^= 0xC08AEF25
			v4 = (pktlen - 6) // 4
			v24 = v4
			
			if ( v4 - 1 >= 0 ):
				v5 = v4
				v6 = 0
				while(True):
					msg[4 * v6 + 8] ^= (v26 & 0xFF)
					msg[4 * v6 + 9] ^= ((v26 >> 8) & 0xFF)
					msg[4 * v6 + 10] ^= ((v26 >> 16) & 0xFF)
					msg[4 * v6 + 11] ^= ((v26 >> 24) & 0xFF)
					v26 = l32r(v26, 1)
					v6 += 1
					v5 -= 1
					if (v5 == 0):
						break
			
			v24 *= 4
			if ((pktlen - 6) % 4 - 1 >= 0 ):
				v7 = (pktlen - 6) % 4
				v8 = 0
				while(True):
					msg[v24 + 8 + v8] ^= (v26 >> (v8 * 8) & 0xFF )
					v8 += 1
					v7 -= 1
					if (v7 == 0):
						break
			
			v9 = sub_37A744(msg[7:], pktlen - 5) #hash
			msg[3] = v9 & 0xFF
			msg[4] = (v9 >> 8) & 0xFF
			msg[5] = (v9 >> 16) & 0xFF
			msg[6] = (v9 >> 24) & 0xFF
			
			v25 = v9 % 7 + 1
			v10 = (pktlen - 5) // 4
			v24 = v10
			if ( v10 - 1 >= 0):
				v11 = v10
				v12 = 0
				while(True):
					tmp = l32r( (msg[4 * v12 + 7] | (msg[4 * v12 + 8]<<8) | (msg[4 * v12 + 9]<<16) | (msg[4 * v12 + 10]<<24)), v25)
					msg[4 * v12 + 7] = tmp & 0xFF
					msg[4 * v12 + 8] = (tmp >> 8) & 0xFF
					msg[4 * v12 + 9] = (tmp >> 16) & 0xFF
					msg[4 * v12 + 10] = (tmp >> 24) & 0xFF
					v12 += 1
					v11 -= 1
					if (v11 == 0):
						break
			
			v24 *= 4
			v13 = (pktlen - 5) % 4
			v14 = v24
			v15 = v13 + v24 - 1
			v17 = v15 - v24
			if ( v17 >= 0):
				v18 = v17 + 1
				while(True):
					msg[v14 + 7] = l8r(msg[v14 + 7], v25)
					v14 += 1
					v18 -= 1
					if ( v18 == 0):
						break
			
			msg[2] = l8r(msg[2], msg[3])
			encrPktLen(msg)
				

class connThread(threading.Thread):
	def __init__(self, conn, addr):
		threading.Thread.__init__(self)
		self.conn = conn
		self.addr = addr

	def run(self):
		global pktid

		while(True):
			data = self.conn.recv(8192)
			if (len(data) == 0):
				break
			
			data = bytearray(data)
			
			decrPktLen(data)
			
			#print("Recvd not decr pkt {} ".format(len(data)) + data.hex())
			
			decrPkt(data)
			
			pktlen = data[0] | (data[1] << 8)
			if (pktlen == len(data) - 2):
				if (data[2] == 0xBF):
					print("Recvd BF {}: ".format(pktlen) + data[2:].hex())
					
					#New!
					tmp = bytearray()
					tmp.append(0)
					tmp.append(0)
					tmp.append(0xBF)
					tmp += bytes([0, 0, 0, 0]) #hash
					#+0x7
					tmp.append(pktid & 0xFF) 
					tmp.append(1)
					tmp += bytes([1, 1])
					tmp += bytes([1, 0, 0, 0] )
					
					tmp[0] = len(tmp) - 2

					encr(tmp)
					self.conn.send( tmp )
					
					pktid += 1
					del tmp
					
					
					#Load map
					tmp = bytearray()
					tmp.append(0)
					tmp.append(0)
					tmp.append(0xB0)
					tmp += bytes([0, 0, 0, 0]) #hash
					#+0x7
					tmp.append(pktid & 0xFF) 
					tmp.append(0x11)
					tmp += bytes([0x90, 0, 0, 0]) #MAPID
					tmp += bytes([100, 0]) #POSX
					tmp += bytes([100, 0]) #POSY
					
					tmp[0] = len(tmp) - 2

					encr(tmp)
					self.conn.send( tmp )
					
					pktid += 1
					del tmp
					
					
					#Show 
					tmp = bytearray()
					tmp.append(0)
					tmp.append(0)
					tmp.append(0xB0)
					tmp += bytes([0, 0, 0, 0]) #hash
					#+0x7
					tmp.append(pktid & 0xFF) 
					tmp.append(0x13)
					
					tmp[0] = len(tmp) - 2

					encr(tmp)
					self.conn.send( tmp )
					
					pktid += 1
					del tmp

					
					
					#Set player info
					tmp = bytearray()
					tmp.append(0)
					tmp.append(0)
					tmp.append(0xC0)
					tmp += bytes([0, 0, 0, 0]) #hash
					#+0x7
					tmp.append(pktid & 0xFF) 
					tmp.append(0x0)
					
					tmp += bytes([10, 0, 0, 0]) #Kron
					tmp += bytes([0, 0, 0, 0])
					tmp.append(0x2B) #???
					tmp.append(0x1) #JOB
					tmp.append(0x0) #Hair
					tmp += bytes([0, 1]) #HP
					tmp += bytes([0, 1]) #MP
					tmp.append(250) #Level
					tmp += bytes([17, 17, 17, 17])
					tmp += bytes([240, ]) #POW
					tmp += bytes([239, ]) #STA
					tmp += bytes([238, ]) #AGI
					tmp += bytes([237, ]) #INT
					tmp += bytes([236, ]) #MEN
					tmp += bytes([235, ]) #WIS
					tmp += bytes([0, 0])
					ii = 0
					while (ii < 0x92):
						tmp.append(0)
						ii += 1
					
					tmp[0] = len(tmp) - 2

					encr(tmp)
					self.conn.send( tmp )
					
					pktid += 1
					del tmp
					
					

					#Create player char
					tmp = bytearray()
					tmp.append(0)
					tmp.append(0)
					tmp.append(0xB1)
					tmp += bytes([0, 0, 0, 0]) #hash
					#+0x7
					tmp.append(pktid & 0xFF) 
					
					#++0x0
					tmp.append(1)
					tmp.append(0)
					tmp += bytes([1, 1])
					
					#++0x4
					ii = 0
					while (ii < 10):
						tmp.append(0)
						ii += 1
					
					#++14
					tmp.append(0)
					tmp.append(50) #speed
					tmp.append(0)
					tmp.append(0)
					tmp.append(0)
						
					tmp += bytes([100, 0])
					tmp += bytes([100, 0])
					
					ii = 0
					while (ii < 10):
						tmp.append(0)
						ii += 1
					
					tmp[0] = len(tmp) - 2

					encr(tmp)
					self.conn.send( tmp )
					
					pktid += 1
					del tmp
					

					#Create another char
					tmp = bytearray()
					tmp.append(0)
					tmp.append(0)
					tmp.append(0xB1)
					tmp += bytes([0, 0, 0, 0]) #hash
					#+0x7
					tmp.append(pktid & 0xFF) 
					tmp.append(1)
					tmp.append(0)
					tmp += bytes([1, 0])
					ii = 0
					while (ii < 15):
						tmp.append(0)
						ii += 1
						
					tmp += bytes([105, 0])
					tmp += bytes([105, 0])
					
					ii = 0
					while (ii < 10):
						tmp.append(0)
						ii += 1
					
					tmp[0] = len(tmp) - 2

					encr(tmp)
					self.conn.send( tmp )
					
					pktid += 1
					del tmp

					
					print("OK")
				elif (data[2] == 0xBC):
					print ("Recvd pkt 0xBC {}: ".format(hex(data[8])) + data.hex())
						   
					if (data[8] == 0x16):
						wantX = data[9] | (data[10] << 8)
						wantY = data[11] | (data[12] << 8)
						print("Go to {}x{}".format(wantX, wantY))
						
						tmp = bytearray()
						tmp.append(0)
						tmp.append(0)
						tmp.append(0xB3)
						tmp += bytes([0, 0, 0, 0]) #hash
						#+0x7
						tmp.append(pktid & 0xFF)
						   
						tmp.append(0x1)						   
						tmp += bytes([1, 1]) #Player ID
						
						tmp += bytes([data[9], data[10]])
						tmp += bytes([data[11], data[12]])
						
						tmp[0] = len(tmp) - 2
						   
						encr(tmp)
						self.conn.send( tmp )
					
						pktid += 1
						del tmp
						
				else:
					print("Recvd pkt {} ".format(len(data)) + data.hex())
			else:
				print("Recvd not packet {} ".format(len(data)) + data.hex())

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

