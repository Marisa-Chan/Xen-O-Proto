package sots

import (
	"encoding/binary"
	"image"
	"image/color"
)

//*BMP
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

func pow2close(a int) int{
	if a >= 1024 {
		return 512
	}
	
	var tmp uint = 1
	for tmp < uint(a) {
		tmp <<= 1
	}
	
	if tmp != uint(a) {
		return int(tmp >> 1)
	}
	return int(tmp)
}

func decodeImage(itm []byte, w,h,tp,parts int) image.Image {

	var img = image.NewNRGBA( image.Rect(0, 0, w, h) )

	var wrkw = w
	var wrkh = h

	var pxid = 0
	var partN = 0
	var xx = 0
	var yy = 0
	
	for wrkw > 0 {
		var pw = pow2close(wrkw)
		if pw == 0 {
			pw = 1
		}
		
		for wrkh > 0 {
			var ph = pow2close(wrkh)
			if ph == 0 {
				ph = 1
			}
			
			for ty := 0; ty < ph; ty++ {
				for tx := 0; tx < pw; tx++ {
					var cr,cg,cb,ca uint8
					switch(tp) {
					case 7:
						cb = itm[pxid]
						cg = itm[pxid + 1]
						cr = itm[pxid + 2]
						ca = itm[pxid + 3]
						pxid += 4
					case 0:
						ca = (itm[pxid] & 0xF) * 17
						cb = ((itm[pxid] >> 4) & 0xF) * 17
						cg = (itm[pxid + 1] & 0xF) * 17
						cr = ((itm[pxid + 1] >> 4) & 0xF) * 17
						pxid += 2
					case 1:
						var clr = uint ( binary.LittleEndian.Uint16(itm[pxid : pxid + 2]) )
						ca = uint8((clr & 1) * 0xFF)
						cb = uint8( float32((clr >> 1) & 0x1F) * 8.23)
						cg = uint8( float32((clr >> 6) & 0x1F) * 8.23)
						cr = uint8( float32((clr >> 11) & 0x1F) * 8.23)
						pxid += 2
					case 2:
						cr = itm[pxid]
						cg = itm[pxid + 1]
						cb = itm[pxid + 2]
						ca = itm[pxid + 3]
						pxid += 4
					case 5:
						cb = (itm[pxid] & 0xF) * 17
						cg = ((itm[pxid] >> 4) & 0xF) * 17
						cr = (itm[pxid + 1] & 0xF) * 17
						ca = ((itm[pxid + 1] >> 4) & 0xF) * 17
						pxid += 2
					default:
						cr = 0
						cg = 0
						cb = 0
						ca = 0
					}
										
					img.SetNRGBA( xx + tx, yy + ty, color.NRGBA{cr, cg, cb, ca} )
				}
			}
			
			partN++
			
			if partN >= parts {
				break
			}
			
			yy += ph
			wrkh -= ph
		}
		
		if partN >= parts {
			break
		}
		
		xx += pw
		wrkw -= pw
		
		yy = 0
		wrkh = h
	}
	
	return img
}

//TEXC
func GetImageType2(itm []byte) image.Image {
	var w = int( binary.LittleEndian.Uint16(itm[0:2]) )
	var h = int( binary.LittleEndian.Uint16(itm[2:4]) )
	var tp = int(itm[4])
	var parts = int(itm[7])
	
	return decodeImage(itm[8:], w, h, tp, parts)
}

//GImgSrc
func GetImageType3(itm []byte) image.Image {
	var w = int( binary.LittleEndian.Uint16(itm[4:6]) )
	var h = int( binary.LittleEndian.Uint16(itm[6:8]) )
	var tp = int(binary.LittleEndian.Uint16(itm[0:2]))
	var parts = int(binary.LittleEndian.Uint16(itm[2:4]))
	
	return decodeImage(itm[8:], w, h, tp, parts)
}

//GSkill GItem
func GetImageIcon(itm []byte) image.Image {
	var w = int( binary.LittleEndian.Uint16(itm[0:2]) )
	var h = int( binary.LittleEndian.Uint16(itm[2:4]) )
	
	return decodeImage(itm[8:], w, h, 0, 1)
}




func encodeImage(img image.Image, mode int) ([]byte, int) {
	var w int = img.Bounds().Dx()
	var h int = img.Bounds().Dy()
	var itm []byte
	var pos image.Point
	var parts int = 0
	
	for w > 0 {
		var dx = pow2close(w)
		pos.Y = 0
		
		for _h := h; _h > 0;{
			var dy = pow2close(_h)
			
			
			for wy := pos.Y; wy < pos.Y + dy; wy++ {
				for wx := pos.X; wx < pos.X + dx; wx++ {
					pixel := img.At(wx, wy)				
					clr := color.NRGBAModel.Convert(pixel).(color.NRGBA)
					switch(mode) {
					case 7:
						itm = append(itm, uint8(clr.B))
						itm = append(itm, uint8(clr.G))
						itm = append(itm, uint8(clr.R))
						itm = append(itm, uint8(clr.A))
					case 0:
						itm = append(itm, uint8( (clr.A / 17) | ((clr.B / 17) << 4) ) )
						itm = append(itm, uint8( (clr.G / 17) | ((clr.R / 17) << 4) ) )					
					case 1:
						var c uint16 = ((uint16(float32(clr.B) / 8.23) & 0x1F) << 1) |
						               ((uint16(float32(clr.G) / 8.23) & 0x1F) << 6) |
									   ((uint16(float32(clr.R) / 8.23) & 0x1F) << 11)
						
						if clr.A > 178 {
							c |= 1
						}
						
						itm = append(itm, uint8( c & 0xFF ) )
						itm = append(itm, uint8( (c >> 8) & 0xFF ) )
												
					case 2:
						itm = append(itm, uint8(clr.R))
						itm = append(itm, uint8(clr.G))
						itm = append(itm, uint8(clr.B))
						itm = append(itm, uint8(clr.A))
						
					case 5:
						itm = append(itm, uint8( (clr.B / 17) | ((clr.G / 17) << 4) ) )
						itm = append(itm, uint8( (clr.R / 17) | ((clr.A / 17) << 4) ) )	
						
					default:
						
					}
				}
			}
			
			parts++
			
			pos.Y += dy
			_h -= dy
		}
		
		pos.X += dx
		w -= dx
	}
	return itm, parts
}


func MakeImageType3(img image.Image, mode int) []byte {
	var tmp []byte = fastGetBtLU16(mode)
	
	itm, parts := encodeImage(img, mode)
	
	tmp = append(tmp, fastGetBtLU16(parts)...)
	tmp = append(tmp, fastGetBtLU16(img.Bounds().Dx())...)
	tmp = append(tmp, fastGetBtLU16(img.Bounds().Dy())...)
	tmp = append(tmp, itm...)
	return tmp
}