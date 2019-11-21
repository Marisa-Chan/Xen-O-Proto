package sots

import (
	"os"
	"compress/zlib"
	"io"
)

type TDra struct {
	items []*TItem
	strm *os.File
}

func NewDra(filename string)(*TDra) {
	var tmp = new(TDra)
	tmp.strm , _ = os.Open(filename)
	
	tmp.strm.Seek(0x10, 0)
	
	var num = FreadLU32(tmp.strm)
	
	tmp.strm.Seek(1, 1)
	
	for i := 0; i < int(num); i++ {
		var iid = FreadLU32(tmp.strm)
		var iof = FreadLU32(tmp.strm)
		
		if iof != 0 {
			tmp.items = append(tmp.items, &TItem{iid, iof, 0} )
		}
	}
		
	return tmp
}

func (t *TDra) ReadItem(itm *TItem) ([]byte) {
	t.strm.Seek(int64(itm.off) + 4, 0)
	var decsz = FreadLU32(t.strm)
	var _ = FreadLU32(t.strm) //compsz

	var out = make([]byte, decsz)
	
	if FreadU8(t.strm) == 1 {
		var rd, _ = zlib.NewReader( t.strm )
		io.ReadFull(rd, out)
		rd.Close()
	} else {
		t.strm.Read(out)
	}
		
	return out
}

func (t *TDra) Items() ([]*TItem) {
	return t.items
}