#!/bin/bash

# Quick installer script for XPAT Worker Automation Tool on macOS
# This script can be bundled with the DMG or run separately

echo "🚀 XPAT Worker Automation Tool - macOS Quick Installer"
echo "========================================================"
echo ""

# Check if app is already installed
if [[ -d "/Applications/xpat_worker_tool.app" ]]; then
    echo "✅ App is already installed at /Applications/xpat_worker_tool.app"
    echo ""
    echo "Options:"
    echo "  1. Launch the app"
    echo "  2. Uninstall"
    echo "  3. Reinstall (overwrite current installation)"
    echo "  4. Exit"
    echo ""
    read -p "Select option (1-4): " choice
    
    case $choice in
        1)
            echo "🚀 Launching app..."
            open /Applications/xpat_worker_tool.app
            exit 0
            ;;
        2)
            echo "🗑️  Removing app..."
            rm -rf /Applications/xpat_worker_tool.app
            echo "✅ App uninstalled"
            exit 0
            ;;
        3)
            echo "Continuing with reinstall..."
            ;;
        *)
            echo "Exiting..."
            exit 0
            ;;
    esac
fi

# Find the app bundle
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
APP_BUNDLE="$SCRIPT_DIR/dist/xpat_worker_tool.app"

# Check if DMG mount point has the app
if [[ ! -d "$APP_BUNDLE" ]] && [[ -d "/Volumes/XPAT-Worker-Automation-Tool/xpat_worker_tool.app" ]]; then
    APP_BUNDLE="/Volumes/XPAT-Worker-Automation-Tool/xpat_worker_tool.app"
fi

# Look for app in common locations
if [[ ! -d "$APP_BUNDLE" ]]; then
    APP_BUNDLE=$(find /Volumes -name "xpat_worker_tool.app" -type d 2>/dev/null | head -1)
fi

if [[ ! -d "$APP_BUNDLE" ]]; then
    echo "❌ Error: Cannot find xpat_worker_tool.app"
    echo ""
    echo "Please:"
    echo "  1. Double-click the DMG file if you haven't already"
    echo "  2. Navigate to the mounted volume"
    echo "  3. Run this script from there"
    echo ""
    read -p "Enter path to xpat_worker_tool.app: " APP_BUNDLE
    
    if [[ ! -d "$APP_BUNDLE" ]]; then
        echo "❌ App not found at: $APP_BUNDLE"
        exit 1
    fi
fi

echo "📦 Installing app from: $APP_BUNDLE"
echo ""

# Create Applications folder if needed
mkdir -p /Applications

# Copy app to Applications
echo "📂 Copying app to Applications folder..."
cp -r "$APP_BUNDLE" /Applications/

if [[ -d "/Applications/xpat_worker_tool.app" ]]; then
    echo "✅ App installed successfully!"
    echo ""
    echo "🚀 Launching app..."
    open /Applications/xpat_worker_tool.app
    echo ""
    echo "💡 Tips:"
    echo "   • Find the app in Applications folder"
    echo "   • Add to Dock: Right-click app → Options → Keep in Dock"
    echo "   • Search via Spotlight: Cmd+Space → type 'xpat'"
else
    echo "❌ Installation failed"
    exit 1
fi
