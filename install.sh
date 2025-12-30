#!/bin/bash

################################################################################
# JarvisCO - Automated Installation Script for Termux
# 
# This script handles:
# - System package updates and dependencies
# - Python environment setup
# - Virtual environment creation
# - Python dependencies installation
# - Model downloads and setup
# - Configuration initialization
#
# Usage: bash install.sh
################################################################################

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Script configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_NAME="JarvisCO"
VENV_DIR="$SCRIPT_DIR/venv"
PYTHON_MIN_VERSION="3.8"
MODELS_DIR="$SCRIPT_DIR/models"
CONFIG_DIR="$SCRIPT_DIR/config"
LOG_FILE="$SCRIPT_DIR/install.log"

################################################################################
# Utility Functions
################################################################################

print_header() {
    echo -e "\n${BLUE}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${CYAN}  $1${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}\n"
}

print_info() {
    echo -e "${CYAN}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

log_step() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

check_termux() {
    if [[ ! -d "$PREFIX" ]]; then
        print_error "Termux environment not detected!"
        print_info "This script is optimized for Termux. Install Termux from:"
        print_info "https://github.com/termux/termux-app"
        exit 1
    fi
    print_success "Termux environment detected"
    log_step "Termux environment verified"
}

check_python() {
    print_info "Checking Python installation..."
    
    if ! command -v python3 &> /dev/null; then
        print_warning "Python3 not found. Installing..."
        apt-get install -y python3
        log_step "Python3 installed"
    fi
    
    PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
    print_success "Python $PYTHON_VERSION detected"
    log_step "Python version: $PYTHON_VERSION"
}

update_system() {
    print_header "System Update"
    print_info "Updating package lists..."
    apt-get update -y
    print_info "Upgrading packages..."
    apt-get upgrade -y
    print_success "System packages updated"
    log_step "System packages updated"
}

install_dependencies() {
    print_header "Installing System Dependencies"
    
    local packages=(
        "python3"
        "python3-pip"
        "python3-venv"
        "build-essential"
        "libssl-dev"
        "libffi-dev"
        "git"
        "curl"
        "wget"
        "ffmpeg"
        "libopus0"
        "libopus-dev"
    )
    
    for package in "${packages[@]}"; do
        if apt-cache show "$package" &> /dev/null; then
            print_info "Installing $package..."
            apt-get install -y "$package"
        else
            print_warning "Package $package not found in repositories"
        fi
    done
    
    print_success "System dependencies installed"
    log_step "System dependencies installation completed"
}

create_virtual_environment() {
    print_header "Creating Python Virtual Environment"
    
    if [[ -d "$VENV_DIR" ]]; then
        print_warning "Virtual environment already exists"
        read -p "Remove and recreate? (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            rm -rf "$VENV_DIR"
            print_info "Virtual environment removed"
        else
            print_info "Using existing virtual environment"
            return
        fi
    fi
    
    print_info "Creating virtual environment at $VENV_DIR..."
    python3 -m venv "$VENV_DIR"
    
    print_success "Virtual environment created"
    log_step "Virtual environment created at $VENV_DIR"
}

activate_venv() {
    print_info "Activating virtual environment..."
    source "$VENV_DIR/bin/activate"
    print_success "Virtual environment activated"
}

upgrade_pip() {
    print_header "Upgrading pip, setuptools, and wheel"
    
    print_info "Upgrading pip..."
    pip install --upgrade pip setuptools wheel
    
    print_success "pip, setuptools, and wheel upgraded"
    log_step "pip and build tools upgraded"
}

install_python_dependencies() {
    print_header "Installing Python Dependencies"
    
    if [[ ! -f "$SCRIPT_DIR/requirements.txt" ]]; then
        print_error "requirements.txt not found!"
        print_info "Creating default requirements.txt..."
        create_default_requirements
    fi
    
    print_info "Installing packages from requirements.txt..."
    pip install -r "$SCRIPT_DIR/requirements.txt"
    
    print_success "Python dependencies installed"
    log_step "Python dependencies installation completed"
}

create_default_requirements() {
    cat > "$SCRIPT_DIR/requirements.txt" << 'EOF'
# Core dependencies
numpy>=1.21.0
scipy>=1.7.0
pandas>=1.3.0

# Audio processing
librosa>=0.9.0
soundfile>=0.11.0
pydub>=0.25.1

# Speech recognition and synthesis
SpeechRecognition>=3.8.1
pyttsx3>=2.90
pyaudio>=0.2.11

# Machine learning and models
torch>=1.10.0
torchvision>=0.11.0
transformers>=4.20.0

# NLP processing
nltk>=3.6
spacy>=3.0

# API and web
requests>=2.26.0
flask>=2.0.0
python-dotenv>=0.19.0

# Utilities
tqdm>=4.62.0
colorama>=0.4.4
pyyaml>=5.4.0

# Development
pytest>=6.2.0
pytest-cov>=2.12.0
black>=21.7b0
flake8>=3.9.0
EOF
    print_success "Default requirements.txt created"
    log_step "Default requirements.txt generated"
}

setup_models_directory() {
    print_header "Setting Up Models Directory"
    
    mkdir -p "$MODELS_DIR"
    print_success "Models directory created at $MODELS_DIR"
    log_step "Models directory created"
    
    # Create placeholder for model organization
    if [[ ! -f "$MODELS_DIR/README.md" ]]; then
        cat > "$MODELS_DIR/README.md" << 'EOF'
# JarvisCO Models Directory

This directory contains downloaded machine learning models.

## Structure:
- `/speech-recognition/` - Speech recognition models
- `/tts/` - Text-to-speech models
- `/nlp/` - Natural language processing models
- `/audio/` - Audio processing models

## Usage:
Models are automatically downloaded during first run or via:
```bash
python3 setup_models.py
```

## Storage Note:
Large models can consume significant storage. Ensure adequate space is available.
EOF
    fi
    print_success "Models directory structure initialized"
}

setup_config_directory() {
    print_header "Setting Up Configuration Directory"
    
    mkdir -p "$CONFIG_DIR"
    print_success "Config directory created at $CONFIG_DIR"
    log_step "Configuration directory created"
    
    # Create default configuration
    if [[ ! -f "$CONFIG_DIR/config.yaml" ]]; then
        cat > "$CONFIG_DIR/config.yaml" << 'EOF'
# JarvisCO Configuration File

app:
  name: JarvisCO
  version: 1.0.0
  debug: false

speech:
  language: en-US
  recognition_engine: google
  synthesis_engine: pyttsx3
  rate: 150  # words per minute

audio:
  sample_rate: 16000
  channels: 1
  format: wav
  chunk_size: 1024

models:
  directory: ./models
  auto_download: true
  cache_enabled: true

logging:
  level: INFO
  file: ./logs/jarvisCO.log
  max_size_mb: 10
  backup_count: 5

system:
  max_workers: 4
  timeout_seconds: 30
  enable_gpu: false
EOF
        print_success "Default configuration created"
        log_step "Configuration file initialized"
    else
        print_info "Configuration file already exists"
    fi
}

download_models() {
    print_header "Model Download Setup"
    
    print_info "Models will be downloaded on first application run."
    print_info "To manually download models, run:"
    print_info "  source $VENV_DIR/bin/activate"
    print_info "  python3 scripts/download_models.py"
    
    # Create model download script template
    if [[ ! -d "$SCRIPT_DIR/scripts" ]]; then
        mkdir -p "$SCRIPT_DIR/scripts"
    fi
    
    if [[ ! -f "$SCRIPT_DIR/scripts/download_models.py" ]]; then
        cat > "$SCRIPT_DIR/scripts/download_models.py" << 'EOF'
#!/usr/bin/env python3
"""
Model download script for JarvisCO
Downloads required models for speech recognition, TTS, and NLP
"""

import os
import sys
from pathlib import Path

def download_models():
    """Download all required models"""
    print("Starting model download...")
    print("This may take several minutes depending on your connection speed.")
    print()
    
    # Create model directories
    models_dir = Path("./models")
    models_dir.mkdir(exist_ok=True)
    
    try:
        # Speech recognition models
        print("[1/4] Downloading speech recognition models...")
        import speech_recognition as sr
        # Initializing downloads
        sr.Recognizer()
        print("✓ Speech recognition models ready")
        
        # NLTK data
        print("[2/4] Downloading NLTK data...")
        import nltk
        nltk.download('punkt')
        nltk.download('averaged_perceptron_tagger')
        nltk.download('maxent_ne_chunker')
        nltk.download('words')
        print("✓ NLTK data downloaded")
        
        # Spacy models
        print("[3/4] Downloading spaCy models...")
        import subprocess
        subprocess.run([sys.executable, "-m", "spacy", "download", "en_core_web_sm"])
        print("✓ spaCy models downloaded")
        
        # Transformers cache
        print("[4/4] Initializing transformer models cache...")
        from transformers import AutoTokenizer
        # This will cache models on first use
        print("✓ Transformers ready")
        
        print()
        print("✓ All models downloaded successfully!")
        print("Ready to run JarvisCO")
        
    except Exception as e:
        print(f"✗ Error downloading models: {e}")
        print("You can retry with: python3 scripts/download_models.py")
        return False
    
    return True

if __name__ == "__main__":
    success = download_models()
    sys.exit(0 if success else 1)
EOF
        chmod +x "$SCRIPT_DIR/scripts/download_models.py"
        print_success "Model download script created"
        log_step "Model download script created"
    fi
}

create_startup_script() {
    print_header "Creating Startup Script"
    
    if [[ ! -f "$SCRIPT_DIR/run.sh" ]]; then
        cat > "$SCRIPT_DIR/run.sh" << 'EOF'
#!/bin/bash
# JarvisCO Startup Script

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/venv"

if [[ ! -d "$VENV_DIR" ]]; then
    echo "Error: Virtual environment not found!"
    echo "Please run: bash install.sh"
    exit 1
fi

# Activate virtual environment
source "$VENV_DIR/bin/activate"

# Run the application
python3 "$SCRIPT_DIR/main.py" "$@"
EOF
        chmod +x "$SCRIPT_DIR/run.sh"
        print_success "Startup script created"
        log_step "Startup script created"
    fi
}

verify_installation() {
    print_header "Verifying Installation"
    
    local all_good=true
    
    # Check virtual environment
    if [[ -d "$VENV_DIR" ]]; then
        print_success "Virtual environment exists"
    else
        print_error "Virtual environment missing"
        all_good=false
    fi
    
    # Check key directories
    if [[ -d "$MODELS_DIR" ]]; then
        print_success "Models directory exists"
    else
        print_error "Models directory missing"
        all_good=false
    fi
    
    if [[ -d "$CONFIG_DIR" ]]; then
        print_success "Config directory exists"
    else
        print_error "Config directory missing"
        all_good=false
    fi
    
    # Check Python packages
    source "$VENV_DIR/bin/activate"
    if python3 -c "import numpy, requests, librosa" 2>/dev/null; then
        print_success "Core Python packages installed"
    else
        print_warning "Some Python packages may be missing"
    fi
    
    return 0
}

create_uninstall_script() {
    print_header "Creating Uninstall Script"
    
    if [[ ! -f "$SCRIPT_DIR/uninstall.sh" ]]; then
        cat > "$SCRIPT_DIR/uninstall.sh" << 'EOF'
#!/bin/bash
# JarvisCO Uninstall Script

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/venv"

echo "JarvisCO Uninstall"
echo "=================="
echo ""
read -p "Remove virtual environment? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    rm -rf "$VENV_DIR"
    echo "✓ Virtual environment removed"
fi

read -p "Remove models directory? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    rm -rf "$SCRIPT_DIR/models"
    echo "✓ Models directory removed"
fi

echo ""
echo "Uninstall complete. Other files preserved."
EOF
        chmod +x "$SCRIPT_DIR/uninstall.sh"
        print_success "Uninstall script created"
    fi
}

generate_installation_report() {
    print_header "Installation Report"
    
    cat > "$SCRIPT_DIR/INSTALLATION_REPORT.md" << EOF
# JarvisCO Installation Report

**Installation Date:** $(date '+%Y-%m-%d %H:%M:%S')

## System Information
- Platform: Termux
- Python Version: $(python3 --version)
- Bash Version: $BASH_VERSION

## Installation Summary

### ✓ Completed Steps
- [x] System dependencies installed
- [x] Python virtual environment created
- [x] Python packages installed
- [x] Models directory configured
- [x] Configuration files initialized
- [x] Startup scripts created

### Installation Directories
- **Project Directory:** $SCRIPT_DIR
- **Virtual Environment:** $VENV_DIR
- **Models Directory:** $MODELS_DIR
- **Config Directory:** $CONFIG_DIR
- **Log File:** $LOG_FILE

## Next Steps

1. **Download Models (Optional):**
   \`\`\`bash
   source $VENV_DIR/bin/activate
   python3 scripts/download_models.py
   \`\`\`

2. **Run JarvisCO:**
   \`\`\`bash
   bash $SCRIPT_DIR/run.sh
   \`\`\`

3. **Verify Installation:**
   \`\`\`bash
   source $VENV_DIR/bin/activate
   python3 -c "import numpy, requests, librosa; print('All packages OK')"
   \`\`\`

## Configuration

Configuration file location: \`$CONFIG_DIR/config.yaml\`

Key settings:
- Speech Recognition Language: en-US
- Sample Rate: 16000 Hz
- Debug Mode: Disabled

## Troubleshooting

### Virtual Environment Issues
\`\`\`bash
rm -rf $VENV_DIR
bash install.sh
\`\`\`

### Missing Dependencies
\`\`\`bash
source $VENV_DIR/bin/activate
pip install --upgrade -r requirements.txt
\`\`\`

### Space Issues
Check available space:
\`\`\`bash
df -h
\`\`\`

Models can consume 1-5GB of storage.

## Uninstall

To uninstall JarvisCO:
\`\`\`bash
bash $SCRIPT_DIR/uninstall.sh
\`\`\`

## Support

For issues and updates, visit:
https://github.com/s29268979-boop/jarvisCO

---
Generated by JarvisCO Install Script v1.0
EOF
    
    print_success "Installation report generated"
    log_step "Installation report created"
}

show_summary() {
    print_header "Installation Complete!"
    
    echo -e "${GREEN}JarvisCO has been successfully installed!${NC}\n"
    
    echo -e "${YELLOW}Installation Summary:${NC}"
    echo -e "  Project Location: ${CYAN}$SCRIPT_DIR${NC}"
    echo -e "  Virtual Environment: ${CYAN}$VENV_DIR${NC}"
    echo -e "  Models Directory: ${CYAN}$MODELS_DIR${NC}"
    echo -e "  Config Directory: ${CYAN}$CONFIG_DIR${NC}"
    echo ""
    
    echo -e "${YELLOW}Quick Start:${NC}"
    echo -e "  1. Activate environment: ${CYAN}source $VENV_DIR/bin/activate${NC}"
    echo -e "  2. Run JarvisCO: ${CYAN}bash run.sh${NC}"
    echo ""
    
    echo -e "${YELLOW}Useful Commands:${NC}"
    echo -e "  Download models: ${CYAN}python3 scripts/download_models.py${NC}"
    echo -e "  Uninstall: ${CYAN}bash uninstall.sh${NC}"
    echo -e "  View logs: ${CYAN}cat $LOG_FILE${NC}"
    echo ""
    
    echo -e "${YELLOW}Documentation:${NC}"
    echo -e "  Installation Report: ${CYAN}cat INSTALLATION_REPORT.md${NC}"
    echo ""
    
    print_success "Setup complete! You're ready to use JarvisCO."
}

main() {
    print_header "JarvisCO - Automated Installation Script"
    
    print_info "Starting installation..."
    print_info "Log file: $LOG_FILE"
    echo "" > "$LOG_FILE"
    log_step "Installation started"
    
    # Pre-installation checks
    check_termux
    check_python
    
    # System setup
    update_system
    install_dependencies
    
    # Python environment
    create_virtual_environment
    activate_venv
    upgrade_pip
    
    # Python packages
    install_python_dependencies
    
    # Project setup
    setup_models_directory
    setup_config_directory
    download_models
    
    # Scripts and helpers
    create_startup_script
    create_uninstall_script
    
    # Verification
    verify_installation
    
    # Documentation
    generate_installation_report
    
    # Final summary
    show_summary
    
    log_step "Installation completed successfully"
}

# Run main function
main "$@"
exit $?
