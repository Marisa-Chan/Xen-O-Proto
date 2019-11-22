package sots

import (
	"fmt"
	"os"
	"compress/zlib"
	"io"
	"io/ioutil"
	"bytes"
	"path"
)


type TLst struct {
	arrs int
	lastarr int
	items []*TItem
	strm *os.File
	path string
}



func NewLst(filepath string)(*TLst) {
	var tmp = new(TLst)
	tmp.arrs = 0
	tmp.lastarr = -1
	tmp.path = ""
	tmp.strm = nil
	
	var ext = path.Ext(filepath)
	tmp.path = filepath[:len(filepath) - len(ext)]
	
	var strm, _ = os.Open(tmp.path + ".LST")
	
	strm.Seek(0x10, 0)
	var num = FreadLU32(strm)	
	
	strm.Seek(1, 1)
	tmp.arrs = int( FreadU8(strm) )
	
	for i := 0; i < int(num); i++ {
		var iid = FreadLU32(strm)
		var iof = FreadLU32(strm)
		var iar = FreadU8(strm)
		
		tmp.items = append(tmp.items, &TItem{iid, iof, int(iar)} )
	}
	
	strm.Close()
	return tmp
}


func (t *TLst) ReadItem(itm *TItem) ([]byte) {

	if t.lastarr != itm.arr {
		if t.strm != nil {
			t.strm.Close()
		}
		
		var pth string
		
		if itm.arr != 0 {
			pth = fmt.Sprintf("%s.%03x", t.path, itm.arr)
		} else {
			pth = fmt.Sprintf("%s.DRA", t.path)
		}
		
		t.strm, _ = os.Open(pth)
		t.lastarr = itm.arr
	}
	
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


func (t *TLst) Items() ([]*TItem) {
	return t.items
}
