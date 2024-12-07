"""Build script for OllamaMonitor."""
import os
import shutil
import subprocess

def clean_build():
    """Clean build and dist directories."""
    dirs_to_clean = ['build', 'dist']
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"Cleaned {dir_name} directory")

def create_version_info():
    """Create version info file."""
    subprocess.run(['python', 'create_version_info.py'], check=True)
    print("Created version_info.txt")

def build_exe():
    """Build executable."""
    subprocess.run(['pyinstaller', 'OllamaMonitor.spec'], check=True)
    print("Built executable")

def main():
    """Main build process."""
    print("Starting build process...")
    clean_build()
    create_version_info()
    build_exe()
    print("Build process completed!")

if __name__ == '__main__':
    main()
