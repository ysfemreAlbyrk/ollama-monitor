//go:build windows

package main

import (
	"os"
	"path/filepath"

	"golang.org/x/sys/windows/registry"
)

func toggleStartup(enable bool) error {
	k, err := registry.OpenKey(registry.CURRENT_USER, `Software\Microsoft\Windows\CurrentVersion\Run`, registry.QUERY_VALUE|registry.SET_VALUE)
	if err != nil {
		return err
	}
	defer k.Close()

	if enable {
		execPath, err := os.Executable()
		if err != nil {
			return err
		}
		absPath, err := filepath.Abs(execPath)
		if err != nil {
			return err
		}
		appLogger.Printf("Enabling startup: %s", absPath)
		return k.SetStringValue(AppName, absPath)
	} else {
		appLogger.Println("Disabling startup")
		_ = k.DeleteValue(AppName)
		return nil
	}
}
