#!/usr/bin/python3

import zlib
import sys
import os
import io

class TItem:
	def __init__(self, _id, _off, _arr = 0):
		self.ID = _id
		self.off = _off
		self.arr = _arr
	ID = 0
	off = 0
	arr = 0

class TEra:
	shift = 0
	items = None
	strm = None
	tabl = None
	
	def __init__(self, fpath, shifter = True):
		self.items = list()
		self.strm = open(fpath, "rb")
		
		self.strm.seek(0, 2)
		fsz = self.strm.tell()

		self.strm.seek(0x14)
		num = int.from_bytes( self.strm.read(4), byteorder="little" )
		off = int.from_bytes( self.strm.read(4), byteorder="little" )
		
		d = self.strm.read(4)
		
		if shifter:
			self.shift = d[2]
		
		self.strm.seek(off)

		t = None
		if (d[0] == 1):
			t = zlib.decompress(self.strm.read(fsz - off))
		else:
			t = self.strm.read(fsz - off)
			
		del d
		
		s = io.BytesIO(t)
		s.seek(0)
		
		i = 0
		while i < num:
			iid = int.from_bytes(s.read(4), byteorder = "little")
			iof = int.from_bytes(s.read(4), byteorder = "little")
			if iof < off and iof != 0:
				
				self.items.append( TItem(iid, iof) )
			
			i += 1
			
		del s
		del t
		
		self.strm.seek(0x1F)
		num2 = int.from_bytes( self.strm.read(4), byteorder="little" )
		off2 = int.from_bytes( self.strm.read(4), byteorder="little" )
		
		cc = self.strm.read(1)[0]
		
		if (num2 > 0 and off2 < fsz):
			self.strm.seek(off2)
			
			if cc == 1:
				self.tabl = zlib.decompress(self.strm.read(fsz - off2))
			else:
				self.tabl = self.strm.read(num2 * 8)
		
		
	
	def readItem(self, itm):
		self.strm.seek(itm.off)
		decsz = int.from_bytes(self.strm.read(4), byteorder = "little")
		compsz = int.from_bytes(self.strm.read(4), byteorder = "little")
		
		d = None
		
		if ( self.strm.read(1)[0] == 1):
			d = bytearray( zlib.decompress( self.strm.read(compsz) ) )
		else:
			d = bytearray( self.strm.read(compsz) )
		
		if (self.shift):
			shift = self.shift % 7 + 1
			i = 0
			while (i + 4) <= len(d):
				e = int.from_bytes(d[i: i + 4], "little")
				e = e >> shift | ((e << (32-shift)) & 0xFFFFFFFF)
				d[i] = e & 0xFF
				d[i + 1] = (e >> 8) & 0xFF
				d[i + 2] = (e >> 16) & 0xFF
				d[i + 3] = (e >> 24) & 0xFF
				i += 4
	
			while i < len(d):
				e = d[i]
				e = e >> shift | ((e << (8-shift)) & 0xFF)
				d[i] = e & 0xFF
				i += 1
		
		return d


class TDra:
	items = None
	strm = None
	
	def __init__(self, fpath):
		self.items = list()
		self.strm = open(fpath, "rb")
		
		self.strm.seek(0, 2)
		fsz = self.strm.tell()

		self.strm.seek(0x10)
		num = int.from_bytes( self.strm.read(4), byteorder="little" )
		
		self.strm.seek(1, 1)

		i = 0
		while i < num:
			iid = int.from_bytes(self.strm.read(4), byteorder = "little")
			iof = int.from_bytes(self.strm.read(4), byteorder = "little")
			
			if iof != 0:
				self.items.append( TItem(iid, iof) )
			
			i += 1
	
	def readItem(self, itm):
		self.strm.seek(itm.off + 4)
		decsz = int.from_bytes(self.strm.read(4), byteorder = "little")
		compsz = int.from_bytes(self.strm.read(4), byteorder = "little")
		
		d = None
		
		if ( self.strm.read(1)[0] == 1):
			d = bytearray( zlib.decompress( self.strm.read(compsz) ) )
		else:
			d = bytearray( self.strm.read(compsz) )
		
		return d


class TLst:
	arrs = 0
	lastarr = -1
	items = None
	strm = None
	path = ""
	
	def __init__(self, fpath):
		self.items = list()
		
		(hd,ext) = os.path.splitext(fpath)
		
		self.path = hd
		
		if (ext.upper() != ".LST"):
			fpath = hd + ".LST"
		
		strm = open(fpath, "rb")
		strm.seek(0x10)
		
		num = int.from_bytes( strm.read(4), byteorder="little" )

		self.arrs = strm.read(2)[1]
		
		i = 0
		while i < num:
			iid = int.from_bytes(strm.read(4), byteorder = "little")
			iof = int.from_bytes(strm.read(4), byteorder = "little")
			iar = strm.read(1)[0]
			
			self.items.append( TItem(iid, iof, iar) )
			
			i += 1
		
		strm.close()
	
	def readItem(self, itm):
		if (self.lastarr != itm.arr):
			if (self.strm):
				self.strm.close()
				
			pth = self.path
			
			if (itm.arr):
				pth += ".{:03x}".format(itm.arr)
			else:
				pth += ".DRA"
			
			self.strm = open(pth, "rb")
			self.lastarr = itm.arr
		
		self.strm.seek(itm.off + 4)
		decsz = int.from_bytes(self.strm.read(4), byteorder = "little")
		compsz = int.from_bytes(self.strm.read(4), byteorder = "little")
		
		d = None
		
		if ( self.strm.read(1)[0] == 1):
			d = bytearray( zlib.decompress( self.strm.read(compsz) ) )
		else:
			d = bytearray( self.strm.read(compsz) )
		
		return d


def main():
	if len(sys.argv) != 3:
		print("script.py  TYPE  Filename")
		print("TYPE = ERA | DRA | LST")
		print("")
		exit(-1)

	tp = sys.argv[1].upper()
	fl = sys.argv[2]
	
	arc = None
	if (tp == "DRA"):
		arc = TDra(fl)
	elif (tp == "ERA"):
		arc = TEra(fl)
	elif (tp == "LST"):
		arc = TLst(fl)
	else:
		print("Wrong type")
		exit(-1)
	
	outdir = "extract_" + os.path.basename(fl)

	if not (os.path.isdir(outdir)):
		os.mkdir(outdir)

	i = 0
	for elm in arc.items:
		print ("{}/{}".format(i + 1, len(arc.items)) )
		
		s = None
		if ( len(arc.items) > 10000):
			subdr = i // 2000
			
			if i % 2000 == 0:
				if not (os.path.isdir(outdir + "/" + str(subdr))):
					os.mkdir(outdir + "/" + str(subdr))
			s = open(outdir + "/" + str(subdr) + "/" + str(elm.ID) + ".raw", "wb")
		else:
			s = open(outdir + "/" + str(elm.ID) + ".raw", "wb")
		s.write( arc.readItem(elm) )
		s.close()
		i += 1
	
	if (tp == "ERA" and arc.tabl != None):
		t = open("extract_" + os.path.basename(fl) + ".table", "wb")
		t.write(arc.tabl)
		t.close()

if __name__ == "__main__":
	main()
