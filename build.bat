@echo off
echo Generating Windows resources (icon and version info)...
go run github.com/josephspurrier/goversioninfo/cmd/goversioninfo
echo Building optimized OllamaMonitor.exe (no terminal)...
go build -ldflags "-s -w -H=windowsgui" -o OllamaMonitor.exe
echo Build completed successfully!
pause
