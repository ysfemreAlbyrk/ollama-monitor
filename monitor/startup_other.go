//go:build !windows

package monitor

func toggleStartup(enable bool) error {
	// Startup configuration not implemented yet on non-Windows platforms
	return nil
}
