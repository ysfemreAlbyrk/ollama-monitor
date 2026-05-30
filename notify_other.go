//go:build !windows

package main

import (
	"github.com/gen2brain/beeep"
)

func registerAUMID() {
	// Only needed on Windows
}

func sendNotification(title, message string) {
	_ = beeep.Notify(title, message, "")
}
