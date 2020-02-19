#!/usr/bin/python3

import zlib
import sys
import os
import io
import re

class fil:
	f = ""
	i = 0

def shiftdata(d, shft):
	shift = shft % 7 + 1
	i = 0
	while (i + 4) <= len(d):
		e = int.from_bytes(d[i: i + 4], "little")
		e = e >> (32-shift) | ((e << (shift)) & 0xFFFFFFFF)
		d[i] = e & 0xFF
		d[i + 1] = (e >> 8) & 0xFF
		d[i + 2] = (e >> 16) & 0xFF
		d[i + 3] = (e >> 24) & 0xFF
		i += 4

	while i < len(d):
		e = d[i]
		e = e >> (8-shift) | ((e << (shift)) & 0xFF)
		d[i] = e & 0xFF
		i += 1
	

def main():
	if len(sys.argv) < 2:
		print("script.py [-opt=xxx ...] Dir")
		print("options:")
		print("o | out | output - output archive file (default out.era)")
		print("s | shift - shift value \"encryption\" (0-6) ")
		print("clist - compress content list (0,1)")
		print("cfiles - compress files (0,1)")
		print("cp | cpage | codepage - codepage of text (default 437)")
		print("l | lvl | level - compression level (0-9,-1  default -1)")
		print("tbl - additional ID-ID table file")
		print("ctbl - compress ID-ID table (0,1)")
		print("")
		print("Example: script.py -o=out.era -s=4 -clist=1 /dir/with/files")
		print("")
		exit(-1)
	
	output = "out.era"
	shift = 1
	clist = 1
	cfiles = 1
	codepage = 437
	level = -1
	indir = ""
	idtable = ""
	ctbl = 1
	dr = None
	
	rg = re.compile("-(.+)=(.+)")
	
	for f in sys.argv[1:]:
		match = rg.match(f)
		if (match):
			op = match.group(1)
			val = match.group(2)
			if (op == "o" or op == "out" or op == "output"):
				output=val
			elif (op == "s" or op == "shift"):
				shift=int(val)
			elif (op == "clist"):
				clist = int(val)
				if (clist != 0):
					clist = 1
			elif (op == "cfiles"):
				cfiles = int(val)
				if (cfiles != 0):
					cfiles = 1
			elif (op == "codepage" or op == "cpage" or op == "cp"):
				codepage = int(val)
			elif (op == "tbl"):
				idtable = val
			elif (op == "ctbl"):
				ctbl = int(val)
				if (ctbl != 0):
					ctbl = 1
			elif (op == "l" or op == "lvl" or op == "level"):
				level = int(val)
				if level < -1 or level > 9:
					level = -1			
		elif os.path.isdir(f):
			indir = f
	
	if (indir == ""):
		print("No input dir")
		exit(-1)
	
	print("Output: " + output)
	print("Shift: " + str(shift))
	print("Compress files list: " + str(clist))
	print("Compress files: " + str(cfiles))
	print("Codepage: " + str(codepage))
	print("Compress level: " + str(level))
	print("Input dir : " + indir)
	
	entries = os.listdir(indir)
	files = list()
	
	for f in entries:
		fnm = re.sub('[^0-9]','', f)
		if os.path.isfile(indir + "/" + f) and fnm != "":
			t = fil()
			t.f = f
			t.i = int(fnm)
			files.append(t)

	files.sort(key=lambda t: t.i)
	
	num = len(files)
	
	hdr = bytearray()
	
	hdr += "XENONLINE   ".encode("ascii")
	hdr += b"\x11\x10\x06\x20" #0xC
	hdr += codepage.to_bytes(4, byteorder = "little") #0x10
	hdr += num.to_bytes(4, byteorder = "little") #0x14
	hdr += (0).to_bytes(4, byteorder = "little") #0x18  offset
	hdr += clist.to_bytes(2, byteorder = "little") #0x1C
	hdr += shift.to_bytes(2, byteorder = "little") #0x1E
	hdr += bytearray(0x14) #0x20
	
	
	outfile = open(output, "wb")
	outfile.write(hdr)
	
	contlst = bytearray()
	
	for f in files:
		print("\tadding : " + f.f)
		contlst += ( f.i ).to_bytes(4, byteorder = "little")
		contlst += ( outfile.tell() ).to_bytes(4, byteorder = "little")
		
		fl = open(indir + "/" + f.f, "rb")
		pp = bytearray(fl.read())
		fl.close()
		
		decsz = len(pp)
		
		if (shift):
			shiftdata(pp, shift)
		
		if (cfiles != 0):
			pp = zlib.compress(pp, level=level)
		
		outfile.write( decsz.to_bytes(4, byteorder = "little") )
		outfile.write( (len(pp)).to_bytes(4, byteorder = "little") )
		outfile.write( (cfiles).to_bytes(1, byteorder = "little") )
		outfile.write( pp )
	
	contoff = outfile.tell()
		
	if (clist != 0):
		contlst = zlib.compress(contlst, level=level)
	
	outfile.write( contlst )
		
	outfile.seek(0x18)
	outfile.write( contoff.to_bytes(4, byteorder = "little") )
	
	if (idtable != ""):
		print("Adding:", idtable)
		tbf = open(idtable, "rb")
		t = tbf.read()
		tbf.close()
		if (len(t) > 0 and ((len(t) & 7) == 0)):
			tnum = len(t) // 8
			
			if (ctbl != 0):
				t = zlib.compress(t, level=level)
			
			outfile.seek(0, 2)
			tbl2off = outfile.tell()
			
			outfile.write(t)
			outfile.seek(0x1F)
			outfile.write( tnum.to_bytes(4, byteorder = "little") )
			outfile.write( tbl2off.to_bytes(4, byteorder = "little") )
			outfile.write( ctbl.to_bytes(1, byteorder = "little") )
		else:
			print("Invalid size, not mod of 8")
	
	
	outfile.close()
			
	


if __name__ == "__main__":
	main()
