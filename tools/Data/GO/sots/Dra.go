package sots

import (
	"os"
	"compress/zlib"
	"io"
	"io/ioutil"
	"bytes"
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
	var _ = FreadLU32(t.strm)
	var compsz = FreadLU32(t.strm)

	var out = make([]byte, compsz)
	
	if FreadU8(t.strm) == 1 {
		io.ReadFull(t.strm, out)
		
		var br = bytes.NewReader(out)
		var rd, _ = zlib.NewReader( br )
		out, _ = ioutil.ReadAll(rd)
		rd.Close()
	} else {
		io.ReadFull(t.strm, out)
	}
		
	return out
}

func (t *TDra) Items() ([]*TItem) {
	return t.items
}