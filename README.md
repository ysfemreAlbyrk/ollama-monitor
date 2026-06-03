<p align="center">
  <picture>
    <source srcset="./monitor/icons/icon.ico">
    <img src="./monitor/icons/icon.ico" width="64" height="64">
  </picture>
</p>
<div align="center">
  
# Ollama Monitor

[![Go 1.18+](https://img.shields.io/badge/Go-1.18+-blue.svg)](https://go.dev/dl/)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-blue.svg)](#)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A lightweight cross-platform system tray application to monitor Ollama AI models with real-time status updates and zero-overhead performance.

[Features](#-features) • [Installation](#-installation) • [Usage](#-usage) • [Contributing](#-contributing) • [License](#-license)

</div>

---

## ✨ Features

- 🔄 **Real-Time Monitoring**: Dynamic tracking of loaded Ollama models.
- 🔀 **Multi-Model Support**: Displays all actively running models as individual dedicated rows in the tray menu and grouped in the hover tooltip.
- 🔔 **System Notifications**: Minimal, non-intrusive desktop notifications on model state changes.
- 🚀 **Windows Startup Configuration**: Native checkmark option directly in the tray menu to automatically run at Windows startup.
- ⚙️ **Customizable Connection**: Dynamic API URL setup with support for HTTPS proxies and SSL/TLS validation bypass.
- 🎯 **Color-Coded Status Indicators**:
  - 🟢 Green: Models are loaded and actively running
  - 🔵 Blue: Ollama service is idle (no model loaded)
  - 🔴 Red: Ollama service is offline or unreachable

---

## 📋 Requirements

- 💻 Windows 10/11, macOS, or Linux
- 🤖 [Ollama](https://github.com/jmorganca/ollama) installed and configured

---

## 🚀 Installation

### Option 1: Download Executable
1. Go to the [Releases](https://github.com/ysfemreAlbyrk/ollama-monitor/releases) page.
2. Download the latest compiled version for your operating system.
3. Run the executable.

### Option 2: Build from Source (Windows)
1. Clone this repository:
   ```bash
   git clone https://github.com/ysfemreAlbyrk/ollama-monitor.git
   cd ollama-monitor
   ```
2. Double-click the provided `build.bat` script or run it in your terminal:
   ```bash
   build.bat
   ```
   This will automatically compile a highly optimized, completely standalone, and terminal-free `OllamaMonitor.exe` in the root directory.

### Option 3: Build from Source (macOS / Linux)
1. Clone this repository:
   ```bash
   git clone https://github.com/ysfemreAlbyrk/ollama-monitor.git
   cd ollama-monitor
   ```
2. Compile using the Go compiler:
   ```bash
   go build -ldflags "-s -w" -o OllamaMonitor
   ```

---

## 📖 Usage

1. Ensure Ollama is running on your system.
2. Launch the **Ollama Monitor** application.
3. The app will immediately register in your system tray with a color-coded status icon.
4. Right-click the tray icon to:
   - View currently running models (each loaded model appears as an individual row).
   - Toggle **Run at Startup** (Windows-only).
   - Click **Change API URL...** to configure host connections (supports HTTPS proxies and authentication).
   - Click **About...** to view version information.
   - Click **Exit** to shut down the monitor.

---

## 🔧 Development & Project Structure

The project has been refactored into a highly modular, clean Go codebase:
- `main.go`: Application lifecycle, tray setup, and event loop.
- `api.go`: Ollama API client and multi-model query parser.
- `config.go`: Settings JSON loading/saving.
- `icon.go`: Embedded icon resources and PNG-to-ICO runtime packaging.
- `logging.go`: Rotating file logger.
- `startup_windows.go` / `startup_other.go`: Platform-specific OS startup registration using Go build tags.

---

## 📜 Changelog

See [CHANGELOG.md](CHANGELOG.md) for detailed version release history.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request or open an Issue.

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

<div align="center">
Made with ❤️ by Yusuf Emre ALBAYRAK
</div>
