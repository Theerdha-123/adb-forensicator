# 🔍 ADB Forensicator

An Android Digital Forensics tool built with Python
that extracts and analyzes artifacts from Android 
devices using ADB (Android Debug Bridge).

![Python](https://img.shields.io/badge/Python-3.13-blue)
![Platform](https://img.shields.io/badge/Platform-Windows-green)
![License](https://img.shields.io/badge/License-Educational-orange)

## 📸 Screenshots

### GUI - Terminal Log
![GUI](screenshots/01_gui_terminal.png)

### GUI - Scan Complete
![Scan](screenshots/02_gui_scan_complete.png)

### HTML Report - Summary
![HTML](screenshots/03_html_report_summary.png)

### HTML Report - Timeline
![Timeline](screenshots/04_html_timeline.png)

### HTML Report - Photo EXIF
![Photos](screenshots/05_html_photos.png)

### PDF Report
![PDF](screenshots/06_pdf_report.png)

## ✅ Features
- 📞 Call Log Extraction
- 💬 SMS Extraction
- 🌐 Firefox Browser History
- 📷 EXIF Photo Metadata
- 🗑️ Deleted SMS Recovery
- 🤖 ML Anomaly Detection
- ⚠️ Suspicious Activity Detection
- 📄 PDF + HTML Reports
- 🖥️ Professional Dark GUI

## 🛠️ Tech Stack
- Python 3.13
- ADB (Android Debug Bridge)
- SQLite3 Forensics
- Scikit-learn (Isolation Forest)
- Pandas
- CustomTkinter
- FPDF2
- Pillow + ExifRead

## ⚙️ Installation

### Step 1 — Install Python
Download from https://python.org

### Step 2 — Install ADB
Download Platform Tools from:
https://developer.android.com/tools/releases/platform-tools

### Step 3 — Install Firefox APK (for emulator)
Download x86_64 version from:
https://www.apkmirror.com/apk/mozilla/firefox/

### Step 4 — Install Python Libraries
pip install pandas fpdf2 customtkinter pillow exifread scikit-learn numpy

### Step 5 — Setup Android Emulator
- Install Android Studio
- Create Pixel 4 device with API 30 AOSP
- Install Firefox APK using ADB

## 🚀 Usage

### Run GUI
python gui.py

### Run Terminal
python main.py


## 📁 Project Structure
```
android_forensics/
├── extractor/
│   ├── __init__.py
│   └── db_parser.py
├── analyzer/
│   ├── __init__.py
│   ├── timeline_builder.py
│   ├── anomaly_detector.py
│   └── ml_detector.py
├── reporter/
│   ├── __init__.py
│   └── report_generator.py
├── screenshots/
├── .gitignore
├── README.md
├── gui.py
├── main.py
└── create_test_data.py
```

## ⚠️ Disclaimer
This tool is for educational purposes only.
Only use on devices you own or have permission to analyze.

## 📥 Required Downloads

These files are NOT included in the repo due to size:

### ADB (Android Debug Bridge)
Download Platform Tools:
https://developer.android.com/tools/releases/platform-tools

Place adb.exe in: C:\platform-tools\

### Firefox APK (for emulator)
Download x86_64 version:
https://www.apkmirror.com/apk/mozilla/firefox/

Install using:
adb install org.mozilla.firefox_143.0.4.apk

## 👨‍💻 Author
M.V.Theerdha
