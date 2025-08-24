# MCP Speech-to-Text Server Startup Script (PowerShell)
# Compatible with PowerShell 5.1+ and PowerShell Core

param(
    [string]$WhisperModelSize = $env:WHISPER_MODEL_SIZE ?? "base",
    [string]$DefaultLanguage = $env:DEFAULT_LANGUAGE ?? "auto",
    [string]$LogLevel = $env:LOG_LEVEL ?? "INFO",
    [switch]$SkipModelDownload,
    [switch]$NoPause,
    [switch]$Verbose,
    [switch]$Dev
)

# Enable strict mode
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

if ($Verbose) {
    $VerbosePreference = "Continue"
}

# Function to write colored output
function Write-ColorOutput {
    param(
        [string]$Message,
        [string]$Color = "White",
        [string]$Prefix = ""
    )
    
    if ($Prefix) {
        Write-Host "$Prefix " -ForegroundColor $Color -NoNewline
        Write-Host $Message -ForegroundColor White
    } else {
        Write-Host $Message -ForegroundColor $Color
    }
}

# Function to test if command exists
function Test-Command {
    param([string]$Command)
    try {
        Get-Command $Command -ErrorAction Stop | Out-Null
        return $true
    } catch {
        return $false
    }
}

Write-Host "🎤 MCP Speech-to-Text Server v1.0.0" -ForegroundColor Green
Write-Host "====================================" -ForegroundColor Green
Write-Host ""Text Server Startup Script (PowerShell)
# Compatible with PowerShell 5.1+ and PowerShell Core

param(
    [string]$WhisperModelSize = $env:WHISPER_MODEL_SIZE ?? "base",
    [string]$DefaultLanguage = $env:DEFAULT_LANGUAGE ?? "auto",
    [string]$LogLevel = $env:LOG_LEVEL ?? "INFO"
)

# Enable strict mode
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

Write-Host "🎤 MCP Speech-to-Text Server v1.0.0" -ForegroundColor Green
Write-Host "==================================" -ForegroundColor Green
Write-Host ""

# Check if Python is installed
Write-Verbose "Checking Python installation..."
try {
    $pythonVersion = python --version 2>&1
    if ($LASTEXITCODE -ne 0) { throw }
    Write-ColorOutput "✅" "Green" "Python found: $pythonVersion"
} catch {
    Write-ColorOutput "❌ Python is not installed or not in PATH" "Red"
    Write-ColorOutput "Please install Python from: https://www.python.org/downloads/" "Yellow"
    if (-not $NoPause) { Read-Host "Press Enter to exit" }
    exit 1
}

# Check if uv is installed
Write-Verbose "Checking uv installation..."
try {
    $uvVersion = uv --version 2>&1
    if ($LASTEXITCODE -ne 0) { throw }
    Write-ColorOutput "✅" "Green" "uv found: $uvVersion"
} catch {
    Write-ColorOutput "⚠️ uv is not installed." "Yellow"
    Write-ColorOutput "Installing uv via pip..." "Cyan"
    try {
        pip install uv
        $uvVersion = uv --version 2>&1
        Write-ColorOutput "✅" "Green" "uv installed successfully: $uvVersion"
    } catch {
        Write-ColorOutput "❌ Failed to install uv. Please install manually:" "Red"
        Write-ColorOutput "Visit: https://github.com/astral-sh/uv" "Yellow"
        if (-not $NoPause) { Read-Host "Press Enter to exit" }
        exit 1
    }
}

# Set environment variables
$env:WHISPER_MODEL_SIZE = $WhisperModelSize
$env:DEFAULT_LANGUAGE = $DefaultLanguage
$env:LOG_LEVEL = $LogLevel

Write-ColorOutput "📋 Configuration:" "Yellow"
Write-Host "  Whisper Model: $WhisperModelSize" -ForegroundColor White
Write-Host "  Default Language: $DefaultLanguage" -ForegroundColor White
Write-Host "  Log Level: $LogLevel" -ForegroundColor White
if ($Dev) {
    Write-Host "  Development Mode: Enabled" -ForegroundColor Magenta
}
Write-Host ""

# Check if running in Docker
if ($env:DOCKER_CONTAINER) {
    Write-ColorOutput "🐳 Running in Docker container" "Cyan"
    $env:PYTHONPATH = "/app/src"
    Set-Location "/app"
} else {
    Write-ColorOutput "💻 Running locally on Windows (PowerShell)" "Cyan"
    Write-Host ""
    
    # Create virtual environment if it doesn't exist
    if (-not (Test-Path ".venv")) {
        Write-ColorOutput "📦 Creating virtual environment..." "Yellow"
        try {
            uv venv
            Write-ColorOutput "✅ Virtual environment created" "Green"
        } catch {
            Write-ColorOutput "❌ Failed to create virtual environment: $_" "Red"
            if (-not $NoPause) { Read-Host "Press Enter to exit" }
            exit 1
        }
    } else {
        Write-ColorOutput "✅ Virtual environment exists" "Green"
    }
    
    # Activate virtual environment and install dependencies
    Write-ColorOutput "📦 Setting up dependencies..." "Yellow"
    
    $activateScript = ".venv\Scripts\Activate.ps1"
    if (Test-Path $activateScript) {
        try {
            Write-Verbose "Activating virtual environment..."
            & $activateScript
            Write-ColorOutput "✅ Virtual environment activated" "Green"
        } catch {
            Write-ColorOutput "❌ Failed to activate virtual environment: $_" "Red"
            Write-ColorOutput "You may need to enable script execution:" "Yellow"
            Write-Host "  Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser" -ForegroundColor Cyan
            if (-not $NoPause) { Read-Host "Press Enter to exit" }
            exit 1
        }
    } else {
        Write-ColorOutput "❌ Virtual environment activation script not found" "Red"
        if (-not $NoPause) { Read-Host "Press Enter to exit" }
        exit 1
    }
    
    try {
        Write-Verbose "Installing project dependencies..."
        if ($Dev) {
            uv pip install -e ".[dev]"
            Write-ColorOutput "✅ Development dependencies installed" "Green"
        } else {
            uv pip install -e .
            Write-ColorOutput "✅ Dependencies installed" "Green"
        }
    } catch {
        Write-ColorOutput "❌ Failed to install dependencies: $_" "Red"
        if (-not $NoPause) { Read-Host "Press Enter to exit" }
        exit 1
    }
    
    # Set PYTHONPATH for Windows
    $env:PYTHONPATH = "$PWD\src"
    Write-Verbose "PYTHONPATH set to: $env:PYTHONPATH"
}

# Download Whisper model if needed
if (-not $SkipModelDownload) {
    Write-ColorOutput "🤖 Checking Whisper model..." "Yellow"
    try {
        python -c "import whisper; whisper.load_model('$WhisperModelSize')" 2>$null
        Write-ColorOutput "✅ Whisper model ready" "Green"
    } catch {
        Write-ColorOutput "📥 Downloading Whisper model ($WhisperModelSize)..." "Cyan"
        Write-Host "   This may take a few minutes depending on model size and internet speed..." -ForegroundColor Gray
        try {
            python -c "import whisper; print(f'Loading {'''$WhisperModelSize'''} model...'); model = whisper.load_model('$WhisperModelSize'); print(f'Model loaded successfully: {model.__class__.__name__}')"
            Write-ColorOutput "✅ Whisper model downloaded and verified" "Green"
        } catch {
            Write-ColorOutput "❌ Failed to download Whisper model: $_" "Red"
            Write-ColorOutput "Check your internet connection and try again" "Yellow"
            if (-not $NoPause) { Read-Host "Press Enter to exit" }
            exit 1
        }
    }
} else {
    Write-ColorOutput "⏭️ Skipping Whisper model download" "Yellow"
}

Write-ColorOutput "✅ Setup complete!" "Green"
Write-ColorOutput "🚀 Starting MCP Speech-to-Text server..." "Green"
Write-Host ""

if ($Dev) {
    Write-ColorOutput "🔧 Development mode enabled" "Magenta"
    Write-Host "   - Verbose logging activated" -ForegroundColor Gray
    Write-Host "   - Development dependencies loaded" -ForegroundColor Gray
    Write-Host ""
}

Write-Host "📡 Server will be available at: http://localhost:8000" -ForegroundColor Cyan
Write-Host "🛑 Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

# Start the server
try {
    if ($Verbose -or $Dev) {
        $env:LOG_LEVEL = "DEBUG"
    }
    
    python -m mcp_speech_to_text.server
} catch {
    Write-ColorOutput "❌ Server failed to start: $_" "Red"
    Write-Host ""
    Write-Host "Troubleshooting tips:" -ForegroundColor Yellow
    Write-Host "  1. Check if all dependencies are installed: uv pip list" -ForegroundColor Gray
    Write-Host "  2. Verify Python path: python -c 'import sys; print(sys.path)'" -ForegroundColor Gray
    Write-Host "  3. Check for port conflicts: netstat -an | findstr :8000" -ForegroundColor Gray
    Write-Host "  4. Run with verbose logging: .\start.ps1 -Verbose" -ForegroundColor Gray
    
    if (-not $NoPause) { Read-Host "Press Enter to exit" }
    exit 1
} finally {
    Write-Host ""
    Write-ColorOutput "👋 Server stopped" "Yellow"
    if (-not $NoPause) {
        Read-Host "Press Enter to exit"
    }
}
