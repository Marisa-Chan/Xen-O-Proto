#!/usr/bin/python3
import config

def sdbm(a):
	h = 0
	for b in a:
		h = b + (h << 16) + (h << 6) - h;
	
	return h & 0xFFFFFFFF


class Packet:
	tp = 0
	pktid = 0
	data = None
	
	def __init__(self):
		self.data = bytearray()
		self.tp = 0
		self.pktid = 0

def r8r(val, s):
		s = s % 8
		if ( s > 0 ):
			val = ((val >> s) | (val << (8 - s))) & 0xFF
		return val
	
def l8r(val, s):
	s = s % 8
	if ( s > 0 ):
		val = ((val << s) | (val >> (8 - s))) & 0xFF
	return val

def r16r(val, s):
	s = s % 8
	if ( s > 0 ):
		val = ((val >> s) | (val << (16 - s))) & 0xFFFF
	return val

def l16r(val, s):
	s = s % 8
	if ( s > 0 ):
		val = ((val << s) | (val >> (16 - s))) & 0xFFFF
	return val

def r32r(val, s):
	s = s % 8
	if ( s > 0 ):
		val = ((val >> s) | (val << (32 - s))) & 0xFFFFFFFF
	return val

def l32r(val, s):
	s = s % 8
	if ( s > 0 ):
		val = ((val << s) | (val >> (32 - s))) & 0xFFFFFFFF
	return val

def decrPktLen(pkt):
	if len(pkt) > 3:
		ln = r16r(  int.from_bytes(pkt[:2],"little")  ,   pkt[2] % 7 + 1  ) ^ (config.NETXORKEY & 0xFFFF)
		ln = l16r(  ln,  pkt[3] % 7 + 1 )
		pkt[0] = ln & 0xFF
		pkt[1] = (ln & 0xFF00) >> 8
		return ln + 2

def encrPktLen(pkt):
	if len(pkt) > 3:
		ln = r16r(  int.from_bytes(pkt[:2],"little")   ,  pkt[3] % 7 + 1  ) ^ (config.NETXORKEY & 0xFFFF)
		ln = l16r(  ln,  pkt[2] % 7 + 1 )
		pkt[0] = ln & 0xFF
		pkt[1] = (ln & 0xFF00) >> 8

def parse_from(d):	
	if len(d) < 3:
		return None	
	p = Packet()
	p.tp = d[2]
	p.data = d[3:]
	return p

def formate_to(p):	
	d = bytearray(3) + p.data
	pktln = len(d) - 2
	
	d[0] = pktln & 0xFF
	d[1] = (pktln >> 8) & 0xFF
	d[2] = p.tp & 0xFF

	return d

def decrypt_from(d):
	if len(d) < 8:
		return None
	p = Packet()
	p.tp = r8r(d[2], d[3])
	hsh = int.from_bytes(d[3:7], "little")
	shift = hsh % 7 + 1
	
	tmp = bytearray(d[7:])
	
	mi = (len(d) - 7) // 4
	i = 0
	while(i < mi):
		a = r32r( int.from_bytes(tmp[i * 4: (i + 1) * 4], "little") ,  shift )
		tmp[i * 4 + 0] = a & 0xFF
		tmp[i * 4 + 1] = (a >> 8) & 0xFF
		tmp[i * 4 + 2] = (a >> 16) & 0xFF
		tmp[i * 4 + 3] = (a >> 24) & 0xFF
		i += 1
	
	of = mi * 4

	mi = (len(d) - 7) % 4
	i = 0
	while(i < mi):
		tmp[of + i] = r8r( tmp[of + i] ,  shift )
		i += 1
	
	if (sdbm(tmp) != hsh):
		return None
	
	p.tp ^= tmp[0]
	p.pktid = tmp[0] ^ (d[0] ^ d[1] ^ (config.NETXORKEY & 0xFF))
		
	if ( len(tmp) > 1 ):
		xor = ( tmp[0] | (tmp[0] << 8) | (tmp[0] << 16) | (tmp[0] << 24) ) ^ config.NETXORKEY
		mi = (len(tmp) - 1) // 4
		i = 0
		
		while (i < mi):
			tmp[1 + i * 4] ^= (xor & 0xFF)
			tmp[2 + i * 4] ^= ((xor >> 8) & 0xFF)
			tmp[3 + i * 4] ^= ((xor >> 16) & 0xFF)
			tmp[4 + i * 4] ^= ((xor >> 24) & 0xFF)
			xor = l32r(xor, 1)
			i += 1
		
		of = mi * 4 + 1
		
		mi = (len(tmp) - 1) % 4
		i = 0
		while (i < mi):
			tmp[of + i] ^= ( (xor >> (i * 8)) & 0xFF )
			i += 1
	
	p.data = tmp[1:]
	return p


def encrypt_pkt(p):
	if len(p.data) <= 0:
		return bytearray()
	
	d = bytearray(8) + p.data
	
	pktln = len(d) - 2
	
	d[0] = pktln & 0xFF
	d[1] = (pktln >> 8) & 0xFF
	d[2] = p.tp & 0xFF
	d[7] = p.pktid & 0xFF
	
	d[7] ^= d[1] ^ d[0] ^ (config.NETXORKEY & 0xFF)
	d[2] ^= d[7]
		
	xor = ( d[7] | (d[7] << 8) | (d[7] << 16) | (d[7] << 24) ) ^ config.NETXORKEY
	
	mi = (len(d) - 8) // 4
	i = 0
	
	while (i < mi):
		of = 8 + i * 4
		d[of + 0] ^= (xor & 0xFF)
		d[of + 1] ^= ((xor >> 8) & 0xFF)
		d[of + 2] ^= ((xor >> 16) & 0xFF)
		d[of + 3] ^= ((xor >> 24) & 0xFF)
		xor = l32r(xor, 1)
		i += 1
	
	of = mi * 4 + 8
	
	mi = (len(d) - 8) % 4
	i = 0
	while (i < mi):
		d[of + i] ^= ( (xor >> (i * 8)) & 0xFF )
		i += 1
	
	hsh = sdbm(d[7:])
	
	d[3] = hsh & 0xFF
	d[4] = (hsh >> 8) & 0xFF
	d[5] = (hsh >> 16) & 0xFF
	d[6] = (hsh >> 24) & 0xFF
	
	shift = hsh % 7 + 1
	
	mi = (len(d) - 7) // 4
	i = 0
	while(i < mi):
		of = 7 + i * 4
		a = l32r( int.from_bytes(d[of  :  of + 4], "little") ,  shift )
		d[of + 0] = a & 0xFF
		d[of + 1] = (a >> 8) & 0xFF
		d[of + 2] = (a >> 16) & 0xFF
		d[of + 3] = (a >> 24) & 0xFF
		i += 1
	
	of = mi * 4 + 7

	mi = (len(d) - 7) % 4
	i = 0
	while(i < mi):
		d[of + i] = l8r( d[of + i] ,  shift )
		i += 1
			
	d[2] = l8r(d[2], d[3])
	encrPktLen(d)
	
	return d


def sendOutBuf(outBuf, sock):
	sock.send( outBuf )
	del outBuf[:]

def placePkt(p, outBuf, sock, encr = False):
	d = None
	if encr:
		d = encrypt_pkt(p)
	else:
		d = formate_to(p)
	
	if len(outBuf) + len(d) > 8192:
		sendOutBuf(outBuf, sock)
	
	outBuf += d

def getPkt(inBuf,  encr = False):
	if len(inBuf) < 3:
		return None

	ln = 0
	if encr:
		ln = decrPktLen(inBuf)
	else:
		ln = int.from_bytes(inBuf[:2], "little") + 2
	
	if ln > len(inBuf) :
		return None
		
	p = None
	if encr:
		p = decrypt_from(inBuf[:ln])
	else:
		p = parse_from(inBuf[:ln])
	
	if p == None:
		return None
	
	del inBuf[:ln]
	
	return p