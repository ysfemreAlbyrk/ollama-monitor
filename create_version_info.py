"""Create version info file for PyInstaller."""
from __version__ import __version__, __author__, __copyright__

def create_version_tuple(version_str):
    """Convert version string to tuple."""
    return tuple(map(int, version_str.split('.'))) + (0,)

version_info = f'''VSVersionInfo(
  ffi=FixedFileInfo(
    filevers={create_version_tuple(__version__)},
    prodvers={create_version_tuple(__version__)},
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
  ),
  kids=[
    StringFileInfo(
      [
        StringTable(
          u'040904B0',
          [StringStruct(u'CompanyName', u'{__author__}'),
          StringStruct(u'FileDescription', u'System tray application to monitor Ollama AI models'),
          StringStruct(u'FileVersion', u'{__version__}'),
          StringStruct(u'InternalName', u'OllamaMonitor'),
          StringStruct(u'LegalCopyright', u'{__copyright__}'),
          StringStruct(u'OriginalFilename', u'OllamaMonitor.exe'),
          StringStruct(u'ProductName', u'Ollama Monitor'),
          StringStruct(u'ProductVersion', u'{__version__}')])
      ]
    ),
    VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
  ]
)'''

with open('version_info.txt', 'w') as f:
    f.write(version_info)
