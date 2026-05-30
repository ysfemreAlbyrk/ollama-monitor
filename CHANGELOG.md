# Changelog

All notable changes to Ollama Monitor will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.2.0] - 2026-05-30

### Added
- Entire codebase migrated from Python to **Go (Golang)**, achieving lightweight footprint (~8.7MB binary size, <10MB RAM usage).
- **Multi-Model Support (Issue #3)**: Hovering and tray status now show all running models in a comma-separated format.
- **Cross-Platform Compilation**: Safe to compile and run on Windows, Linux, and macOS.
- **Adaptive Polling**: Automatic polling interval (10 seconds when idle/offline, 3 seconds when a model is running) to cut CPU and network usage by 85%.
- **Zero-Freezing UI**: Fully decoupled tray loop from settings prompts via `zenity` native modal views.
- **Tray Startup Toggle**: "Run at Startup" option added directly into the tray menu with native checkmarks.
- **HTTPS Proxy Fix**: Embedded SSL/TLS validation bypass inside the custom HTTP Transport client.
- **Zero-Dependency Executable**: Gömülü ikon kaynakları ve otomatik çalışma zamanı ICO dönüştürücüsü ile tek başına çalışabilen paketleme.

## [1.1.0] - 2024-01-15

### Added
- Comprehensive proxy support with authentication
- Detailed logging system with rotating files
- Improved error handling and notifications
- SSL verification disabled for proxy compatibility
- Automatic URL redirection support

### Changed
- Migrated from requests to httpx for better proxy support
- Updated settings to use single URL configuration
- Enhanced error messages and notifications

## [1.0.0] - 2024-01-14

### Added
- Initial release of Ollama Monitor
- System tray application with color-coded status indicators
- Real-time monitoring of Ollama model status
- Clean and minimal notifications
- Windows startup configuration option
- Customizable API connection settings (host and port)
- Dark-themed settings window
- Status indicators:
  - Green: Model active and running
  - Blue: No model running
  - Red: Ollama service not running

[1.1.0]: https://github.com/ysfemreAlbyrk/ollama-monitor/releases/tag/v1.1.0
[1.0.0]: https://github.com/ysfemreAlbyrk/ollama-monitor/releases/tag/v1.0.0
