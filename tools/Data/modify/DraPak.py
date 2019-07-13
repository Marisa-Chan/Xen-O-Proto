#!/usr/bin/python3

import zlib
import sys
import os
import io
import re

class fil:
	f = ""
	i = 0	

def main():
	if len(sys.argv) < 2:
		print("script.py [-opt=xxx ...] Dir")
		print("options:")
		print("o | out | output - output archive file (default out.dra)")
		print("cfiles - compress files (0,1)")
		print("l | lvl | level - compression level (0-9,-1  default -1)")
		print("")
		print("Example: script.py -o=out.dra /dir/with/files")
		print("")
		exit(-1)
	
	output = "out.dra"
	cfiles = 1
	level = -1
	indir = ""
	dr = None
	
	rg = re.compile("-(.+)=(.+)")
	
	for f in sys.argv[1:]:
		match = rg.match(f)
		if (match):
			op = match.group(1)
			val = match.group(2)
			if (op == "o" or op == "out" or op == "output"):
				output=val
			elif (op == "cfiles"):
				cfiles = int(val)
				if (cfiles != 0):
					cfiles = 1	
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
	print("Compress files: " + str(cfiles))
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
	
	hdr += "XENONLINE  DRA  ".encode("ascii")
	hdr += num.to_bytes(4, byteorder = "little") #0x10
	hdr += (0).to_bytes(1, byteorder = "little") #0x14	
	
	outfile = open(output, "wb")
	outfile.write(hdr)
	outfile.write( bytearray(num * 8) ) ##dummy file list
	
	contlst = bytearray()
	
	for f in files:
		print("\tadding : " + f.f)
		contlst += ( f.i ).to_bytes(4, byteorder = "little")
		contlst += ( outfile.tell() ).to_bytes(4, byteorder = "little")
		
		fl = open(indir + "/" + f.f, "rb")
		pp = bytearray(fl.read())
		fl.close()
		
		decsz = len(pp)
		
		if (cfiles != 0):
			pp = zlib.compress(pp, level=level)
		
		outfile.write( (f.i).to_bytes(4, byteorder = "little") ) ##it's dummy and not used but we will write index
		outfile.write( decsz.to_bytes(4, byteorder = "little") )
		outfile.write( (len(pp)).to_bytes(4, byteorder = "little") )
		outfile.write( (cfiles).to_bytes(1, byteorder = "little") )
		outfile.write( pp )
	
	outfile.seek(0x15)
	outfile.write( contlst )
	
	outfile.close()
			
	


if __name__ == "__main__":
	main()
