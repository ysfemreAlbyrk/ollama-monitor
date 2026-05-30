package main

import (
	"fmt"
	"net/url"
	"strings"
	"sync"
	"time"

	"github.com/gen2brain/beeep"
	"github.com/getlantern/systray"
	"github.com/ncruces/zenity"
)

// Version info
const (
	Version   = "1.1.0"
	Author    = "Yusuf Emre ALBAYRAK"
	AppName   = "OllamaMonitor"
	APIHost   = "localhost"
	APIPort   = "11434"
)

var (
	settingsLock  sync.Mutex
	currentModel  = "Waiting..."
	lastStatus    = ""
)

func changeAPIURL() {
	settingsLock.Lock()
	currentAPIURL := settings.APIURL
	settingsLock.Unlock()

	newURL, err := zenity.Entry(
		"Enter Ollama API URL:",
		zenity.Title("Change API URL"),
		zenity.EntryText(currentAPIURL),
	)
	if err != nil {
		return
	}

	newURL = strings.TrimSpace(newURL)
	_, err = url.Parse(newURL)
	if err != nil || newURL == "" || !strings.HasPrefix(newURL, "http") {
		_ = zenity.Error(
			"Invalid API URL format. It must start with http:// or https://",
			zenity.Title("Error"),
		)
		return
	}

	settingsLock.Lock()
	settings.APIURL = newURL
	settingsLock.Unlock()

	saveSettings()
	
	_ = beeep.Notify("Settings Saved", fmt.Sprintf("Ollama API URL updated to: %s", newURL), "")
}

func showAbout() {
	_ = zenity.Info(
		fmt.Sprintf("Ollama Monitor v%s\n\nCreated by %s\n\nA lightweight system tray tool to monitor Ollama AI models with real-time status updates.", Version, Author),
		zenity.Title("About Ollama Monitor"),
	)
}

func updateStatusLoop(mStatus *systray.MenuItem) {
	for {
		status := getRunningModels()
		currentModel = status

		// Update system tray icon dynamically
		if strings.Contains(status, "Ollama Not Running") {
			systray.SetIcon(iconRed)
			systray.SetTooltip("Ollama Service: Offline")
			mStatus.SetTitle("Ollama Not Running")
		} else if strings.Contains(status, "No Model Running") {
			systray.SetIcon(iconBlue)
			systray.SetTooltip("Ollama Service: Idle")
			mStatus.SetTitle("No Model Running")
		} else {
			systray.SetIcon(iconGreen)
			// Truncate tooltip if it is too long for Windows limits (128 chars)
			tooltip := fmt.Sprintf("Models: %s", status)
			if len(tooltip) > 127 {
				tooltip = tooltip[:124] + "..."
			}
			systray.SetTooltip(tooltip)
			
			// Show actual models in menu item
			mStatus.SetTitle(status)
		}

		time.Sleep(2 * time.Second)
	}
}

func onReady() {
	systray.SetIcon(iconBlue)
	systray.SetTitle("Ollama Monitor")
	systray.SetTooltip("Ollama Monitor - Loading...")

	mStatus := systray.AddMenuItem("Waiting...", "")
	mStatus.Disable()
	
	systray.AddSeparator()
	
	mStartup := systray.AddMenuItem("Run at Startup", "")
	settingsLock.Lock()
	isStartup := settings.Startup
	settingsLock.Unlock()
	if isStartup {
		mStartup.Check()
	} else {
		mStartup.Uncheck()
	}

	mAPI := systray.AddMenuItem("Change API URL...", "")
	mAbout := systray.AddMenuItem("About...", "")
	
	systray.AddSeparator()
	mExit := systray.AddMenuItem("Exit", "")

	// Start status updater loop
	go updateStatusLoop(mStatus)

	// Wait for actions
	go func() {
		for {
			select {
			case <-mStartup.ClickedCh:
				settingsLock.Lock()
				settings.Startup = !settings.Startup
				newStartup := settings.Startup
				settingsLock.Unlock()
				
				saveSettings()
				if newStartup {
					mStartup.Check()
					if err := toggleStartup(true); err != nil {
						appLogger.Printf("Failed to enable startup: %v", err)
						_ = zenity.Error(fmt.Sprintf("Failed to configure Windows startup: %v", err), zenity.Title("Error"))
					}
				} else {
					mStartup.Uncheck()
					if err := toggleStartup(false); err != nil {
						appLogger.Printf("Failed to disable startup: %v", err)
					}
				}
				
			case <-mAPI.ClickedCh:
				appLogger.Println("Change API URL clicked")
				go changeAPIURL()
				
			case <-mAbout.ClickedCh:
				appLogger.Println("About clicked")
				go showAbout()
				
			case <-mExit.ClickedCh:
				appLogger.Println("Exit clicked, shutting down")
				systray.Quit()
			}
		}
	}()
}

func onExit() {
	appLogger.Println("Ollama Monitor stopped")
	if rotatedWriter != nil {
		_ = rotatedWriter.Close()
	}
}

func main() {
	setupLogging()
	loadSettings()
	initHTTPClient()
	initIcons()

	systray.Run(onReady, onExit)
}
