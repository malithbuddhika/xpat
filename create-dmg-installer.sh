#!/bin/bash

# Create DMG installer for macOS XPAT Worker Automation Tool

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
APP_BUNDLE="$SCRIPT_DIR/dist/xpat_worker_tool.app"
DMG_NAME="XPAT-Worker-Automation-Tool"
DMG_FILE="$SCRIPT_DIR/$DMG_NAME.dmg"
DMG_VOLUME="/Volumes/$DMG_NAME"

echo "📦 Creating macOS DMG installer..."

# Check if app bundle exists
if [[ ! -d "$APP_BUNDLE" ]]; then
    echo "❌ Error: App bundle not found at $APP_BUNDLE"
    echo "Please run build-macos.sh first."
    exit 1
fi

# Remove existing DMG if it exists
if [[ -f "$DMG_FILE" ]]; then
    echo "🗑️  Removing existing DMG..."
    rm "$DMG_FILE"
fi

# Unmount volume if already mounted
if [[ -d "$DMG_VOLUME" ]]; then
    echo "🔓 Unmounting existing volume..."
    hdiutil detach "$DMG_VOLUME" 2>/dev/null || true
fi

# Create temporary DMG
echo "🔨 Creating temporary DMG..."
hdiutil create -srcfolder "$SCRIPT_DIR/dist/xpat_worker_tool.app" \
    -volname "$DMG_NAME" \
    -fs HFS+ \
    -fsargs "-c c=64,a=16,e=16" \
    -format UDZO \
    "$DMG_FILE"

# Mount the DMG to customize it
echo "📂 Mounting DMG for customization..."
hdiutil attach "$DMG_FILE" -readwrite -noverify -noautoopen

# Create Applications symlink (makes drag-and-drop installation easy)
echo "🔗 Creating Applications symlink..."
ln -sf /Applications "$DMG_VOLUME/Applications" 2>/dev/null || true

# Set window properties using AppleScript
echo "🎨 Customizing installer appearance..."
osascript << EOF
tell application "Finder"
    tell disk "$DMG_NAME"
        open
        delay 1
        set current view of container window to icon view
        set toolbar visible of container window to false
        set statusbar visible of container window to false
        set the bounds of container window to {400, 100, 900, 500}
        set viewOptions to the icon view options of container window
        set arrangement of viewOptions to not arranged
        set icon size of viewOptions to 72
        set background picture of viewOptions to file "Applications:Utilities:Finder.app:Contents:Resources:finder.icns"
        delay 1
        eject disk "$DMG_NAME"
    end tell
end tell
EOF

# Convert to read-only compressed DMG
echo "🔒 Converting to read-only format..."
hdiutil convert "$DMG_FILE" \
    -format UDZO \
    -o "$SCRIPT_DIR/${DMG_NAME}-compressed.dmg"

# Replace original with compressed version
mv "$SCRIPT_DIR/${DMG_NAME}-compressed.dmg" "$DMG_FILE"

echo ""
echo "✅ DMG installer created successfully!"
echo ""
echo "📝 Installer details:"
echo "   Location: $DMG_FILE"
echo "   Size: $(du -h "$DMG_FILE" | cut -f1)"
echo ""
echo "🚀 To distribute:"
echo "   1. Users double-click the DMG file"
echo "   2. Drag xpat_worker_tool.app to the Applications folder"
echo "   3. Launch from Applications or Spotlight"
echo ""
echo "📥 To manually install:"
echo "   cp -r dist/xpat_worker_tool.app /Applications/"
