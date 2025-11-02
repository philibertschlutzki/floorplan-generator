#!/bin/bash

echo "=== QCAD Installation Test ==="
echo ""

# Finde QCAD
echo "Suche nach QCAD-Installation..."
QCAD_PATH=$(find ~ -name "qcad" -type f -executable 2>/dev/null | grep -E "qcad-.*linux" | head -1)

if [ -z "$QCAD_PATH" ]; then
    echo "❌ QCAD nicht gefunden!"
    echo ""
    echo "Bitte installieren Sie QCAD:"
    echo "1. Download: https://www.qcad.org/en/download"
    echo "2. chmod +x qcad-*.run"
    echo "3. ./qcad-*.run"
    exit 1
fi

echo "✓ QCAD gefunden: $QCAD_PATH"
echo ""

# Test Version
echo "QCAD Version:"
$QCAD_PATH -version

# Empfehlung für symbolischen Link
echo ""
echo "Empfohlener nächster Schritt:"
echo "sudo ln -s $QCAD_PATH /usr/local/bin/qcad"
echo ""
echo "Oder ohne sudo:"
echo "mkdir -p ~/bin"
echo "ln -s $QCAD_PATH ~/bin/qcad"
echo "echo 'export PATH=\$PATH:\$HOME/bin' >> ~/.bashrc"
echo "source ~/.bashrc"
EOF

