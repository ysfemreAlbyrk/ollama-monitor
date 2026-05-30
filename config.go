package main

import (
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
)

// Settings structure
type Settings struct {
	Startup bool   `json:"startup"`
	APIURL  string `json:"api_url"`
}

var (
	settings     Settings
	settingsPath string
)

func loadSettings() {
	appData := os.Getenv("APPDATA")
	settingsPath = filepath.Join(appData, AppName, "settings.json")
	_ = os.MkdirAll(filepath.Dir(settingsPath), 0755)

	settingsLock.Lock()
	defer settingsLock.Unlock()

	file, err := os.Open(settingsPath)
	if err == nil {
		defer file.Close()
		decoder := json.NewDecoder(file)
		if err := decoder.Decode(&settings); err == nil {
			appLogger.Println("Settings loaded successfully")
			return
		}
	}

	// Default settings
	settings = Settings{
		Startup: false,
		APIURL:  fmt.Sprintf("http://%s:%s", APIHost, APIPort),
	}
	saveSettingsLocked()
	appLogger.Println("Created default settings")
}

func saveSettingsLocked() {
	file, err := os.Create(settingsPath)
	if err != nil {
		appLogger.Printf("Failed to save settings: %v", err)
		return
	}
	defer file.Close()

	encoder := json.NewEncoder(file)
	encoder.SetIndent("", "    ")
	_ = encoder.Encode(settings)
}

func saveSettings() {
	settingsLock.Lock()
	defer settingsLock.Unlock()
	saveSettingsLocked()
	appLogger.Println("Settings saved successfully")
}
