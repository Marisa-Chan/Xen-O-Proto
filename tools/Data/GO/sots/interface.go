package sots

type ARC interface {
	Items() []*TItem
	ReadItem(itm *TItem) []byte
}