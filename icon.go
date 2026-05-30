package main

import (
	_ "embed"
)

// Embed icons
//go:embed icons/icon_red.png
var iconRed []byte

//go:embed icons/icon_blue.png
var iconBlue []byte

//go:embed icons/icon_green.png
var iconGreen []byte

func pngToIco(pngBytes []byte) []byte {
	size := len(pngBytes)
	ico := make([]byte, 22+size)
	
	// Icon Directory
	ico[0] = 0 // Reserved
	ico[1] = 0
	ico[2] = 1 // Type (1 = icon)
	ico[3] = 0
	ico[4] = 1 // Count (1 image)
	ico[5] = 0
	
	// Icon Directory Entry
	ico[6] = 0 // Width (0 = auto)
	ico[7] = 0 // Height
	ico[8] = 0 // Color count
	ico[9] = 0 // Reserved
	ico[10] = 1 // Planes
	ico[11] = 0
	ico[12] = 32 // Bit count
	ico[13] = 0
	
	// Bytes size
	ico[14] = byte(size & 0xFF)
	ico[15] = byte((size >> 8) & 0xFF)
	ico[16] = byte((size >> 16) & 0xFF)
	ico[17] = byte((size >> 24) & 0xFF)
	
	// Offset (value 22)
	ico[18] = 22
	ico[19] = 0
	ico[20] = 0
	ico[21] = 0
	
	copy(ico[22:], pngBytes)
	return ico
}

func initIcons() {
	iconRed = pngToIco(iconRed)
	iconBlue = pngToIco(iconBlue)
	iconGreen = pngToIco(iconGreen)
}
