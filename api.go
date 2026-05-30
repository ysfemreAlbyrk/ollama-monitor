package main

import (
	"crypto/tls"
	"encoding/json"
	"fmt"
	"net/http"
	"net/url"
	"strings"
	"time"

	"github.com/gen2brain/beeep"
)

// States
const (
	StateOffline = iota
	StateIdle
	StateActive
)

// Ollama API response structures
type ModelDetails struct {
	ParameterSize string `json:"parameter_size"`
}

type ModelInfo struct {
	Name    string       `json:"name"`
	Details ModelDetails `json:"details"`
}

type PSResponse struct {
	Models []ModelInfo `json:"models"`
}

var (
	client *http.Client
)

func initHTTPClient() {
	tr := &http.Transport{
		Proxy: http.ProxyFromEnvironment,
		TLSClientConfig: &tls.Config{
			InsecureSkipVerify: true, // Bypass SSL/TLS certificate validation for proxies and self-signed certs
		},
	}
	client = &http.Client{
		Transport: tr,
		Timeout:   2 * time.Second,
	}
}

func getRunningModels() (int, []string) {
	settingsLock.Lock()
	apiURL := settings.APIURL
	settingsLock.Unlock()

	parsedURL, err := url.Parse(apiURL)
	if err != nil {
		appLogger.Printf("Invalid API URL: %v", err)
		return StateOffline, nil
	}

	endpoint := fmt.Sprintf("%s/api/ps", apiURL)
	req, err := http.NewRequest("GET", endpoint, nil)
	if err != nil {
		appLogger.Printf("Failed to create request: %v", err)
		return StateOffline, nil
	}

	// Support basic authentication if username/password is present in the URL
	if parsedURL.User != nil {
		password, _ := parsedURL.User.Password()
		req.SetBasicAuth(parsedURL.User.Username(), password)
	}

	resp, err := client.Do(req)
	if err != nil {
		if lastStatus != "Ollama Not Running" {
			appLogger.Printf("Connection error: %v", err)
			_ = beeep.Notify("Ollama Service Stopped", "Could not connect to Ollama", "")
			lastStatus = "Ollama Not Running"
		}
		return StateOffline, nil
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		appLogger.Printf("API returned status code: %d", resp.StatusCode)
		return StateOffline, nil
	}

	var psResp PSResponse
	if err := json.NewDecoder(resp.Body).Decode(&psResp); err != nil {
		appLogger.Printf("Failed to decode response: %v", err)
		return StateOffline, nil
	}

	if len(psResp.Models) > 0 {
		var models []string
		for _, m := range psResp.Models {
			models = append(models, fmt.Sprintf("%s (%s)", m.Name, m.Details.ParameterSize))
		}
		modelInfo := strings.Join(models, ", ")

		if lastStatus != modelInfo {
			appLogger.Printf("Model status changed: %s", modelInfo)
			_ = beeep.Notify("Model Running", modelInfo, "")
			lastStatus = modelInfo
		}
		return StateActive, models
	}

	if lastStatus != "No Model Running" {
		appLogger.Println("No model running")
		_ = beeep.Notify("Model Stopped", "All models unloaded", "")
		lastStatus = "No Model Running"
	}
	return StateIdle, nil
}
