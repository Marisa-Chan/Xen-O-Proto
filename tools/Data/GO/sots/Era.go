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
	items []*TItem
	strm *os.File
	shift uint
}



func NewEra(filename string, not_shift bool)(*TEra) {
	var tmp = new(TEra)
	tmp.strm , _ = os.Open(filename)
	tmp.shift = 0
	
	//var fsz, _ = tmp.Strm.Seek(0, 2)
	tmp.strm.Seek(0x14, 0)
	
	var num = FreadLU32(tmp.strm)
	var off = FreadLU32(tmp.strm)
	
	var d, _ = Fread(tmp.strm, 4)
	
	if !not_shift {
		tmp.shift = uint(d[2])
	}
	
	tmp.strm.Seek(int64(off), 0)
	
	var t []byte
	
	if d[0] == 1 {
		var rd, _ = zlib.NewReader( tmp.strm )
		t, _ = ioutil.ReadAll( rd )
		rd.Close()
	} else {
		t, _ = ioutil.ReadAll( tmp.strm )
	}
	
	var s = bytes.NewReader(t)
	
	for i := 0; i < int(num); i++ {
		var iid = FreadLU32(s)
		var iof = FreadLU32(s)
		
		if iof != 0 && iof < off {
			tmp.items = append(tmp.items, &TItem{iid, iof, 0} )
		}
	}
	
	return tmp
}



func (t *TEra) ReadItem(itm *TItem) ([]byte) {
	t.strm.Seek(int64(itm.off), 0)
	var _ = FreadLU32(t.strm)
	var compsz = FreadLU32(t.strm)
	
	var d = make([]byte, compsz)
	if FreadU8(t.strm) == 1 {
		io.ReadFull(t.strm, d)
		
		var br = bytes.NewReader(d)
		var rd, _ = zlib.NewReader( br )
		d, _ = ioutil.ReadAll(rd)
		rd.Close()
	} else {
		io.ReadFull(t.strm, d)
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

func (t *TEra) Items() ([]*TItem) {
	return t.items
}