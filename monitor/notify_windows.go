//go:build windows

package monitor

import (
	"os"
	"path/filepath"

	"git.sr.ht/~jackmordaunt/go-toast"
	"golang.org/x/sys/windows/registry"
)

func registerAUMID() {
	k, _, err := registry.CreateKey(
		registry.CURRENT_USER,
		`Software\Classes\AppUserModelId\OllamaMonitor`,
		registry.QUERY_VALUE|registry.SET_VALUE,
	)
	if err == nil {
		defer k.Close()
		_ = k.SetStringValue("DisplayName", "Ollama Monitor")
		
		// Extract embedded blue PNG icon to AppData so Windows toast can load it in the header
		appData := os.Getenv("APPDATA")
		iconDir := filepath.Join(appData, AppName)
		_ = os.MkdirAll(iconDir, 0755)
		
		iconPath := filepath.Join(iconDir, "logo.png")
		_ = os.WriteFile(iconPath, iconBlue, 0644)
		_ = k.SetStringValue("IconUri", iconPath)
	}
}

func sendNotification(title, message string) {
	appData := os.Getenv("APPDATA")
	iconPath := filepath.Join(appData, AppName, "logo.png")

	notification := toast.Notification{
		AppID: "OllamaMonitor",
		Title: title,
		Body:  message,
		Icon:  iconPath, // Path to local transparent PNG file on disk
	}
	_ = notification.Push()
}
