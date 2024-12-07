# Changelog

All notable changes to Ollama Monitor will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
