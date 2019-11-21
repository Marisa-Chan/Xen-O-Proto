package main

import (
	"fmt"
	"os"
	"encoding/binary"
	"./sots"
	"image/png"
)

type bdid struct {
	bodyID  uint32
	bid     uint32
	frameID uint32
}

func makeNPC_BodyList(eye int, state int) []*bdid {
	var arc = sots.NewEra( "GNBFC.XBD", false )

	var items []*bdid
	
	for _, elm := range arc.Items() {
		if (elm.ID & 0xE0) == uint32( (eye << 5) | (state & 0x1F) ) {
			var itmInf = arc.ReadItem(elm)
			var t = new(bdid)
			t.bodyID = (elm.ID >> 8) & 0xFFFF
			t.bid = binary.LittleEndian.Uint32(itmInf[:4])
			
			items = append(items, t)
		}
	}

	return items
}

func makeFrameIDS(st []*bdid, frame int) {
	var arc = sots.NewDra( "GNBID.DRA" )
	for _, elm := range arc.Items() {
		for _, n := range st {
			if elm.ID == n.bid {
				var mm = arc.ReadItem(elm)
				
				if frame < int(mm[0]) {
					n.frameID = uint32( binary.LittleEndian.Uint32( mm[1 + frame * 4  :  1 + frame * 4 + 4] ) )
				} else {
					n.frameID = uint32( binary.LittleEndian.Uint32( mm[1:5] ) )
				}
			}
		}
	}
}

func main() {
	var nm = "GNBMP"
	var d = makeNPC_BodyList(6, 0)
	makeFrameIDS(d, 0)

	var arc = sots.NewLst( nm )

	var outDIR = "NPC_help"

	var jj = 0
	var num = len(d)
	
	if _, err := os.Stat(outDIR); os.IsNotExist(err) {
		os.Mkdir(outDIR, os.ModePerm)
	}
	
	for _,elm := range arc.Items() {
		var i *bdid = nil
	
		for idx,n := range d {
			if (n.frameID == elm.ID) {
				i = n
				
				//Delete it from d
				d[idx] = d[len(d)-1]
				d = d[:len(d)-1]
				break
			}
		}
	
		if i == nil {
			continue
		}
		
		var img = sots.GetImageType1( arc.ReadItem(elm) )
		
		var outF,_ = os.Create( fmt.Sprintf("%s/%d.png", outDIR, i.bodyID) )
		png.Encode(outF, img)
		outF.Close()
		
		jj++
		
		fmt.Printf("%d/%d\n",jj, num)
	}

}