# 🎯 XPAT Worker Automation Tool - macOS Installation Quick Reference

## 📦 What You Have

| File | Size | Purpose |
|------|------|---------|
| `XPAT-Worker-Automation-Tool.dmg` | 14 MB | Ready-to-distribute installer for end users |
| `dist/xpat_worker_tool.app` | ~100 MB | Standalone app bundle |
| `install-app.sh` | Auto-installer script | Interactive installation helper |
| `INSTALLATION_GUIDE_MACOS.md` | Detailed guide | Complete setup & troubleshooting |

---

## ⚡ Quick Start (3 Steps)

### Method 1: DMG Installer (Easiest for Users)
```bash
# Share this file with users:
# XPAT-Worker-Automation-Tool.dmg

# Users do:
# 1. Double-click DMG
# 2. Drag app to Applications
# 3. Launch from Applications
```

### Method 2: Using Install Script
```bash
# Run the installer
./install-app.sh

# Follow the prompts - it will install to /Applications automatically
```

### Method 3: Manual Installation
```bash
# Copy app to Applications
cp -r dist/xpat_worker_tool.app /Applications/

# Launch from Applications or Terminal:
open /Applications/xpat_worker_tool.app
```

---

## 🚀 Launching the App

**Via Finder:**
- Applications → xpat_worker_tool → Double-click

**Via Spotlight:**
- Cmd+Space → Type "xpat" → Press Enter

**Via Terminal:**
```bash
# Standard launch
open /Applications/xpat_worker_tool.app

# With explicit environment variable (if needed)
QT_MAC_WANTS_LAYER=1 open /Applications/xpat_worker_tool.app
```

---

## 📋 System Requirements

✅ macOS 10.13+  
✅ Intel or Apple Silicon (M1/M2/M3)  
✅ 2GB RAM (4GB recommended)  
✅ 500MB disk space

---

## 🔧 Rebuild Instructions

After code changes:

```bash
# 1. Build fresh app bundle
./xpat_worker_tool/build-macos.sh

# 2. Create new DMG installer
./create-dmg-installer.sh

# 3. Both files are ready in:
# - dist/xpat_worker_tool.app
# - XPAT-Worker-Automation-Tool.dmg
```

---

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| App won't open | Right-click → Open (bypass security) |
| Black screen | Set `QT_MAC_WANTS_LAYER=1` environment variable |
| Crash on launch | Check `~/Library/Logs/xpat_worker_tool/` for errors |
| Photos not loading | Verify internet connection and API credentials |

---

## 📊 File Structure After Installation

```
/Applications/xpat_worker_tool.app/          ← Main app
  ├── Contents/
  │   ├── MacOS/xpat_worker_tool             ← Executable
  │   ├── Frameworks/                        ← Python & PySide6
  │   └── Resources/                         ← App data

~/.xpat_cache/                               ← User cache
~/Library/Logs/xpat_worker_tool/            ← App logs
```

---

## 🎁 Distribution

**To share with others:**

1. **Via DMG (Recommended):**
   ```bash
   # Just send: XPAT-Worker-Automation-Tool.dmg (14 MB)
   # Users download and double-click to install
   ```

2. **Via GitHub Releases:**
   ```bash
   # Create release on GitHub
   # Upload XPAT-Worker-Automation-Tool.dmg
   # Users download from releases page
   ```

3. **Via Compressed Archive:**
   ```bash
   cd dist
   zip -r ../xpat_worker_tool.zip xpat_worker_tool.app
   # Share xpat_worker_tool.zip (can be large ~100MB)
   ```

---

## ✨ Features Included

✅ Worker verification automation  
✅ Excel import/export with validation  
✅ Photo preview on row click  
✅ Real-time progress tracking  
✅ Session caching  
✅ Dark theme UI  
✅ Detailed logging  
✅ Multi-threaded operations  

---

## 📝 First Use Checklist

- [ ] App installed to `/Applications/xpat_worker_tool.app`
- [ ] Can open from Spotlight (Cmd+Space → "xpat")
- [ ] Excel file loads correctly
- [ ] API credentials configured
- [ ] Test worker verification on 1-2 rows
- [ ] Check logs if any issues: `~/Library/Logs/xpat_worker_tool/`

---

## 🔗 GitHub Repository

All files, installation package, and build scripts are available at:
```
https://github.com/malithbuddhika/xpat
```

Included files:
- Source code
- Build scripts (`build-macos.sh`)
- DMG installer
- Installation guides
- All dependencies documented

---

## 💡 Pro Tips

1. **Add to Dock:**
   - Right-click app in Applications
   - Select "Options → Keep in Dock"

2. **Create Alias on Desktop:**
   - Right-click app in Applications
   - Select "Make Alias"
   - Drag to Desktop

3. **Uninstall:**
   ```bash
   rm -rf /Applications/xpat_worker_tool.app
   rm -rf ~/.xpat_cache/
   ```

4. **Clear Cache:**
   ```bash
   rm -rf ~/.xpat_cache/*
   ```

---

## 📞 Support

For issues:
1. Check logs: `~/Library/Logs/xpat_worker_tool/app.log`
2. Review [INSTALLATION_GUIDE_MACOS.md](INSTALLATION_GUIDE_MACOS.md)
3. Report on GitHub Issues with logs attached

---

**Version:** 1.0  
**Built:** macOS (Intel + Apple Silicon)  
**Python:** 3.9+  
**Framework:** PySide6
