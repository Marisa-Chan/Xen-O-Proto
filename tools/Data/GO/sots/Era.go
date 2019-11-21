package sots

import (
	"os"
	"encoding/binary"
	"compress/zlib"
	"io"
	"io/ioutil"
	"bytes"
)

type TEra struct {
	Items []*TItem
	Strm *os.File
	shift uint
}



func NewEra(filename string, not_shift bool)(*TEra) {
	var tmp = new(TEra)
	tmp.Strm , _ = os.Open(filename)
	tmp.shift = 0
	
	//var fsz, _ = tmp.Strm.Seek(0, 2)
	tmp.Strm.Seek(0x14, 0)
	
	var num = FreadLU32(tmp.Strm)
	var off = FreadLU32(tmp.Strm)
	
	var d, _ = Fread(tmp.Strm, 4)
	
	if !not_shift {
		tmp.shift = uint(d[2])
	}
	
	tmp.Strm.Seek(int64(off), 0)
	
	var t []byte
	
	if d[0] == 1 {
		var rd, _ = zlib.NewReader( tmp.Strm )
		t, _ = ioutil.ReadAll( rd )
		rd.Close()
	} else {
		t, _ = ioutil.ReadAll( tmp.Strm )
	}
	
	var s = bytes.NewReader(t)
	
	for i := 0; i < int(num); i++ {
		var iid = FreadLU32(s)
		var iof = FreadLU32(s)
		
		if iof != 0 && iof < off {
			tmp.Items = append(tmp.Items, &TItem{iid, iof, 0} )
		}
	}
	
	return tmp
}



func (t *TEra) ReadItem(itm *TItem) ([]byte) {
	t.Strm.Seek(int64(itm.off), 0)
	var decsz = FreadLU32(t.Strm)
	var _ = FreadLU32(t.Strm) //compsz
	
	var d = make([]byte, decsz)
	if FreadU8(t.Strm) == 1 {
		var rd, _ = zlib.NewReader( t.Strm )
		io.ReadFull(rd, d)
		rd.Close()
	} else {
		t.Strm.Read(d)
	}
	
	if t.shift != 0 {
		var shift = t.shift % 7 + 1
		
		var i = 0
		for i + 4 < len(d) {
			var e = binary.LittleEndian.Uint32( d[i : i + 4] )
			e = e >> shift | ((e << (32 - shift)) & 0xFFFFFFFF)
			d[i]	 = byte(e & 0xFF)
			d[i + 1] = byte((e >> 8) & 0xFF)
			d[i + 2] = byte((e >> 16) & 0xFF)
			d[i + 3] = byte((e >> 24) & 0xFF)
			i += 4
		}
		
		for i < len(d) {
			var e = d[i]
			e = e >> shift | ((e << (8-shift)) & 0xFF)
			d[i] = e & 0xFF
			i ++
		}
	}
	
	return d
}
