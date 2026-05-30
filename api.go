package main

import (
	"crypto/tls"
	"encoding/json"
	"fmt"
	"net/http"
	"net/url"
	"strings"
	"time"
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
	client            *http.Client
	lastRunningModels []string
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

func sliceContains(slice []string, val string) bool {
	for _, item := range slice {
		if item == val {
			return true
		}
	}
	return false
}

func notifyModelChanges(currentModels []string) {
	// If it's the first run, populate lastRunningModels but don't notify to avoid startup spam
	if lastStatus == "" {
		lastRunningModels = currentModels
		lastStatus = strings.Join(currentModels, ", ")
		return
	}

	var started []string
	for _, m := range currentModels {
		if !sliceContains(lastRunningModels, m) {
			started = append(started, m)
		}
	}

	var stopped []string
	for _, m := range lastRunningModels {
		if !sliceContains(currentModels, m) {
			stopped = append(stopped, m)
		}
	}

	if len(started) > 0 {
		sendNotification("Model Started", strings.Join(started, ", "))
	}
	if len(stopped) > 0 {
		sendNotification("Model Stopped", strings.Join(stopped, ", "))
	}

	lastRunningModels = currentModels
	lastStatus = strings.Join(currentModels, ", ")
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
			sendNotification("Ollama Service Stopped", "Could not connect to Ollama")
			lastStatus = "Ollama Not Running"
			lastRunningModels = nil
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
		
		notifyModelChanges(models)
		return StateActive, models
	}

	if lastStatus != "No Model Running" {
		appLogger.Println("No model running")
		notifyModelChanges(nil)
		lastStatus = "No Model Running"
	}
	return StateIdle, nil
}
