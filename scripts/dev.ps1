# MCP Speech-to-Text Development Helper Script (PowerShell)
# Provides various development utilities and shortcuts

param(
    [Parameter(Position = 0)]
    [ValidateSet("build", "start", "test", "lint", "format", "clean", "install", "status", "help")]
    [string]$Command = "help",
    
    [switch]$Verbose,
    [switch]$NoPause,
    [switch]$Force
)

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

function Show-Help {
    Write-Host "🛠️  MCP Speech-to-Text Development Helper" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Usage: .\dev.ps1 <command> [options]" -ForegroundColor White
    Write-Host ""
    Write-Host "Commands:" -ForegroundColor Yellow
    Write-Host "  build    - Build Docker image" -ForegroundColor White
    Write-Host "  start    - Start the development server" -ForegroundColor White
    Write-Host "  test     - Run tests" -ForegroundColor White
    Write-Host "  lint     - Run linting checks" -ForegroundColor White
    Write-Host "  format   - Format code" -ForegroundColor White
    Write-Host "  clean    - Clean build artifacts" -ForegroundColor White
    Write-Host "  install  - Install/update dependencies" -ForegroundColor White
    Write-Host "  status   - Show project status" -ForegroundColor White
    Write-Host "  help     - Show this help" -ForegroundColor White
    Write-Host ""
    Write-Host "Options:" -ForegroundColor Yellow
    Write-Host "  -Verbose   Enable verbose output" -ForegroundColor White
    Write-Host "  -NoPause   Don't pause after completion" -ForegroundColor White
    Write-Host "  -Force     Force operation (where applicable)" -ForegroundColor White
    Write-Host ""
    Write-Host "Examples:" -ForegroundColor Yellow
    Write-Host "  .\dev.ps1 build -Verbose" -ForegroundColor Gray
    Write-Host "  .\dev.ps1 start" -ForegroundColor Gray
    Write-Host "  .\dev.ps1 test -NoPause" -ForegroundColor Gray
}

function Invoke-Build {
    Write-ColorOutput "🐳 Building Docker image..." "Cyan"
    if ($Verbose) {
        & ".\build.ps1" -Verbose -NoPause
    } else {
        & ".\build.ps1" -NoPause
    }
}

function Invoke-Start {
    Write-ColorOutput "🚀 Starting development server..." "Green"
    $params = @("-Dev")
    if ($Verbose) { $params += "-Verbose" }
    if ($NoPause) { $params += "-NoPause" }
    
    & ".\start.ps1" @params
}

function Invoke-Test {
    Write-ColorOutput "🧪 Running tests..." "Yellow"
    
    if (-not (Test-Path ".venv\Scripts\Activate.ps1")) {
        Write-ColorOutput "❌ Virtual environment not found. Run: .\dev.ps1 install" "Red"
        return
    }
    
    try {
        & ".venv\Scripts\Activate.ps1"
        
        Write-Host "Running unit tests..." -ForegroundColor Gray
        python -m pytest tests/ -v
        
        Write-Host "Running integration tests..." -ForegroundColor Gray
        python test_server.py
        
        Write-ColorOutput "✅ All tests completed" "Green"
    } catch {
        Write-ColorOutput "❌ Tests failed: $_" "Red"
    }
}

function Invoke-Lint {
    Write-ColorOutput "🔍 Running linting checks..." "Yellow"
    
    if (-not (Test-Path ".venv\Scripts\Activate.ps1")) {
        Write-ColorOutput "❌ Virtual environment not found. Run: .\dev.ps1 install" "Red"
        return
    }
    
    try {
        & ".venv\Scripts\Activate.ps1"
        
        Write-Host "Running ruff..." -ForegroundColor Gray
        python -m ruff check src/ tests/
        
        Write-Host "Running mypy..." -ForegroundColor Gray
        python -m mypy src/
        
        Write-ColorOutput "✅ Linting completed" "Green"
    } catch {
        Write-ColorOutput "❌ Linting failed: $_" "Red"
    }
}

function Invoke-Format {
    Write-ColorOutput "✨ Formatting code..." "Magenta"
    
    if (-not (Test-Path ".venv\Scripts\Activate.ps1")) {
        Write-ColorOutput "❌ Virtual environment not found. Run: .\dev.ps1 install" "Red"
        return
    }
    
    try {
        & ".venv\Scripts\Activate.ps1"
        
        Write-Host "Running black..." -ForegroundColor Gray
        python -m black src/ tests/
        
        Write-Host "Running ruff fix..." -ForegroundColor Gray
        python -m ruff check --fix src/ tests/
        
        Write-ColorOutput "✅ Code formatted" "Green"
    } catch {
        Write-ColorOutput "❌ Formatting failed: $_" "Red"
    }
}

function Invoke-Clean {
    Write-ColorOutput "🧹 Cleaning build artifacts..." "Yellow"
    
    $itemsToClean = @(
        "__pycache__",
        "*.pyc",
        "*.pyo",
        "*.pyd",
        ".pytest_cache",
        "build",
        "dist",
        "*.egg-info",
        ".coverage",
        ".mypy_cache",
        ".ruff_cache"
    )
    
    foreach ($item in $itemsToClean) {
        Get-ChildItem -Recurse -Force -Name $item -ErrorAction SilentlyContinue | 
        ForEach-Object {
            Write-Verbose "Removing: $_"
            Remove-Item $_ -Recurse -Force -ErrorAction SilentlyContinue
        }
    }
    
    if ($Force -and (Test-Path ".venv")) {
        Write-Host "Removing virtual environment..." -ForegroundColor Gray
        Remove-Item ".venv" -Recurse -Force
    }
    
    Write-ColorOutput "✅ Cleanup completed" "Green"
}

function Invoke-Install {
    Write-ColorOutput "📦 Installing/updating dependencies..." "Cyan"
    
    try {
        if (-not (Test-Path ".venv")) {
            Write-Host "Creating virtual environment..." -ForegroundColor Gray
            uv venv
        }
        
        & ".venv\Scripts\Activate.ps1"
        
        Write-Host "Installing development dependencies..." -ForegroundColor Gray
        uv pip install -e ".[dev]"
        
        Write-ColorOutput "✅ Dependencies installed" "Green"
    } catch {
        Write-ColorOutput "❌ Installation failed: $_" "Red"
    }
}

function Show-Status {
    Write-Host "📊 Project Status" -ForegroundColor Green
    Write-Host "=================" -ForegroundColor Green
    Write-Host ""
    
    # Python version
    try {
        $pythonVersion = python --version 2>&1
        Write-Host "Python: $pythonVersion" -ForegroundColor White
    } catch {
        Write-Host "Python: Not found" -ForegroundColor Red
    }
    
    # UV version
    try {
        $uvVersion = uv --version 2>&1
        Write-Host "UV: $uvVersion" -ForegroundColor White
    } catch {
        Write-Host "UV: Not found" -ForegroundColor Red
    }
    
    # Virtual environment
    if (Test-Path ".venv") {
        Write-Host "Virtual Environment: ✅ Exists" -ForegroundColor Green
        
        try {
            & ".venv\Scripts\Activate.ps1"
            $packages = uv pip list
            $packageCount = ($packages | Measure-Object).Count - 2  # Subtract header lines
            Write-Host "Installed Packages: $packageCount" -ForegroundColor White
        } catch {
            Write-Host "Virtual Environment: ⚠️ Cannot activate" -ForegroundColor Yellow
        }
    } else {
        Write-Host "Virtual Environment: ❌ Not found" -ForegroundColor Red
    }
    
    # Docker
    try {
        docker --version | Out-Null
        Write-Host "Docker: ✅ Available" -ForegroundColor Green
        
        $images = docker images mcp-speech-to-text --format "table {{.Tag}}" 2>$null | Select-Object -Skip 1
        if ($images) {
            Write-Host "Docker Images: $($images -join ', ')" -ForegroundColor White
        } else {
            Write-Host "Docker Images: None built" -ForegroundColor Gray
        }
    } catch {
        Write-Host "Docker: ❌ Not available" -ForegroundColor Red
    }
    
    # Project files
    $projectFiles = @(
        "pyproject.toml",
        "src/mcp_speech_to_text/server.py",
        "tests/test_server.py",
        "Dockerfile"
    )
    
    Write-Host ""
    Write-Host "Project Files:" -ForegroundColor Yellow
    foreach ($file in $projectFiles) {
        if (Test-Path $file) {
            Write-Host "  ✅ $file" -ForegroundColor Green
        } else {
            Write-Host "  ❌ $file" -ForegroundColor Red
        }
    }
}

# Main execution
try {
    switch ($Command) {
        "build" { Invoke-Build }
        "start" { Invoke-Start }
        "test" { Invoke-Test }
        "lint" { Invoke-Lint }
        "format" { Invoke-Format }
        "clean" { Invoke-Clean }
        "install" { Invoke-Install }
        "status" { Show-Status }
        "help" { Show-Help }
        default { Show-Help }
    }
} catch {
    Write-ColorOutput "❌ Command failed: $_" "Red"
    if (-not $NoPause) {
        Read-Host "Press Enter to exit"
    }
    exit 1
} finally {
    if (-not $NoPause -and $Command -ne "help") {
        Write-Host ""
        Read-Host "Press Enter to exit"
    }
}
