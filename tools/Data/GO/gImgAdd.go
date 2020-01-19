package main

import (
	"os"
	"fmt"
	"strconv"
	"image"
	_ "image/png" //register png
	_ "image/jpeg" //register jpeg
	"./sots"
)

func main() {
	if len(os.Args) < 3 {
		fmt.Println("gImgAdd gImgSrc.era image.(png|jpg) [Mode]")
		fmt.Println("Mode:")
		fmt.Println("\t0 - RGBA4444")
		fmt.Println("\t1 - ARGB1555")
		fmt.Println("\t2 - ABGR8888")
		fmt.Println("\t5 - ARGB4444")
		fmt.Println("\t7 - ARGB8888")
		os.Exit(-1)
	}
	
	var mode int = 7
	
	if len(os.Args) > 3 {
		mode, _ = strconv.Atoi(os.Args[3])
	}
	
	infile, _ := os.Open(os.Args[2])
    img, _, _ := image.Decode(infile)
	infile.Close()
	
	itm := sots.MakeImageType3(img, mode)

	var arc = sots.NewEra(os.Args[1], true)
	var newID = arc.AddItem(itm, true)
	fmt.Printf("New item ID is %d (0x%X)\n", newID, newID)
}