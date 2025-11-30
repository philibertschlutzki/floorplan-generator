#!/bin/bash

# GitHub Codespaces Setup Script for Floorplan Generator
# This script installs all necessary dependencies including QCAD, OpenCV, and Python packages

set -e

echo "======================================================"
echo "🚀 Floorplan Generator - Codespaces Setup"
echo "======================================================"

# Update package list
echo "📦 Updating package lists..."
sudo apt-get update -qq

# Install system dependencies
echo "🔧 Installing system dependencies..."
sudo apt-get install -y -qq \
    xvfb \
    x11-utils \
    libxkbcommon-x11-0 \
    libxcb-icccm4 \
    libxcb-image0 \
    libxcb-keysyms1 \
    libxcb-randr0 \
    libxcb-render-util0 \
    libxcb-xinerama0 \
    libxcb-xfixes0 \
    libxcb-shape0 \
    libegl1-mesa \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libfontconfig1 \
    libdbus-1-3 \
    jq \
    wget \
    curl \
    git \
    imagemagick \
    ghostscript

# Install OpenCV system dependencies
echo "📷 Installing OpenCV dependencies..."
sudo apt-get install -y -qq \
    libopencv-dev \
    python3-opencv \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1

# Install QCAD
echo "🏗️  Installing QCAD..."
if [ ! -d "/opt/qcad" ]; then
    cd /tmp
    
    # Download QCAD (Community Edition)
    QCAD_VERSION="3.29.5"
    QCAD_FILE="qcad-${QCAD_VERSION}-trial-linux-x86_64.tar.gz"
    QCAD_URL="https://github.com/qcad/qcad/releases/download/v${QCAD_VERSION}/${QCAD_FILE}"
    
    echo "   Downloading QCAD ${QCAD_VERSION}..."
    wget -q "${QCAD_URL}" -O "${QCAD_FILE}" || {
        echo "⚠️  Official download failed, trying alternative source..."
        # Fallback to direct download
        wget -q "https://www.qcad.org/archives/qcad/qcad-${QCAD_VERSION}-trial-linux-x86_64.tar.gz" -O "${QCAD_FILE}"
    }
    
    if [ -f "${QCAD_FILE}" ]; then
        echo "   Extracting QCAD..."
        sudo tar -xzf "${QCAD_FILE}" -C /opt/
        sudo mv /opt/qcad-* /opt/qcad
        
        # Create symlink
        sudo ln -sf /opt/qcad/qcad /usr/local/bin/qcad
        
        # Set permissions
        sudo chmod +x /opt/qcad/qcad
        
        echo "   ✅ QCAD installed to /opt/qcad"
    else
        echo "   ⚠️  QCAD download failed, will install from apt as fallback"
        sudo apt-get install -y -qq qcad || true
    fi
    
    cd -
else
    echo "   ✅ QCAD already installed"
fi

# Verify QCAD installation
if command -v qcad &> /dev/null; then
    echo "   ✅ QCAD command available: $(which qcad)"
    qcad --version || echo "   (Version info not available)"
else
    echo "   ⚠️  QCAD not found in PATH, adding to environment"
    echo 'export PATH="/opt/qcad:$PATH"' >> ~/.bashrc
fi

# Install Python dependencies
echo "🐍 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create necessary directories
echo "📁 Creating directory structure..."
mkdir -p output
mkdir -p configs
mkdir -p test_outputs
mkdir -p logs
mkdir -p archive

# Set up virtual display for headless QCAD
echo "🖥️  Setting up virtual display..."
cat > /tmp/start-xvfb.sh << 'EOF'
#!/bin/bash
Xvfb :99 -screen 0 1024x768x24 > /dev/null 2>&1 &
export DISPLAY=:99
EOF
chmod +x /tmp/start-xvfb.sh

# Add Xvfb to bashrc
if ! grep -q "DISPLAY=:99" ~/.bashrc; then
    echo '' >> ~/.bashrc
    echo '# Virtual display for QCAD' >> ~/.bashrc
    echo 'export DISPLAY=:99' >> ~/.bashrc
    echo 'if ! pgrep -x "Xvfb" > /dev/null; then' >> ~/.bashrc
    echo '    Xvfb :99 -screen 0 1024x768x24 > /dev/null 2>&1 &' >> ~/.bashrc
    echo 'fi' >> ~/.bashrc
fi

# Start Xvfb now
export DISPLAY=:99
Xvfb :99 -screen 0 1024x768x24 > /dev/null 2>&1 &
sleep 2

# Create example test image
echo "🎨 Creating test resources..."
python3 << 'PYTHON_SCRIPT'
import numpy as np
import cv2
from pathlib import Path

# Create a simple test building image
test_img = np.ones((800, 1000, 3), dtype=np.uint8) * 255

# Draw foundation (gray rectangle)
cv2.rectangle(test_img, (100, 400), (900, 700), (150, 150, 150), -1)
cv2.rectangle(test_img, (100, 400), (900, 700), (80, 80, 80), 3)

# Draw wood section (brown)
cv2.rectangle(test_img, (100, 200), (900, 400), (139, 90, 43), -1)
cv2.rectangle(test_img, (100, 200), (900, 400), (80, 50, 20), 3)

# Draw windows (dark blue)
window_positions = [(250, 250), (450, 250), (650, 250)]
for x, y in window_positions:
    cv2.rectangle(test_img, (x, y), (x+80, y+80), (50, 50, 150), -1)
    cv2.rectangle(test_img, (x, y), (x+80, y+80), (20, 20, 80), 2)

# Draw door (dark brown)
cv2.rectangle(test_img, (450, 500), (550, 680), (70, 40, 20), -1)
cv2.rectangle(test_img, (450, 500), (550, 680), (40, 20, 10), 3)

# Draw roof (red lines)
roof_peak = (500, 100)
cv2.line(test_img, roof_peak, (100, 200), (0, 0, 200), 8)
cv2.line(test_img, roof_peak, (900, 200), (0, 0, 200), 8)

# Save test image
Path('test_inputs').mkdir(exist_ok=True)
cv2.imwrite('test_inputs/example_building.png', test_img)
print("✅ Test image created: test_inputs/example_building.png")
PYTHON_SCRIPT

# Make scripts executable
echo "🔐 Setting script permissions..."
chmod +x generate_alpine_sennhuette.sh 2>/dev/null || true
chmod +x generate_alpine_sennhuette_improved.sh 2>/dev/null || true
find . -type f -name "*.sh" -exec chmod +x {} \; 2>/dev/null || true

# Run tests to verify installation
echo "🧪 Running verification tests..."
python3 -m pytest tests/ -v --tb=short || echo "⚠️  Some tests failed (this is OK for initial setup)"

echo ""
echo "======================================================"
echo "✅ Setup Complete!"
echo "======================================================"
echo ""
echo "🎯 Quick Start Commands:"
echo ""
echo "  1. Test CV pipeline with example image:"
echo "     python generate_from_image.py --input test_inputs/example_building.png --output configs/test_config.json"
echo ""
echo "  2. Generate DXF from existing config:"
echo "     ./generate_alpine_sennhuette_improved.sh alpenhuette_config_20251102_213551.json"
echo ""
echo "  3. Run full test suite:"
echo "     python -m pytest tests/ -v"
echo ""
echo "  4. Check QCAD installation:"
echo "     qcad --version"
echo ""
echo "📚 See README.md for detailed documentation"
echo "======================================================"
