# XPAT Worker Automation Tool

A cross-platform desktop application (macOS + Windows) built with **Python 3.11+** and **PySide6**. It automates verification of Maldives XPAT work permits via the official verification endpoint and updates Excel sheets with worker details.

---

## ✅ Features

- Load Excel files containing `WorkPermitNumber` and `PassportNumber`
- Verify permits in parallel (8 threads)
- Automatically parse worker data from XPAT HTML response
- Cache previously verified permits
- Drag & drop Excel file support
- Live progress, logs, and stats
- Table preview with sorting
- Photo preview on row click
- Export results to Excel or CSV
- Dark mode UI

---

## 🛠️ Installation

```bash
python -m venv .venv
source .venv/bin/activate    # macOS/Linux
.venv\Scripts\activate     # Windows
pip install -r requirements.txt
```

> ⚙️ Optional (icon conversion)
>
> If you want to generate `assets/icon.ico` and `assets/icon.icns` from the built-in `assets/icon.svg`, install additional dependencies:
>
> ```bash
> pip install cairosvg pillow
> python scripts/icon_convert.py
> ```

---

## ▶️ Running Locally

```bash
python main.py
```

---

## 📦 Packaging (PyInstaller)

### Windows

PyInstaller on Windows requires an `.ico` icon file. Convert `assets/icon.svg` to `assets/icon.ico` (or use your own).

```bash
pyinstaller --onefile --windowed --icon=assets/icon.ico main.py
```

Expected output:

- `dist/xpat_worker_tool.exe`

### macOS

PyInstaller on macOS requires an `.icns` icon file. Convert `assets/icon.svg` to `assets/icon.icns` (or use your own).

```bash
pyinstaller --windowed --icon=assets/icon.icns main.py
```

Expected output:

- `dist/xpat_worker_tool.app`

> ⚠️ Note: The repository includes a placeholder `assets/icon.svg`. Replace it with a real icon before building for distribution.

---

## 🔧 Troubleshooting

- If verification fails for many permits, ensure your network access and that the XPAT endpoint is reachable.
- If the UI hangs, stop the process and reduce the concurrent thread count in `app/utils/config.py` by tuning `MAX_WORKERS`.
- Check logs in `logs/app.log` for detailed info.

---

## 🧠 Notes

- This tool uses a shared `requests.Session()` to maintain ASP.NET cookies required by XPAT.
- Caching is stored in `cache/verified_cache.json` to avoid repeated lookups.
- The HTML parser tries to be resilient, but changes in the XPAT site structure may require updating `app/services/html_parser.py`.
