#!/usr/bin/env python3
"""
Ollama Monitor - A system tray application to monitor Ollama AI models.
Created by: Yusuf Emre ALBAYRAK
"""

import json
import os
import sys
import threading
import time
import webbrowser
from typing import Optional

import pystray
import requests
from PIL import Image
from tkinter import ttk
import tkinter as tk
import winreg

from __version__ import __version__, __author__, __copyright__

class SettingsWindow:
    """Settings window for Ollama Monitor configuration."""

    def __init__(self, monitor: 'OllamaMonitor'):
        """
        Initialize the settings window.

        Args:
            monitor: Reference to the main OllamaMonitor instance
        """
        self.monitor = monitor
        self.window = tk.Tk()
        self.window.title("Ollama Monitor - Settings")
        self.window.geometry("400x460")
        self.window.resizable(False, False)
        
        # Set Windows theme
        self.style = ttk.Style()
        self.style.theme_use('vista')
        
        self._create_widgets()
        self._center_window()
        
        # Make window modal
        self.window.transient()
        self.window.grab_set()
        self.window.focus_set()
        
        self.window.mainloop()
    
    def _create_widgets(self):
        """Create and arrange all window widgets."""
        # Title
        title_label = ttk.Label(
            self.window, 
            text="Ollama Monitor", 
            font=('Segoe UI', 14, 'bold')
        )
        title_label.pack(pady=10)
        
        # Settings frame
        settings_frame = ttk.LabelFrame(
            self.window, 
            text="Settings", 
            padding=10
        )
        settings_frame.pack(fill="x", padx=10, pady=5)
        
        # Startup setting
        self.startup_var = tk.BooleanVar(
            value=self.monitor.settings.get('startup', False)
        )
        startup_check = ttk.Checkbutton(
            settings_frame,
            text="Run at Windows startup",
            variable=self.startup_var,
            command=self.toggle_startup
        )
        startup_check.pack(anchor="w", pady=5)
        
        # API Settings frame
        api_frame = ttk.LabelFrame(
            self.window, 
            text="API Connection", 
            padding=10
        )
        api_frame.pack(fill="x", padx=10, pady=5)
        
        # Host setting
        host_frame = ttk.Frame(api_frame)
        host_frame.pack(fill="x", pady=2)
        
        ttk.Label(
            host_frame, 
            text="Host:"
        ).pack(side="left")
        
        self.host_var = tk.StringVar(
            value=self.monitor.settings.get(
                'api_host', 
                self.monitor.DEFAULT_API_HOST
            )
        )
        host_entry = ttk.Entry(
            host_frame,
            textvariable=self.host_var,
            width=30
        )
        host_entry.pack(side="right")
        
        # Port setting
        port_frame = ttk.Frame(api_frame)
        port_frame.pack(fill="x", pady=2)
        
        ttk.Label(
            port_frame, 
            text="Port:"
        ).pack(side="left")
        
        self.port_var = tk.StringVar(
            value=self.monitor.settings.get(
                'api_port', 
                self.monitor.DEFAULT_API_PORT
            )
        )
        port_entry = ttk.Entry(
            port_frame,
            textvariable=self.port_var,
            width=30
        )
        port_entry.pack(side="right")
        
        # Save API settings button
        save_api_btn = ttk.Button(
            api_frame,
            text="Save API Settings",
            command=self.save_api_settings
        )
        save_api_btn.pack(pady=5)
        
        # About frame
        about_frame = ttk.LabelFrame(
            self.window, 
            text="About", 
            padding=10
        )
        about_frame.pack(fill="x", padx=10, pady=5)
        
        # Version info
        version_label = ttk.Label(
            about_frame, 
            text=f"Version: {__version__}"
        )
        version_label.pack(anchor="w")
        
        # Description
        desc_label = ttk.Label(
            about_frame,
            text="Ollama Monitor is a system tray application that helps you\nmonitor your Ollama AI models.\nCreated by Yusuf Emre ALBAYRAK",
            justify="left"
        )
        desc_label.pack(anchor="w", pady=5)
        
        # GitHub link
        github_link = ttk.Label(
            about_frame,
            text="GitHub Repository",
            cursor="hand2",
            foreground="blue"
        )
        github_link.pack(anchor="w")
        github_link.bind(
            "<Button-1>", 
            lambda e: webbrowser.open(
                "https://github.com/ysfemreAlbyrk/ollama-monitor"
            )
        )
        
        # Close button
        close_btn = ttk.Button(
            self.window, 
            text="Close", 
            command=self.window.destroy
        )
        close_btn.pack(side="bottom", pady=10)
    
    def _center_window(self):
        """Center the window on the screen."""
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f'{width}x{height}+{x}+{y}')
    
    def toggle_startup(self):
        """Toggle Windows startup setting."""
        startup = self.startup_var.get()
        self.monitor.settings['startup'] = startup
        self.monitor.save_settings()
        
        key_path = r"Software\\Microsoft\\Windows\\CurrentVersion\\Run"
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER, 
                key_path, 
                0, 
                winreg.KEY_ALL_ACCESS
            )
            
            if startup:
                executable_path = os.path.abspath(sys.argv[0])
                winreg.SetValueEx(
                    key, 
                    "OllamaMonitor", 
                    0, 
                    winreg.REG_SZ, 
                    executable_path
                )
            else:
                try:
                    winreg.DeleteValue(key, "OllamaMonitor")
                except WindowsError:
                    pass
            
            winreg.CloseKey(key)
        except Exception as e:
            self.monitor.icon.notify(
                "Failed to save startup setting!"
            )
    
    def save_api_settings(self):
        """Save API connection settings."""
        self.monitor.settings['api_host'] = self.host_var.get()
        self.monitor.settings['api_port'] = self.port_var.get()
        self.monitor.save_settings()
        self.monitor.icon.notify(
            "API settings saved! Changes will take effect immediately."
        )


class CustomMenuItem(pystray.MenuItem):
    """Custom menu item with better visibility for disabled items."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def render(self, window, offset=(0, 0)):
        if not self.visible:
            return []
            
        # Use white color (or any other color) for disabled items
        text_color = 'white' if not self.enabled else 'black'
        
        return [(
            offset[0], offset[1],
            self.text,
            {
                'text': text_color,
                'background': None,
            }
        )]


class OllamaMonitor:
    """Main class for the Ollama Monitor application."""
    
    DEFAULT_API_HOST = "localhost"
    DEFAULT_API_PORT = "11434"
    
    def __init__(self):
        """Initialize the Ollama Monitor application."""
        self.current_model = "Waiting..."
        self.icon: Optional[pystray.Icon] = None
        self.should_run = True
        self.last_status = None
        
        # Icon paths
        self.icons_dir = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), 
            'icons'
        )
        self.icon_red = os.path.join(self.icons_dir, 'icon_red.png')
        self.icon_blue = os.path.join(self.icons_dir, 'icon_blue.png')
        self.icon_green = os.path.join(self.icons_dir, 'icon_green.png')
        
        # Load settings
        self.settings_file = os.path.join(
            os.getenv('APPDATA'),
            'OllamaMonitor',
            'settings.json'
        )
        os.makedirs(os.path.dirname(self.settings_file), exist_ok=True)
        self.load_settings()

    def load_settings(self):
        """Load application settings from JSON file."""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r') as f:
                    self.settings = json.load(f)
            else:
                # Default settings
                self.settings = {
                    'startup': False,
                    'api_host': self.DEFAULT_API_HOST,
                    'api_port': self.DEFAULT_API_PORT
                }
                # Save default settings
                self.save_settings()
        except Exception as e:
            print(f"Error loading settings: {e}")
            self.settings = {
                'startup': False,
                'api_host': self.DEFAULT_API_HOST,
                'api_port': self.DEFAULT_API_PORT
            }

    def save_settings(self):
        """Save application settings to JSON file."""
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(self.settings, f, indent=4)
        except Exception as e:
            print(f"Error saving settings: {e}")
    
    def show_settings(self):
        """Show the settings window."""
        SettingsWindow(self)

    @property
    def api_url(self) -> str:
        """Get the full API URL based on current settings."""
        host = self.settings.get('api_host', self.DEFAULT_API_HOST)
        port = self.settings.get('api_port', self.DEFAULT_API_PORT)
        return f"http://{host}:{port}"

    def create_icon(self, status: str) -> Image.Image:
        """
        Create system tray icon based on status.
        
        Args:
            status: Current status text
            
        Returns:
            PIL Image object for the icon
        """
        if "Ollama Not Running" in status:
            icon_path = self.icon_red
        elif "No Model Running" in status:
            icon_path = self.icon_blue
        else:
            icon_path = self.icon_green
            
        return Image.open(icon_path)

    def get_running_models(self) -> str:
        """
        Get information about running Ollama models.
        
        Returns:
            Status message about running models
        """
        try:
            response = requests.get(
                f'{self.api_url}/api/ps',
                timeout=2
            )
            
            if response.status_code == 200:
                data = response.json()
                running_models = data.get('models', [])
                
                if running_models:
                    model = running_models[0]
                    model_info = (
                        f"{model['name']} "
                        f"({model['details']['parameter_size']})"
                    )
                    
                    if self.last_status != model_info:
                        self.icon.notify(
                            f"{model_info}"
                        )
                        self.last_status = model_info
                    return model_info
                
                if self.last_status != "No Model Running":
                    self.icon.notify("Model Stopped")
                    self.last_status = "No Model Running"
                return "No Model Running"
                
            return "Ollama Not Running"
            
        except requests.exceptions.Timeout:
            return "Ollama Not Running"
            
        except requests.exceptions.ConnectionError:
            if self.last_status != "Ollama Not Running":
                self.icon.notify("Ollama Service Stopped")
                self.last_status = "Ollama Not Running"
            return "Ollama Not Running"
            
        except Exception:
            return "Ollama Not Running"

    def create_menu(self) -> pystray.Menu:
        """
        Create the system tray icon menu.
        
        Returns:
            pystray.Menu object
        """
        return pystray.Menu(
            pystray.MenuItem(
                self.current_model,  
                lambda _: None,
                enabled=True
            ),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Settings", self.show_settings),
            pystray.MenuItem("Exit", self.stop)
        )

    def update_status(self):
        """Update the system tray icon status periodically."""
        while self.should_run:
            self.current_model = self.get_running_models()
            if self.icon:
                self.icon.icon = self.create_icon(self.current_model)
                self.icon.title = f"{self.current_model}"
                self.icon.menu = self.create_menu()
            time.sleep(1)

    def run(self):
        """Start the Ollama Monitor application."""
        self.icon = pystray.Icon(
            "ollama-monitor",
            self.create_icon("Starting..."),
            "Ollama Monitor",
            menu=self.create_menu()
        )

        update_thread = threading.Thread(target=self.update_status)
        update_thread.daemon = True
        update_thread.start()

        self.icon.run()

    def stop(self):
        """Stop the Ollama Monitor application."""
        self.should_run = False
        if self.icon:
            self.icon.stop()


if __name__ == "__main__":
    monitor = OllamaMonitor()
    monitor.run()