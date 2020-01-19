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
	filename string
	hdrCompr bool
}



func NewEra(filename string, not_shift bool)(*TEra) {
	var tmp = new(TEra)
	tmp.filename = filename
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
		tmp.hdrCompr = true
	} else {
		t, _ = ioutil.ReadAll( tmp.strm )
		tmp.hdrCompr = false
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


func (t *TEra) eraGenItem(itm []byte, compr bool) []byte {
	d := make([]byte, len(itm))
	copy(d, itm)
	if t.shift != 0 {
		var shift = t.shift % 7 + 1
		
		var i = 0
		for i + 4 < len(d) {
			var e = binary.LittleEndian.Uint32( d[i : i + 4] )
			e = (e << shift | (e >> (32 - shift))) & 0xFFFFFFFF
			d[i]	 = byte(e & 0xFF)
			d[i + 1] = byte((e >> 8) & 0xFF)
			d[i + 2] = byte((e >> 16) & 0xFF)
			d[i + 3] = byte((e >> 24) & 0xFF)
			i += 4
		}
		
		for i < len(d) {
			var e = d[i]
			e = (e << shift | (e >> (8-shift))) & 0xFF
			d[i] = e & 0xFF
			i ++
		}
	}
	
	var g bytes.Buffer
	if compr {
		var z bytes.Buffer
		w := zlib.NewWriter(&z)
		w.Write(d)
		w.Close()
		
		g.Write(fastGetBtLU32(uint32(len(itm))))
		g.Write(fastGetBtLU32(uint32(z.Len())))
		g.WriteByte(1)
		
		g.Write(z.Bytes())
	} else {
		g.Write(fastGetBtLU32(uint32(len(itm))))
		g.Write(fastGetBtLU32(uint32(len(d))))
		g.WriteByte(0)
		g.Write(d)
	}
	
	return g.Bytes()	
}

func (t *TEra) eraGenFileTable() []byte {
	var lst bytes.Buffer
	for _,elm := range t.items {
		lst.Write( fastGetBtLU32( uint32(elm.ID) ) )
		lst.Write( fastGetBtLU32( uint32(elm.off) ) )
	}
	
	if t.hdrCompr == true {
		var c bytes.Buffer
		z := zlib.NewWriter(&c)
		z.Write(lst.Bytes())
		z.Close()
		return c.Bytes()
	} else {
		return lst.Bytes()
	}
}

func (t *TEra) AddItem(itm []byte, compr bool) uint32 {
	t.strm.Close()
	t.strm, _ = os.OpenFile(t.filename, os.O_RDWR, 0644)
	
	var newID uint32 = 0
	
	/** Find where files ends
	    Can be used file-table offset, but better find it **/
	var maxOff uint32 = 0
	for _,elm := range t.items {
		t.strm.Seek(int64(elm.off), 0)
		var _ = FreadLU32(t.strm)
		var compsz = FreadLU32(t.strm)

		if (elm.off + compsz + 9) > maxOff {
			maxOff = (elm.off + compsz + 9)
		}
		if (elm.ID > newID) {
			newID = elm.ID
		}
	}
	
	var newItm = TItem{newID + 1, maxOff, 0}
	t.items = append(t.items, &newItm )
	
	t.strm.Seek(int64(maxOff), 0)
	
	//Write new item
	eItm := t.eraGenItem(itm, compr)
	t.strm.Write(eItm)
	
	var hdrPos = maxOff + uint32(len(eItm))
	
	//Write new file table
	eHdr := t.eraGenFileTable()
	t.strm.Write(eHdr)
	
	//Fix pointer + number of files
	t.strm.Seek(0x14, 0)
	
	t.strm.Write( fastGetBtLU32( uint32(len(t.items)) ) )
	t.strm.Write( fastGetBtLU32( uint32(hdrPos) ) )
	
	t.strm.Close()
	t.strm , _ = os.Open(t.filename)
	
	return newItm.ID
}

func (t *TEra) Items() ([]*TItem) {
	return t.items
}