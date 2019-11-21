package sots

import (
	"encoding/binary"
	"image"
	"image/color"
)


func GetImageType1(itm []byte) image.Image {
	var w = int( binary.LittleEndian.Uint16(itm[0:2]) )
	var h = int( binary.LittleEndian.Uint16(itm[2:4]) )

	var img = image.NewNRGBA( image.Rect(0, 0, w, h) )

	var xpages = (w + 0xFF) >> 8
	var ypages = (h + 0xFF) >> 8

	var pxid = 0
	
	for xpg := 0; xpg < xpages; xpg++ {
		var pw, ph int
		
		if xpg == xpages - 1 {
			pw = w & 0xFF
		} else {
			pw = 0x100
		}

		for ypg := 0; ypg < ypages; ypg++ {
		
			if ypg == ypages - 1 {
				ph = h & 0xFF
			} else {
				ph = 0x100
			}

			for y := 0; y < ph; y++ {
				for x := 0; x < pw; x++ {

					var t = int(  itm[8 + (pxid + (y * pw + x)) * 2 + 1]  )
					var r = uint8(  ((t & 0xF0) >> 4) * 17  )
					var g = uint8(  (t & 0xF) * 17  )

					    t = int(  itm[8 + (pxid + (y * pw + x)) * 2]  )
					var b = uint8(  ((t & 0xF0) >> 4) * 17  )
					var aa = uint8(   (t & 0xF) * 17  )

					img.SetNRGBA( (xpg << 8) + x, (ypg << 8) + y, color.NRGBA{r, g, b, aa} )
				}
			}

			pxid += pw * ph
		}
	}
	
	return img
}