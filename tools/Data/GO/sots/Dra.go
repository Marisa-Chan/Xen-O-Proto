package sots

import (
	"os"
	"compress/zlib"
	"io"
)

type TDra struct {
	Items []*TItem
	Strm *os.File
}

func NewDra(filename string)(*TDra) {
	var tmp = new(TDra)
	tmp.Strm , _ = os.Open(filename)
	
	tmp.Strm.Seek(0x10, 0)
	
	var num = FreadLU32(tmp.Strm)
	
	tmp.Strm.Seek(1, 1)
	
	for i := 0; i < int(num); i++ {
		var iid = FreadLU32(tmp.Strm)
		var iof = FreadLU32(tmp.Strm)
		
		if iof != 0 {
			tmp.Items = append(tmp.Items, &TItem{iid, iof, 0} )
		}
	}
		
	return tmp
}

func (t *TDra) ReadItem(itm *TItem) ([]byte) {
	t.Strm.Seek(int64(itm.off) + 4, 0)
	var decsz = FreadLU32(t.Strm)
	var _ = FreadLU32(t.Strm) //compsz

	var out = make([]byte, decsz)
	
	if FreadU8(t.Strm) == 1 {
		var rd, _ = zlib.NewReader( t.Strm )
		io.ReadFull(rd, out)
		rd.Close()
	} else {
		t.Strm.Read(out)
	}
		
	return out
}