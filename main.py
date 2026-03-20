import os
import subprocess
from extractor.db_parser import (
    extract_sms,
    extract_calls,
    extract_browser,
    extract_firefox,
    extract_contacts,
    extract_exif_metadata,
    recover_deleted_sms
)
from analyzer.timeline_builder import build_timeline
from analyzer.anomaly_detector import detect_suspicious
from reporter.report_generator import generate_pdf_report, generate_html_report
from analyzer.ml_detector import run_ml_detection

BASE_PATH = "./real_data"

print("\n========== ADB FORENSICATOR - ANDROID FORENSIC EXTRACTOR ==========\n")

# ── Device Information ────────────────────────────────────────────
print("===== DEVICE INFORMATION =====")
props = {
    "Model"      : "ro.product.model",
    "Brand"      : "ro.product.brand",
    "Android Ver": "ro.build.version.release",
    "Serial No"  : "ro.serialno",
}
for label, prop in props.items():
    try:
        result = subprocess.run(
            ['C:\\platform-tools\\adb', 'shell', 'getprop', prop],
            capture_output=True, text=True
        )
        value = result.stdout.strip()
        print(f"[{label}]: {value if value else 'N/A'}")
    except:
        print(f"[{label}]: N/A")

# ── SMS Extraction ────────────────────────────────────────────────
print("\n[*] Extracting SMS...")
sms = extract_sms(BASE_PATH)

# ── Call Log Extraction ───────────────────────────────────────────
print("\n[*] Extracting Call Logs...")
calls = extract_calls(BASE_PATH)

# ── Chrome Browser History ────────────────────────────────────────
print("\n[*] Extracting Chrome Browser History...")
browser = extract_browser(BASE_PATH)

# ── Firefox Browser History ───────────────────────────────────────
print("\n[*] Extracting Firefox Browser History...")
firefox = extract_firefox(BASE_PATH)

# ── Contacts ──────────────────────────────────────────────────────
print("\n[*] Extracting Contacts...")
contacts = extract_contacts(BASE_PATH)

# ── Deleted SMS Recovery ──────────────────────────────────────────
print("\n[*] Attempting Deleted SMS Recovery...")
deleted_sms = recover_deleted_sms(BASE_PATH)
if deleted_sms is not None and len(deleted_sms) > 0:
    print(f"\n===== RECOVERED DELETED SMS ({len(deleted_sms)}) =====")
    for _, row in deleted_sms.iterrows():
        print(f"📱 From   : {row.get('address', 'Unknown')}")
        print(f"   Date   : {row.get('date', 'Unknown')}")
        print(f"   Message: {str(row.get('body', ''))[:80]}")
        print(f"   Method : {row.get('recovery_method', 'Unknown')}")
        print()
else:
    print("[+] No deleted SMS recovered")

# ── EXIF Photo Metadata ───────────────────────────────────────────
print("\n[*] Extracting Photo EXIF Metadata...")
photos = extract_exif_metadata(BASE_PATH)

# ── Build Timeline ────────────────────────────────────────────────
print("\n[*] Building Timeline...")
events = build_timeline(calls, sms, browser, firefox)

# ── Print Timeline ────────────────────────────────────────────────
print("\n===== FORENSIC TIMELINE =====")
icons = {'CALL': '📞', 'SMS': '💬', 'BROWSER': '🌐'}
for e in events:
    icon = icons.get(e['type'], '•')
    print(f"{icon}  [{e['time']}]  {e['detail']}")

# ── Print Contacts ────────────────────────────────────────────────
if contacts is not None and len(contacts) > 0:
    print("\n===== CONTACTS =====")
    for _, row in contacts.iterrows():
        print(f"👤 {row.get('display_name', 'Unknown')}")

# ── Print Photo Metadata ──────────────────────────────────────────
if photos:
    print("\n===== PHOTO METADATA =====")
    for photo in photos:
        print(f"\n📷 File      : {photo['filename']}")
        print(f"   Size      : {photo['size_kb']} KB")
        print(f"   Dimensions: {photo['dimensions']}")
        print(f"   Date Taken: {photo['date_taken']}")
        print(f"   Camera    : {photo['camera']}")
        print(f"   Flash     : {photo['flash']}")
        if photo['gps_lat'] != 'N/A':
            print(f"   GPS       : {photo['gps_lat']}, {photo['gps_lon']}")
            print(f"   Maps Link : https://maps.google.com/?q={photo['gps_lat']},{photo['gps_lon']}")
else:
    print("\n[-] No photos found")

# ── Suspicious Activity Detection ────────────────────────────────
print("\n[*] Running Suspicious Activity Detector...")
flags = detect_suspicious(calls, sms, browser)

if flags:
    print("\n===== SUSPICIOUS ACTIVITY DETECTED =====")
    for flag in flags:
        print(f"⚠️  {flag}")
else:
    print("[+] No suspicious activity detected")

# ── ML Anomaly Detection ──────────────────────────────────────────
print("\n[*] Running ML Anomaly Detection...")
ml_flags = run_ml_detection(calls, sms, browser)
if ml_flags:
    print("\n===== ML ANOMALIES DETECTED =====")
    for flag in ml_flags:
        print(f"🤖  {flag}")
else:
    print("[+] ML: No anomalies detected")

# Combine rule-based + ML flags
all_flags = flags + ml_flags    

# ── Generate Reports ──────────────────────────────────────────────
os.makedirs("output", exist_ok=True)

print("\n[*] Generating PDF Report...")
generate_pdf_report(events, all_flags)

print("\n[*] Generating HTML Report...")
generate_html_report(events, all_flags, photos, deleted_sms)

print("\n✅ Done!")
print("   📄 PDF  → output/forensic_report.pdf")
print("   🌐 HTML → output/forensic_report.html")