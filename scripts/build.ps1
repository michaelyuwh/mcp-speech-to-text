# Build script for MCP Speech-to-Text Docker image (PowerShell)
    # Check if Docker daemon is running
    Write-Verbose "Checking Docker daemon status..."
    try {
        docker info 2>&1 | Out-Null
        if ($LASTEXITCODE -ne 0) { throw "Docker daemon not running" }
        Write-ColorOutput "✅" "Green" "Docker daemon is running"
    } catch {tible with PowerShell 5.1+ and PowerShell Core

param(
    [switch]$Push,
    [string]$Registry = "",
    [switch]$NoPause,
    [switch]$Verbose
)

# Enable strict mode and better error handling
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

if ($Verbose) {
    $VerbosePreference = "Continue"
}

Write-Host "🐳 MCP Speech-to-Text Docker Build Script" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Green
Write-Host ""

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

# Function to check if command exists
function Test-Command {
    param([string]$Command)
    
    try {
        Get-Command $Command -ErrorAction Stop | Out-Null
        return $true
    } catch {
        return $false
    }
}

try {
    # Check if Docker is installed
    Write-Verbose "Checking Docker installation..."
    if (-not (Test-Command "docker")) {
        Write-ColorOutput "❌ Error: Docker is not installed or not in PATH" "Red"
        Write-ColorOutput "Please install Docker Desktop from: https://www.docker.com/products/docker-desktop" "Yellow"
        if (-not $NoPause) { Read-Host "Press Enter to exit" }
        exit 1
    }
    
    Write-ColorOutput "✅" "Green" "Docker found:"
    $dockerVersion = docker --version
    Write-Host "   $dockerVersion" -ForegroundColor Gray
    
    # Check if Docker daemon is running
    Write-Verbose "Checking Docker daemon status..."
    try {
        $dockerInfo = docker info 2>&1
        if ($LASTEXITCODE -ne 0) { throw "Docker daemon not running" }
        Write-ColorOutput "✅" "Green" "Docker daemon is running"
    } catch {
        Write-ColorOutput "❌ Error: Docker daemon is not running" "Red"
        Write-ColorOutput "Please start Docker Desktop" "Yellow"
        if (-not $NoPause) { Read-Host "Press Enter to exit" }
        exit 1
    }
    
    # Get version from pyproject.toml
    Write-Verbose "Parsing version from pyproject.toml..."
    $version = "1.0.0"  # Default fallback
    
    if (Test-Path "pyproject.toml") {
        try {
            $content = Get-Content "pyproject.toml" -Raw
            if ($content -match 'version\s*=\s*"([^"]+)"') {
                $version = $matches[1]
                Write-ColorOutput "✅" "Green" "Version parsed: $version"
            } else {
                Write-ColorOutput "⚠️" "Yellow" "Could not parse version from pyproject.toml, using default: $version"
            }
        } catch {
            Write-ColorOutput "⚠️" "Yellow" "Error reading pyproject.toml, using default version: $version"
        }
    } else {
        Write-ColorOutput "⚠️" "Yellow" "pyproject.toml not found, using default version: $version"
    }
    
    # Set image names
    $imageName = "mcp-speech-to-text"
    $fullImageName = if ($Registry) { "$Registry/$imageName" } else { $imageName }
    $taggedImage = "${fullImageName}:${version}"
    $latestImage = "${fullImageName}:latest"
    
    Write-Host ""
    Write-ColorOutput "📦 Building Docker image..." "Cyan"
    Write-Host "   Image: $taggedImage" -ForegroundColor Gray
    Write-Host ""
    
    # Build the Docker image
    Write-Verbose "Starting Docker build..."
    $buildArgs = @(
        "build",
        "-t", $taggedImage,
        "."
    )
    
    if ($Verbose) {
        $buildArgs += "--progress=plain"
    }
    
    & docker @buildArgs
    
    if ($LASTEXITCODE -ne 0) {
        Write-ColorOutput "❌ Docker build failed" "Red"
        if (-not $NoPause) { Read-Host "Press Enter to exit" }
        exit 1
    }
    
    Write-ColorOutput "✅ Build successful" "Green"
    
    # Tag as latest
    Write-Verbose "Tagging as latest..."
    docker tag $taggedImage $latestImage
    
    if ($LASTEXITCODE -eq 0) {
        Write-ColorOutput "🏷️" "Blue" "Tagged as latest"
    }
    
    Write-Host ""
    Write-ColorOutput "🎉 Docker images created successfully:" "Green"
    Write-Host "   • $taggedImage" -ForegroundColor White
    Write-Host "   • $latestImage" -ForegroundColor White
    
    # Display image information
    try {
        $imageInfo = docker images $imageName --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}\t{{.CreatedAt}}" | Select-Object -Skip 1
        if ($imageInfo) {
            Write-Host ""
            Write-ColorOutput "📊 Image Details:" "Cyan"
            Write-Host "   Repository`tTag`tSize`tCreated" -ForegroundColor Gray
            Write-Host "   $($imageInfo -replace "`t", "`t")" -ForegroundColor White
        }
    } catch {
        Write-Verbose "Could not retrieve image details"
    }
    
    # Push to registry if requested
    if ($Push) {
        Write-Host ""
        Write-ColorOutput "📤 Pushing to registry..." "Cyan"
        
        try {
            docker push $taggedImage
            docker push $latestImage
            Write-ColorOutput "✅ Successfully pushed to registry" "Green"
        } catch {
            Write-ColorOutput "❌ Failed to push to registry: $_" "Red"
            if (-not $NoPause) { Read-Host "Press Enter to continue" }
        }
    }
    
    Write-Host ""
    Write-ColorOutput "🚀 Next steps:" "Yellow"
    Write-Host ""
    Write-Host "   Start the container:" -ForegroundColor Gray
    Write-Host "     docker run -p 8000:8000 $taggedImage" -ForegroundColor White
    Write-Host ""
    Write-Host "   Or use Docker Compose:" -ForegroundColor Gray
    Write-Host "     docker-compose up -d" -ForegroundColor White
    Write-Host ""
    Write-Host "   For local development:" -ForegroundColor Gray
    Write-Host "     .\start.ps1" -ForegroundColor White
    Write-Host ""
    
    if ($Push) {
        Write-Host "   Registry images:" -ForegroundColor Gray
        Write-Host "     $taggedImage" -ForegroundColor White
        Write-Host "     $latestImage" -ForegroundColor White
        Write-Host ""
    }
    
    Write-ColorOutput "Build completed successfully! 🎉" "Green"

} catch {
    Write-ColorOutput "❌ Build failed with error: $_" "Red"
    Write-Host ""
    Write-Host "Stack trace:" -ForegroundColor Gray
    Write-Host $_.ScriptStackTrace -ForegroundColor Red
    
    if (-not $NoPause) { 
        Write-Host ""
        Read-Host "Press Enter to exit" 
    }
    exit 1
} finally {
    if (-not $NoPause) {
        Write-Host ""
        Read-Host "Press Enter to exit"
    }
}
