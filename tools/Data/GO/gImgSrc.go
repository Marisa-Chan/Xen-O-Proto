package main

import (
	"os"
	"path"
	"fmt"
	"image/png"
	"./sots"
)


func main() {
	if len(os.Args) != 2 {
		fmt.Println("Usage: " + os.Args[0] + " GImgSrc.ERA")
		fmt.Println("")
		os.Exit(-1)
	}

	var fl = os.Args[1]
	
	var _,flname = path.Split(fl)
	var ext = path.Ext(flname)
	flname = flname[:len(flname) - len(ext)]
	
	var outdir = "extract_" + flname

	if _, err := os.Stat(outdir); os.IsNotExist(err) {
		os.Mkdir(outdir, os.ModePerm)
	}
	
	var arc = sots.NewEra(fl, true)

	var num = len(arc.Items())
	for i,elm := range arc.Items() {		
		var s *os.File
		if ( num > 10000){
			var opath = fmt.Sprintf("%s/%d", outdir, i / 2000)
			
			if i % 2000 == 0 {
				if _, err := os.Stat(opath); os.IsNotExist(err) {
					os.Mkdir(opath, os.ModePerm)
				}
			}
			s,_ = os.Create(fmt.Sprintf("%s/%d.png", opath, elm.ID))
		} else {
			s,_ = os.Create(fmt.Sprintf("%s/%d.png", outdir, elm.ID))
		}
		
		var img = sots.GetImageType3( arc.ReadItem(elm) )
		png.Encode(s, img)
		s.Close()
		
		fmt.Printf("%d/%d\n", i + 1, num)
	}
}