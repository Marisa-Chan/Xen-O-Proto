package main

import (
	"os"
	"path"
	"fmt"
	"strings"
	"./sots"
)


func main() {
	if len(os.Args) != 3 {
		fmt.Println("extract  TYPE  Filename")
		fmt.Println("TYPE = ERA | DRA | LST")
		fmt.Println("")
		os.Exit(-1)
	}

	var tp = strings.ToUpper(os.Args[1])
	var fl = os.Args[2]
	
	var arc sots.ARC = nil
	switch(tp) {
	case "DRA":
		arc = sots.NewDra(fl)
	case "ERA":
		arc = sots.NewEra(fl, false)
	case "LST":
		arc = sots.NewLst(fl)
	default:
		fmt.Println("Wrong type")
		os.Exit(-1)
	}
	
	var _,flname = path.Split(fl)
	var outdir = "extract_" + flname

	if _, err := os.Stat(outdir); os.IsNotExist(err) {
		os.Mkdir(outdir, os.ModePerm)
	}

	var num = len(arc.Items())
	for i,elm := range arc.Items() {
		fmt.Printf("%d/%d\n", i + 1, num)
		
		var s *os.File
		if ( num > 10000){
			var opath = fmt.Sprintf("%s/%d", outdir, i / 2000)
			
			if i % 2000 == 0 {
				if _, err := os.Stat(opath); os.IsNotExist(err) {
					os.Mkdir(opath, os.ModePerm)
				}
			}
			s,_ = os.Create(fmt.Sprintf("%s/%d.raw", opath, elm.ID))
		} else {
			s,_ = os.Create(fmt.Sprintf("%s/%d.raw", outdir, elm.ID))
		}
		s.Write( arc.ReadItem(elm) )
		s.Close()
	}
}