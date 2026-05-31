//go:build windows

package monitor

import (
	"os"
	"path/filepath"

	"git.sr.ht/~jackmordaunt/go-toast"
	"golang.org/x/sys/windows/registry"
)

func registerAUMID() {
	// 1. Register AppID metadata (Friendly name "Ollama Monitor" and Icon "logo.png")
	k, _, err := registry.CreateKey(
		registry.CURRENT_USER,
		`Software\Classes\AppUserModelId\OllamaMonitor`,
		registry.QUERY_VALUE|registry.SET_VALUE,
	)
	if err == nil {
		defer k.Close()
		_ = k.SetStringValue("DisplayName", "Ollama Monitor")
		
		// Extract embedded blue PNG icon directly next to the executable.
		// Windows Notification Service (running in a low-privilege AppContainer sandbox)
		// cannot read files from %APPDATA% due to sandbox restrictions, but it has
		// native read access to the application's own installation folder.
		execPath, err := os.Executable()
		if err == nil {
			execDir := filepath.Dir(execPath)
			iconPath := filepath.Join(execDir, "logo.png")
			_ = os.WriteFile(iconPath, iconBlue, 0644)
			_ = k.SetStringValue("IconUri", iconPath)
		}
	}

	// 2. Associate OllamaMonitor.exe executable name with the AppID.
	// This tells the Windows shell that any process named OllamaMonitor.exe
	// defaults to the AppID "OllamaMonitor", resolving friendly names and icons instantly.
	kApp, _, err := registry.CreateKey(
		registry.CURRENT_USER,
		`Software\Classes\Applications\OllamaMonitor.exe`,
		registry.QUERY_VALUE|registry.SET_VALUE,
	)
	if err == nil {
		defer kApp.Close()
		_ = kApp.SetStringValue("AppUserModelID", "OllamaMonitor")
	}
}

func sendNotification(title, message string) {
	execPath, err := os.Executable()
	var iconPath string
	if err == nil {
		execDir := filepath.Dir(execPath)
		iconPath = filepath.Join(execDir, "logo.png")
	}

	notification := toast.Notification{
		AppID: "OllamaMonitor", // Use the registered AppID
		Title: title,
		Body:  message,
		Icon:  iconPath, // Body icon path on disk
	}
	_ = notification.Push()
}
