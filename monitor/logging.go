package monitor

import (
	"fmt"
	"io"
	"log"
	"os"
	"path/filepath"
	"sync"
	"time"
)

var (
	appLogger     *log.Logger
	rotatedWriter *RotatedWriter
)

// RotatedWriter for log rotation
type RotatedWriter struct {
	mu       sync.Mutex
	filename string
	file     *os.File
	maxSize  int64
}

func NewRotatedWriter(filename string, maxSize int64) (*RotatedWriter, error) {
	rw := &RotatedWriter{
		filename: filename,
		maxSize:  maxSize,
	}
	err := rw.open()
	return rw, err
}

func (rw *RotatedWriter) open() error {
	_ = os.MkdirAll(filepath.Dir(rw.filename), 0755)
	var err error
	rw.file, err = os.OpenFile(rw.filename, os.O_CREATE|os.O_WRONLY|os.O_APPEND, 0644)
	return err
}

func (rw *RotatedWriter) Write(p []byte) (n int, err error) {
	rw.mu.Lock()
	defer rw.mu.Unlock()

	stat, err := rw.file.Stat()
	if err == nil && stat.Size()+int64(len(p)) > rw.maxSize {
		_ = rw.file.Close()
		backup := rw.filename + "." + time.Now().Format("20060102150405")
		_ = os.Rename(rw.filename, backup)
		_ = rw.open()
	}

	return rw.file.Write(p)
}

func (rw *RotatedWriter) Close() error {
	if rw.file != nil {
		return rw.file.Close()
	}
	return nil
}

func setupLogging() {
	appData := os.Getenv("APPDATA")
	logDir := filepath.Join(appData, AppName, "logs")
	_ = os.MkdirAll(logDir, 0755)

	logFile := filepath.Join(logDir, fmt.Sprintf("ollama_monitor_%s.log", time.Now().Format("20060102")))
	
	var err error
	rotatedWriter, err = NewRotatedWriter(logFile, 5*1024*1024) // 5MB
	if err != nil {
		log.Printf("Failed to initialize log file: %v", err)
		appLogger = log.New(os.Stdout, "", log.LstdFlags)
		return
	}

	multi := io.MultiWriter(os.Stdout, rotatedWriter)
	appLogger = log.New(multi, "", log.LstdFlags)
	appLogger.Printf("Starting Ollama Monitor v%s", Version)
}
