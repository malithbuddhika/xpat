# XPAT Worker Automation Tool - macOS Installation Guide

## 📦 Installation Package Created

Your macOS installation package is ready! Here are all the ways to install and use the app.

### Option 1: DMG Installer (Recommended for Distribution)
**File:** `XPAT-Worker-Automation-Tool.dmg` (14 MB)

**Installation Steps:**
1. Double-click the DMG file to open it
2. Drag `xpat_worker_tool.app` to the **Applications** folder
3. Wait for the copy process to complete
4. Open **Applications** → **xpat_worker_tool** and click **Open**

**Launching the App:**
- **Finder:** Applications → xpat_worker_tool → Double-click
- **Spotlight:** Press `Cmd + Space`, type "xpat", press Enter
- **Terminal:** 
  ```bash
  /Applications/xpat_worker_tool.app/Contents/MacOS/xpat_worker_tool
  ```

### Option 2: Direct App Bundle Installation
**File:** `dist/xpat_worker_tool.app` (in project directory)

**Installation:**
```bash
cp -r dist/xpat_worker_tool.app /Applications/
```

**Launch:**
```bash
/Applications/xpat_worker_tool.app/Contents/MacOS/xpat_worker_tool
```

### Option 3: Run from Source (Development)
```bash
# From project root
QT_MAC_WANTS_LAYER=1 ./.venv/bin/python xpat_worker_tool/main.py
```

---

## 🔧 System Requirements

- **OS:** macOS 10.13 or later
- **Architecture:** Intel or Apple Silicon (ARM64)
- **RAM:** 2GB minimum (4GB recommended)
- **Disk:** ~500 MB free space for installation

---

## 📋 What's Included

- ✅ Full XPAT Worker verification automation
- ✅ Excel file import/export
- ✅ Photo preview on click
- ✅ Progress tracking
- ✅ Session caching
- ✅ Real-time logging

---

## 🚀 First Run

1. **Grant Permissions:** The app may ask for network access - click **Allow**
2. **API Configuration:** 
   - Add your XPAT API credentials in the settings
   - Configure session cache location if needed
3. **Load Excel File:**
   - Click "Browse" and select your worker Excel file
   - Ensure columns are named: `Permit Number`, `Passport Number`, `Photo URL`, `Name`
4. **Start Verification:**
   - Click "Start Verification" to begin processing workers

---

## 🛠️ Rebuilding the App

If you need to rebuild the app after code changes:

```bash
# Build the app bundle
./xpat_worker_tool/build-macos.sh

# Create a new DMG installer
./create-dmg-installer.sh

# Or install directly
cp -r dist/xpat_worker_tool.app /Applications/
```

---

## 📱 macOS Troubleshooting

### "App cannot be opened"
If you see a security warning:
1. Open System Preferences → Security & Privacy
2. Allow the app to run
3. Or right-click the app and select "Open"

### App Crashes on Launch
1. Try running from Terminal to see error messages:
   ```bash
   /Applications/xpat_worker_tool.app/Contents/MacOS/xpat_worker_tool
   ```
2. Check the logs in `~/Library/Logs/xpat_worker_tool/`

### Dark Screen or Rendering Issues
1. Ensure QT environment variable is set:
   ```bash
   QT_MAC_WANTS_LAYER=1 /Applications/xpat_worker_tool.app/Contents/MacOS/xpat_worker_tool
   ```

### Photo Preview Not Working
1. Check internet connection
2. Verify photo URLs are accessible
3. Check app logs for API errors

---

## 📊 File Locations

**App Bundle:** 
```
/Applications/xpat_worker_tool.app
```

**User Data & Logs:**
```
~/Library/Logs/xpat_worker_tool/
~/Library/Application Support/xpat_worker_tool/
```

**Cache:**
```
~/.xpat_cache/
```

---

## 🔐 Code Signing (Optional Advanced)

To add code signing for distribution:

```bash
# Sign with your certificate
codesign -s "Developer ID Application" \
  /Applications/xpat_worker_tool.app

# Verify signature
codesign -v /Applications/xpat_worker_tool.app
```

---

## 📝 Building Installer for Distribution

To create a release-ready installer:

1. **Build the app:**
   ```bash
   ./xpat_worker_tool/build-macos.sh
   ```

2. **Create DMG:**
   ```bash
   ./create-dmg-installer.sh
   ```

3. **Upload to GitHub Releases:**
   - Go to your GitHub repository
   - Create a new Release
   - Attach `XPAT-Worker-Automation-Tool.dmg`
   - Add release notes

---

## 🐛 Reporting Issues

If you encounter problems:

1. Check logs in: `~/Library/Logs/xpat_worker_tool/`
2. Run from terminal to capture error messages
3. Report with:
   - macOS version (`sw_vers`)
   - Python version (`.venv/bin/python --version`)
   - Complete error message
   - Steps to reproduce

---

## ✅ Installation Verified

Your installation package is ready for distribution! 
- **DMG File:** `XPAT-Worker-Automation-Tool.dmg` (14 MB)
- **App Location:** `dist/xpat_worker_tool.app`

Users can download the DMG and install by dragging to Applications.
