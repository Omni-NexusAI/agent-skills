# Voice Messaging Skill - Windows Setup Script
# Run with: .\setup.ps1

Write-Host "🎤 Voice Messaging Skill Setup" -ForegroundColor Cyan
Write-Host ""

# Check Python
Write-Host "Checking Python..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ Python: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Python not found" -ForegroundColor Red
    Write-Host "Install Python 3.9+ from: https://www.python.org/" -ForegroundColor Yellow
    exit 1
}

# Install Python dependencies
Write-Host ""
Write-Host "Installing Python dependencies..." -ForegroundColor Yellow
pip install faster-whisper requests pyav tomli
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Dependencies installed" -ForegroundColor Green
} else {
    Write-Host "✗ Failed to install dependencies" -ForegroundColor Red
    exit 1
}

# Check FFmpeg
Write-Host ""
Write-Host "Checking FFmpeg..." -ForegroundColor Yellow
try {
    $ffmpegVersion = ffmpeg -version 2>&1 | Select-String -Pattern "version"
    Write-Host "✓ FFmpeg: $ffmpegVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ FFmpeg not found" -ForegroundColor Red
    Write-Host ""
    Write-Host "Install FFmpeg:" -ForegroundColor Yellow
    Write-Host "  Option 1: choco install ffmpeg" -ForegroundColor White
    Write-Host "  Option 2: Download from https://ffmpeg.org/download.html" -ForegroundColor White
    Write-Host ""
    $install = Read-Host "Install FFmpeg with Chocolatey? (y/n)"
    if ($install -eq "y") {
        choco install ffmpeg
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✓ FFmpeg installed" -ForegroundColor Green
        } else {
            Write-Host "✗ Failed to install FFmpeg" -ForegroundColor Red
        }
    } else {
        Write-Host "Skipping FFmpeg install" -ForegroundColor Yellow
    }
}

# Check Kokoro TTS
Write-Host ""
Write-Host "Checking Kokoro TTS..." -ForegroundColor Yellow
try {
    $kokoroCheck = Test-NetConnection -ComputerName localhost -Port 8880 -WarningAction SilentlyContinue
    if ($kokoroCheck.TcpTestSucceeded) {
        Write-Host "✓ Kokoro TTS running on port 8880" -ForegroundColor Green
    } else {
        Write-Host "⚠ Kokoro TTS not detected on port 8880" -ForegroundColor Yellow
        Write-Host "  Make sure your Docker container is running" -ForegroundColor White
    }
} catch {
    Write-Host "⚠ Could not check Kokoro TTS" -ForegroundColor Yellow
}

# Test setup
Write-Host ""
Write-Host "Testing setup..." -ForegroundColor Yellow
try {
    python test.py
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Setup test passed" -ForegroundColor Green
    } else {
        Write-Host "⚠ Setup test incomplete (this is OK if Kokoro is not running)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "⚠ Setup test failed" -ForegroundColor Yellow
}

# Install in OpenClaw
Write-Host ""
Write-Host "Installing skill in OpenClaw..." -ForegroundColor Yellow
$skillPath = Join-Path $env:USERPROFILE, ".openclaw\skills\agent-voice-messaging"

# Create target directory
if (-not (Test-Path $skillPath)) {
    New-Item -ItemType Directory -Path $skillPath -Force | Out-Null
    Write-Host "✓ Created skill directory" -ForegroundColor Green
}

# Copy files
Write-Host "Copying files..."
Copy-Item -Path "SKILL.md" -Destination $skillPath -Force
Copy-Item -Path "README.md" -Destination $skillPath -Force
Copy-Item -Path "config.toml" -Destination $skillPath -Force

$srcDest = Join-Path $skillPath, "src"
if (-not (Test-Path $srcDest)) {
    New-Item -ItemType Directory -Path $srcDest -Force | Out-Null
}
Copy-Item -Path "src\*" -Destination $srcDest -Force

Write-Host "✓ Files copied" -ForegroundColor Green

# Summary
Write-Host ""
Write-Host "🎉 Setup Complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "  1. Ensure Kokoro TTS Docker container is running:" -ForegroundColor White
Write-Host "     docker run --gpus all -p 8880:8880 ghcr.io/remsky/kokoro-fastapi-gpu:latest" -ForegroundColor Gray
Write-Host ""
Write-Host "  2. Test the skill:" -ForegroundColor White
Write-Host "     python -c `\"import sys; sys.path.insert(0, 'src'); from voice_handler import quick_test; quick_test()`\"" -ForegroundColor Gray
Write-Host ""
Write-Host "  3. Install in OpenClaw:" -ForegroundColor White
Write-Host "     openclaw skills install $skillPath" -ForegroundColor Gray
Write-Host ""
Write-Host "  4. Send a test voice message from Telegram/Discord!" -ForegroundColor Gray
Write-Host ""
Write-Host "To change providers, edit config.toml:" -ForegroundColor Yellow
Write-Host "  [stt]" -ForegroundColor Gray
Write-Host "  provider = `"faster-whisper`"` -ForegroundColor Gray
Write-Host ""
Write-Host "  [tts]" -ForegroundColor Gray
Write-Host "  provider = `"kokoro`"" -ForegroundColor Gray
Write-Host ""
