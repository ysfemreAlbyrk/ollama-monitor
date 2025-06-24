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
import logging
from datetime import datetime
from logging.handlers import RotatingFileHandler
from typing import Optional
from urllib.parse import urlparse

import pystray
import httpx
from PIL import Image
from tkinter import ttk
import tkinter as tk
from tkinter import messagebox
import winreg

from __version__ import __version__, __author__, __copyright__

def setup_logging():
    """Setup logging configuration."""
    log_dir = os.path.join(os.getenv('APPDATA'), 'OllamaMonitor', 'logs')
    os.makedirs(log_dir, exist_ok=True)
    
    # Log file with date
    log_file = os.path.join(
        log_dir, 
        f'ollama_monitor_{datetime.now().strftime("%Y%m%d")}.log'
    )
    
    # Create rotating file handler (max 5MB per file, keep 5 backup files)
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=5*1024*1024,  # 5MB
        backupCount=5,
        encoding='utf-8'
    )
    
    # Create console handler
    console_handler = logging.StreamHandler()
    
    # Create formatters and add it to the handlers
    file_formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(message)s'
    )
    console_formatter = logging.Formatter(
        '[%(levelname)s] %(message)s'
    )
    file_handler.setFormatter(file_formatter)
    console_handler.setFormatter(console_formatter)
    
    # Get the logger
    logger = logging.getLogger('OllamaMonitor')
    logger.setLevel(logging.INFO)
    
    # Add the handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

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
        
        # API URL setting
        url_frame = ttk.Frame(api_frame)
        url_frame.pack(fill="x", pady=2)
        
        ttk.Label(
            url_frame, 
            text="Ollama URL:"
        ).pack(side="left")
        
        self.api_url_var = tk.StringVar(
            value=self.monitor.settings.get(
                'api_url', 
                f'http://{self.monitor.DEFAULT_API_HOST}:{self.monitor.DEFAULT_API_PORT}'
            )
        )
        url_entry = ttk.Entry(
            url_frame,
            textvariable=self.api_url_var,
            width=30
        )
        url_entry.pack(side="right")
        
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
                # Use sys.executable for a more reliable path to the bundled .exe
                executable_path = sys.executable if hasattr(sys, 'frozen') else os.path.abspath(sys.argv[0])
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
            self.monitor.logger.error(f"Failed to save startup setting: {str(e)}")
    
    def save_api_settings(self):
        """Save API settings and reinitialize client."""
        try:
            api_url = self.api_url_var.get().strip()
            
            # Basic URL validation
            parsed = urlparse(api_url)
            if not all([parsed.scheme, parsed.netloc]):
                raise ValueError("Invalid URL format")
            
            # Save new settings
            self.monitor.settings['api_url'] = api_url
            self.monitor.save_settings()
            
            # Reinitialize client
            if hasattr(self.monitor, 'client'):
                self.monitor.client.close()
            self.monitor._init_http_client()
            
            self.window.destroy()
            self.monitor.logger.info("API settings saved and connection updated!")
            self.monitor.icon.notify("API settings saved and connection updated!")
            
        except Exception as e:
            messagebox.showerror(
                "Error",
                f"Invalid API URL: {str(e)}"
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
        # Setup logging
        self.logger = setup_logging()
        self.logger.info(f"Starting Ollama Monitor v{__version__}")
        
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
        
        # Initialize HTTP client with configuration
        self._init_http_client()

    def _init_http_client(self):
        """Initialize HTTP client with current settings."""
        try:
            # Parse URL for authentication
            url = self.api_url
            parsed_url = urlparse(url)
            
            self.logger.info(f"Initializing HTTP client with URL: {url}")
            
            # Setup client config
            client_config = {
                'verify': False,  # Disable SSL verification for proxy support
                'follow_redirects': True
            }

            # If URL contains authentication, set it up in client
            if parsed_url.username and parsed_url.password:
                auth = (parsed_url.username, parsed_url.password)
                client_config['auth'] = auth
                self.logger.info("Using URL authentication")

            # Create client with config
            self.client = httpx.Client(**client_config)
            self.logger.info("HTTP client initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Error initializing HTTP client: {str(e)}")
            raise

    def load_settings(self):
        """Load application settings from JSON file."""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r') as f:
                    self.settings = json.load(f)
                    self.logger.info("Settings loaded successfully")
                    
                    # Convert old settings format if needed
                    if 'api_host' in self.settings and 'api_port' in self.settings:
                        host = self.settings.pop('api_host')
                        port = self.settings.pop('api_port')
                        self.settings['api_url'] = f'http://{host}:{port}'
                        self.save_settings()
                        self.logger.info("Converted old settings format to new URL format")
            else:
                # Default settings
                self.settings = {
                    'startup': False,
                    'api_url': f'http://{self.DEFAULT_API_HOST}:{self.DEFAULT_API_PORT}'
                }
                # Save default settings
                self.save_settings()
                self.logger.info("Created default settings")
        except Exception as e:
            self.logger.error(f"Error loading settings: {str(e)}")
            self.settings = {
                'startup': False,
                'api_url': f'http://{self.DEFAULT_API_HOST}:{self.DEFAULT_API_PORT}'
            }

    def save_settings(self):
        """Save application settings to JSON file."""
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(self.settings, f, indent=4)
            self.logger.info("Settings saved successfully")
        except Exception as e:
            self.logger.error(f"Error saving settings: {str(e)}")

    def get_running_models(self) -> str:
        """
        Get information about running Ollama models.
        
        Returns:
            Status message about running models
        """
        try:
            response = self.client.get(
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
                        self.logger.info(f"Model status changed: {model_info}")
                        self.icon.notify(f"{model_info}")
                        self.last_status = model_info
                    return model_info
                
                if self.last_status != "No Model Running":
                    self.logger.info("No model running")
                    self.icon.notify("Model Stopped")
                    self.last_status = "No Model Running"
                return "No Model Running"
                
            self.logger.warning(f"API returned status code: {response.status_code}")
            return "Ollama Not Running"
            
        except httpx.TimeoutException:
            self.logger.error("API request timed out")
            return "Ollama Not Running"
            
        except httpx.ConnectError as e:
            self.logger.error(f"Connection error: {str(e)}")
            if self.last_status != "Ollama Not Running":
                self.icon.notify("Ollama Service Stopped")
                self.last_status = "Ollama Not Running"
            return "Ollama Not Running"
            
        except Exception as e:
            self.logger.error(f"Unexpected error in get_running_models: {str(e)}")
            return "Ollama Not Running"

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
        self.logger.info("Stopping Ollama Monitor...")
        if hasattr(self, 'client') and self.client is not None:
            try:
                self.client.close()
                self.logger.info("HTTP client closed.")
            except Exception as e:
                self.logger.error(f"Error closing HTTP client: {str(e)}")

        if self.icon:
            self.icon.stop()
            self.logger.info("System tray icon stopped.")

    def show_settings(self):
        """Show the settings window."""
        SettingsWindow(self)

    @property
    def api_url(self) -> str:
        """Get the API URL from settings."""
        return self.settings.get(
            'api_url',
            f'http://{self.DEFAULT_API_HOST}:{self.DEFAULT_API_PORT}'
        )

    def __del__(self):
        """Cleanup when the object is destroyed."""
        # self.client.close() is now handled in stop()
        self.logger.info("Ollama Monitor object being deleted.")


if __name__ == "__main__":
    monitor = OllamaMonitor()
    monitor.run()