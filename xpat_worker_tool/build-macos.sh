#!/bin/bash

# Build script for macOS app bundle of XPAT Worker Automation Tool
# This script generates the .app bundle using PyInstaller.

set -e  # Exit on any error

echo "🚀 Building XPAT Worker Automation Tool for macOS..."

# Check if we're in the project root
if [[ ! -f "main.py" ]]; then
    echo "❌ Error: Run this script from the project root (where main.py is located)."
    exit 1
fi

# Install required dependencies
echo "📦 Installing build dependencies..."
python3 -m pip install --quiet pyinstaller cairosvg pillow

# Generate icon files from SVG
echo "🎨 Generating icon files..."
if python3 scripts/icon_convert.py; then
    echo "✅ Icons generated."
else
    echo "⚠️  Icon conversion failed. Building without custom icon."
fi

# Clean previous builds
echo "🧹 Cleaning previous builds..."
rm -rf build dist

# Build the macOS app bundle
echo "🔨 Building macOS app bundle..."
python3 -m PyInstaller xpat_worker_tool.spec

echo "✅ Build complete! App bundle is at: dist/xpat_worker_tool.app"

# Optional: Test launch
echo "🧪 Testing app launch..."
if ./dist/xpat_worker_tool.app/Contents/MacOS/xpat_worker_tool --help 2>/dev/null; then
    echo "✅ App launches successfully."
else
    echo "⚠️  App may have issues. Check logs or try running manually."
fi

echo "📝 To run the app:"
echo "   open dist/xpat_worker_tool.app"
echo "   # or"
echo "   ./dist/xpat_worker_tool.app/Contents/MacOS/xpat_worker_tool"</content>
<parameter name="filePath">/Users/malithbuddhika/Documents/Development/xpat/xpat_worker_tool/build-macos.sh