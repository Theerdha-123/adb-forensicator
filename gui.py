import customtkinter as ctk
import threading
import os
import sys
from datetime import datetime
from tkinter import filedialog, messagebox

# ── Add project root to path ─────────────────────────────────────
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

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

# ── Theme ─────────────────────────────────────────────────────────
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class ForensicApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("ADB Forensicator  |  v1.0")
        self.geometry("1100x700")
        self.resizable(True, True)
        self.base_path    = ctk.StringVar(value="./real_data")
        self._events      = []
        self._flags       = []
        self._photos      = []
        self._deleted_sms = None
        self._build_ui()

    # ── Layout ────────────────────────────────────────────────────
    def _build_ui(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # ── Left sidebar ─────────────────────────────────────────
        sidebar = ctk.CTkFrame(self, width=220, corner_radius=0,
                               fg_color="#0d1117")
        sidebar.grid(row=0, column=0, sticky="nsew")
        sidebar.grid_rowconfigure(14, weight=1)

        ctk.CTkLabel(sidebar, text="🔍",
                     font=("Courier New", 36)
                     ).grid(row=0, column=0, pady=(30, 0), padx=20)
        ctk.CTkLabel(sidebar, text="ADB\nForensicator",
                     font=("Courier New", 18, "bold"),
                     text_color="#58a6ff"
                     ).grid(row=1, column=0, pady=(5, 25), padx=20)

        nav_buttons = [
            ("  📂  Load Data",        self._select_folder),
            ("  📞  Extract Calls",    self._run_calls),
            ("  💬  Extract SMS",      self._run_sms),
            ("  🌐  Extract Browser",  self._run_browser),
            ("  📷  Extract Photos",   self._run_photos),
            ("  🗑️  Recover Deleted",  self._run_deleted),
            ("  ⚡  Run Full Scan",    self._run_full),
            ("  📄  Generate Report",  self._run_report),
            ("  🖼️  View Photos",      self._open_photos),
        ]
        for i, (label, cmd) in enumerate(nav_buttons):
            ctk.CTkButton(
                sidebar, text=label, anchor="w",
                font=("Courier New", 13),
                fg_color="transparent",
                hover_color="#1f2937",
                text_color="#c9d1d9",
                height=40,
                command=cmd
            ).grid(row=i+2, column=0, padx=10, pady=3, sticky="ew")

        ctk.CTkButton(
            sidebar, text="  🗑️  Clear Log", anchor="w",
            font=("Courier New", 13),
            fg_color="transparent",
            hover_color="#1f2937",
            text_color="#6e7681",
            height=40,
            command=self._clear_log
        ).grid(row=14, column=0, padx=10, pady=(0, 20), sticky="ew")

        # ── Main area ─────────────────────────────────────────────
        main = ctk.CTkFrame(self, fg_color="#0d1117", corner_radius=0)
        main.grid(row=0, column=1, sticky="nsew")
        main.grid_columnconfigure(0, weight=1)
        main.grid_rowconfigure(1, weight=1)

        # ── Top bar ───────────────────────────────────────────────
        topbar = ctk.CTkFrame(main, fg_color="#161b22",
                              corner_radius=0, height=55)
        topbar.grid(row=0, column=0, sticky="ew", pady=(0, 2))
        topbar.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(topbar, text="Data Source:",
                     font=("Courier New", 12),
                     text_color="#8b949e"
                     ).grid(row=0, column=0, padx=(15, 5), pady=15)

        ctk.CTkEntry(
            topbar, textvariable=self.base_path,
            font=("Courier New", 12),
            fg_color="#0d1117",
            border_color="#30363d",
            text_color="#58a6ff",
            width=320
        ).grid(row=0, column=1, padx=5, pady=15, sticky="w")

        ctk.CTkButton(
            topbar, text="Browse", width=80,
            font=("Courier New", 11),
            fg_color="#21262d",
            hover_color="#30363d",
            border_color="#30363d",
            border_width=1,
            command=self._select_folder
        ).grid(row=0, column=2, padx=(5, 15), pady=15)

        self.status_dot = ctk.CTkLabel(
            topbar, text="● READY",
            font=("Courier New", 11, "bold"),
            text_color="#3fb950"
        )
        self.status_dot.grid(row=0, column=3, padx=15)

        # ── Tabs ──────────────────────────────────────────────────
        tabs = ctk.CTkTabview(
            main,
            fg_color="#0d1117",
            segmented_button_fg_color="#161b22",
            segmented_button_selected_color="#1f6feb",
            segmented_button_unselected_color="#161b22",
            segmented_button_selected_hover_color="#388bfd",
        )
        tabs.grid(row=1, column=0, sticky="nsew", padx=10, pady=(5, 10))
        tabs.add("📋 Terminal Log")
        tabs.add("📞 Call Logs")
        tabs.add("💬 SMS")
        tabs.add("📷 Photos")
        tabs.add("🗑️ Deleted SMS")
        tabs.add("⚠️ Flags")

        # Terminal
        self.log_box = ctk.CTkTextbox(
            tabs.tab("📋 Terminal Log"),
            font=("Courier New", 12),
            fg_color="#010409",
            text_color="#39d353",
            wrap="word", border_color="#21262d", border_width=1
        )
        self.log_box.pack(fill="both", expand=True, padx=5, pady=5)

        # Calls
        self.calls_box = ctk.CTkTextbox(
            tabs.tab("📞 Call Logs"),
            font=("Courier New", 12),
            fg_color="#010409",
            text_color="#79c0ff",
            wrap="word", border_color="#21262d", border_width=1
        )
        self.calls_box.pack(fill="both", expand=True, padx=5, pady=5)

        # SMS
        self.sms_box = ctk.CTkTextbox(
            tabs.tab("💬 SMS"),
            font=("Courier New", 12),
            fg_color="#010409",
            text_color="#a5d6ff",
            wrap="word", border_color="#21262d", border_width=1
        )
        self.sms_box.pack(fill="both", expand=True, padx=5, pady=5)

        # Photos
        self.photos_box = ctk.CTkTextbox(
            tabs.tab("📷 Photos"),
            font=("Courier New", 12),
            fg_color="#010409",
            text_color="#d2a8ff",
            wrap="word", border_color="#21262d", border_width=1
        )
        self.photos_box.pack(fill="both", expand=True, padx=5, pady=5)

        # Deleted SMS
        self.deleted_box = ctk.CTkTextbox(
            tabs.tab("🗑️ Deleted SMS"),
            font=("Courier New", 12),
            fg_color="#010409",
            text_color="#f0883e",
            wrap="word", border_color="#21262d", border_width=1
        )
        self.deleted_box.pack(fill="both", expand=True, padx=5, pady=5)

        # Flags
        self.flags_box = ctk.CTkTextbox(
            tabs.tab("⚠️ Flags"),
            font=("Courier New", 12),
            fg_color="#010409",
            text_color="#f0883e",
            wrap="word", border_color="#21262d", border_width=1
        )
        self.flags_box.pack(fill="both", expand=True, padx=5, pady=5)

        # ── Stats bar ─────────────────────────────────────────────
        statsbar = ctk.CTkFrame(main, fg_color="#161b22",
                                corner_radius=0, height=35)
        statsbar.grid(row=2, column=0, sticky="ew")

        self.stat_calls = ctk.CTkLabel(
            statsbar, text="Calls: 0",
            font=("Courier New", 11), text_color="#79c0ff")
        self.stat_calls.grid(row=0, column=0, padx=15, pady=8)

        self.stat_sms = ctk.CTkLabel(
            statsbar, text="SMS: 0",
            font=("Courier New", 11), text_color="#a5d6ff")
        self.stat_sms.grid(row=0, column=1, padx=15)

        self.stat_photos = ctk.CTkLabel(
            statsbar, text="Photos: 0",
            font=("Courier New", 11), text_color="#d2a8ff")
        self.stat_photos.grid(row=0, column=2, padx=15)

        self.stat_deleted = ctk.CTkLabel(
            statsbar, text="Deleted: 0",
            font=("Courier New", 11), text_color="#f0883e")
        self.stat_deleted.grid(row=0, column=3, padx=15)

        self.stat_flags = ctk.CTkLabel(
            statsbar, text="Flags: 0",
            font=("Courier New", 11), text_color="#f0883e")
        self.stat_flags.grid(row=0, column=4, padx=15)

        self.stat_report = ctk.CTkLabel(
            statsbar, text="Report: Not Generated",
            font=("Courier New", 11), text_color="#6e7681")
        self.stat_report.grid(row=0, column=5, padx=15)

        # Welcome
        self._log("=" * 55)
        self._log("   ADB Forensicator  |  v1.0")
        self._log("   For Educational Purposes Only")
        self._log("=" * 55)
        self._log("")
        self._log("[*] System ready.")
        self._log(f"[*] Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self._log(f"[*] Default path: {self.base_path.get()}")
        self._log("")
        self._log("[→] Click 'Run Full Scan' to begin.")

    # ── Helpers ───────────────────────────────────────────────────
    def _log(self, msg):
        self.log_box.configure(state="normal")
        self.log_box.insert("end", msg + "\n")
        self.log_box.see("end")
        self.log_box.configure(state="disabled")

    def _set_status(self, text, color):
        self.status_dot.configure(text=text, text_color=color)

    def _clear_log(self):
        self.log_box.configure(state="normal")
        self.log_box.delete("1.0", "end")
        self.log_box.configure(state="disabled")

    def _select_folder(self):
        folder = filedialog.askdirectory(title="Select Data Folder")
        if folder:
            self.base_path.set(folder)
            self._log(f"[+] Path set to: {folder}")

    def _open_photos(self):
        path = os.path.join(self.base_path.get(), "photos")
        if os.path.exists(path):
            os.startfile(path)
            self._log(f"[+] Opening photos folder: {path}")
        else:
            messagebox.showwarning("Not Found",
                "Photos folder not found!\nRun Full Scan first.")

    # ── Individual extractors ─────────────────────────────────────
    def _run_calls(self):
        def task():
            self._set_status("● RUNNING", "#f0883e")
            self._log("\n[*] Extracting Call Logs...")
            df = extract_calls(self.base_path.get())
            if df is not None:
                self.calls_box.configure(state="normal")
                self.calls_box.delete("1.0", "end")
                self.calls_box.insert("end",
                    f"{'TYPE':<12} {'NUMBER':<18} {'DATE':<22} {'DURATION'}\n")
                self.calls_box.insert("end", "-" * 70 + "\n")
                for _, row in df.iterrows():
                    self.calls_box.insert("end",
                        f"{str(row.get('type','?')):<12} "
                        f"{str(row.get('number','?')):<18} "
                        f"{str(row.get('date','?'))[:19]:<22} "
                        f"{str(row.get('duration','?'))}s\n")
                self.calls_box.configure(state="disabled")
                self.stat_calls.configure(text=f"Calls: {len(df)}")
                self._log(f"[+] {len(df)} call records extracted!")
            else:
                self._log("[-] No call logs found.")
            self._set_status("● READY", "#3fb950")
        threading.Thread(target=task, daemon=True).start()

    def _run_sms(self):
        def task():
            self._set_status("● RUNNING", "#f0883e")
            self._log("\n[*] Extracting SMS...")
            df = extract_sms(self.base_path.get())
            if df is not None:
                self.sms_box.configure(state="normal")
                self.sms_box.delete("1.0", "end")
                self.sms_box.insert("end",
                    f"{'TYPE':<12} {'FROM':<18} {'DATE':<22} {'MESSAGE'}\n")
                self.sms_box.insert("end", "-" * 75 + "\n")
                for _, row in df.iterrows():
                    self.sms_box.insert("end",
                        f"{str(row.get('type','?')):<12} "
                        f"{str(row.get('address','?')):<18} "
                        f"{str(row.get('date','?'))[:19]:<22} "
                        f"{str(row.get('body','?'))[:50]}\n")
                self.sms_box.configure(state="disabled")
                self.stat_sms.configure(text=f"SMS: {len(df)}")
                self._log(f"[+] {len(df)} SMS extracted!")
            else:
                self._log("[-] No SMS found.")
            self._set_status("● READY", "#3fb950")
        threading.Thread(target=task, daemon=True).start()

    def _run_browser(self):
        def task():
            self._set_status("● RUNNING", "#f0883e")
            self._log("\n[*] Extracting Browser History...")
            df = extract_browser(self.base_path.get())
            if df is not None:
                self._log(f"[+] {len(df)} browser records found!")
            else:
                self._log("[-] Browser history not found.")
            self._set_status("● READY", "#3fb950")
        threading.Thread(target=task, daemon=True).start()

    def _run_photos(self):
        def task():
            self._set_status("● RUNNING", "#f0883e")
            self._log("\n[*] Extracting Photo EXIF Metadata...")
            photos = extract_exif_metadata(self.base_path.get())
            self.photos_box.configure(state="normal")
            self.photos_box.delete("1.0", "end")
            if photos:
                self._photos = photos
                self.photos_box.insert("end",
                    f"{'FILENAME':<30} {'SIZE':<10} "
                    f"{'DIMENSIONS':<15} {'DATE TAKEN':<22} {'CAMERA'}\n")
                self.photos_box.insert("end", "-" * 100 + "\n")
                for p in photos:
                    self.photos_box.insert("end",
                        f"{p['filename']:<30} "
                        f"{str(p['size_kb'])+'KB':<10} "
                        f"{p['dimensions']:<15} "
                        f"{p['date_taken']:<22} "
                        f"{p['camera']}\n")
                    if p['gps_lat'] != 'N/A':
                        self.photos_box.insert("end",
                            f"   GPS: {p['gps_lat']}, {p['gps_lon']}\n")
                self.stat_photos.configure(text=f"Photos: {len(photos)}")
                self._log(f"[+] {len(photos)} photos analyzed!")
            else:
                self.photos_box.insert("end", "No photos found.\n")
                self._log("[-] No photos found.")
            self.photos_box.configure(state="disabled")
            self._set_status("● READY", "#3fb950")
        threading.Thread(target=task, daemon=True).start()

    def _run_deleted(self):
        def task():
            self._set_status("● RUNNING", "#f0883e")
            self._log("\n[*] Attempting Deleted SMS Recovery...")
            deleted = recover_deleted_sms(self.base_path.get())
            self.deleted_box.configure(state="normal")
            self.deleted_box.delete("1.0", "end")
            if deleted is not None and len(deleted) > 0:
                self._deleted_sms = deleted
                self.deleted_box.insert("end",
                    f"{'FROM':<18} {'DATE':<22} "
                    f"{'MESSAGE':<50} {'METHOD'}\n")
                self.deleted_box.insert("end", "-" * 110 + "\n")
                for _, row in deleted.iterrows():
                    self.deleted_box.insert("end",
                        f"{str(row.get('address','?')):<18} "
                        f"{str(row.get('date','?'))[:19]:<22} "
                        f"{str(row.get('body',''))[:50]:<50} "
                        f"{str(row.get('recovery_method','?'))}\n")
                self.stat_deleted.configure(
                    text=f"Deleted: {len(deleted)}")
                self._log(f"[+] {len(deleted)} deleted SMS recovered!")
            else:
                self._deleted_sms = None
                self.deleted_box.insert("end",
                    "No deleted SMS recovered.\n")
                self._log("[-] No deleted SMS recovered.")
            self.deleted_box.configure(state="disabled")
            self._set_status("● READY", "#3fb950")
        threading.Thread(target=task, daemon=True).start()

    # ── Full Scan ─────────────────────────────────────────────────
    def _run_full(self):
        def task():
            self._set_status("● SCANNING", "#f0883e")
            self._log("\n" + "=" * 55)
            self._log("  FULL FORENSIC SCAN STARTED")
            self._log("=" * 55)
            path = self.base_path.get()
            self._log(f"\n[*] Target: {path}")
            self._log(
                f"[*] Time  : "
                f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

            # SMS
            self._log("\n[*] Extracting SMS...")
            sms = extract_sms(path)
            if sms is not None:
                self._log(f"[+] {len(sms)} SMS records found")
                self.stat_sms.configure(text=f"SMS: {len(sms)}")
                self.sms_box.configure(state="normal")
                self.sms_box.delete("1.0", "end")
                self.sms_box.insert("end",
                    f"{'TYPE':<12} {'FROM':<18} "
                    f"{'DATE':<22} {'MESSAGE'}\n")
                self.sms_box.insert("end", "-" * 75 + "\n")
                for _, row in sms.iterrows():
                    self.sms_box.insert("end",
                        f"{str(row.get('type','?')):<12} "
                        f"{str(row.get('address','?')):<18} "
                        f"{str(row.get('date','?'))[:19]:<22} "
                        f"{str(row.get('body','?'))[:50]}\n")
                self.sms_box.configure(state="disabled")
            else:
                self._log("[-] No SMS found")

            # Calls
            self._log("\n[*] Extracting Call Logs...")
            calls = extract_calls(path)
            if calls is not None:
                self._log(f"[+] {len(calls)} call records found")
                self.stat_calls.configure(text=f"Calls: {len(calls)}")
                self.calls_box.configure(state="normal")
                self.calls_box.delete("1.0", "end")
                self.calls_box.insert("end",
                    f"{'TYPE':<12} {'NUMBER':<18} "
                    f"{'DATE':<22} {'DURATION'}\n")
                self.calls_box.insert("end", "-" * 70 + "\n")
                for _, row in calls.iterrows():
                    self.calls_box.insert("end",
                        f"{str(row.get('type','?')):<12} "
                        f"{str(row.get('number','?')):<18} "
                        f"{str(row.get('date','?'))[:19]:<22} "
                        f"{str(row.get('duration','?'))}s\n")
                self.calls_box.configure(state="disabled")
            else:
                self._log("[-] No call logs found")

            # Browser
            self._log("\n[*] Extracting Browser History...")
            browser = extract_browser(path)
            if browser is not None:
                self._log(f"[+] {len(browser)} browser records found")
            else:
                self._log("[-] Browser history not found")

            # Firefox
            self._log("\n[*] Extracting Firefox History...")
            firefox = extract_firefox(path)
            if firefox is not None:
                self._log(f"[+] {len(firefox)} Firefox records found")
            else:
                self._log("[-] Firefox history not found")

            # Photos
            self._log("\n[*] Extracting Photo EXIF Metadata...")
            photos = extract_exif_metadata(path)
            self.photos_box.configure(state="normal")
            self.photos_box.delete("1.0", "end")
            if photos:
                self._photos = photos
                for p in photos:
                    self.photos_box.insert("end",
                        f"{p['filename']} | "
                        f"{p['size_kb']}KB | "
                        f"{p['dimensions']} | "
                        f"{p['date_taken']} | "
                        f"{p['camera']}\n")
                    if p['gps_lat'] != 'N/A':
                        self.photos_box.insert("end",
                            f"  GPS: {p['gps_lat']}, "
                            f"{p['gps_lon']}\n")
                self.stat_photos.configure(
                    text=f"Photos: {len(photos)}")
                self._log(f"[+] {len(photos)} photos analyzed!")
            else:
                self.photos_box.insert("end", "No photos found.\n")
                self._log("[-] No photos found")
            self.photos_box.configure(state="disabled")

            # Deleted SMS Recovery
            self._log("\n[*] Attempting Deleted SMS Recovery...")
            deleted = recover_deleted_sms(path)
            self.deleted_box.configure(state="normal")
            self.deleted_box.delete("1.0", "end")
            if deleted is not None and len(deleted) > 0:
                self._deleted_sms = deleted
                self.deleted_box.insert("end",
                    f"{'FROM':<18} {'DATE':<22} "
                    f"{'MESSAGE':<50} {'METHOD'}\n")
                self.deleted_box.insert("end", "-" * 110 + "\n")
                for _, row in deleted.iterrows():
                    self.deleted_box.insert("end",
                        f"{str(row.get('address','?')):<18} "
                        f"{str(row.get('date','?'))[:19]:<22} "
                        f"{str(row.get('body',''))[:50]:<50} "
                        f"{str(row.get('recovery_method','?'))}\n")
                self.stat_deleted.configure(
                    text=f"Deleted: {len(deleted)}")
                self._log(f"[+] {len(deleted)} deleted SMS recovered!")
            else:
                self._deleted_sms = None
                self.deleted_box.insert("end",
                    "No deleted SMS recovered.\n")
                self._log("[-] No deleted SMS recovered")
            self.deleted_box.configure(state="disabled")

            # Timeline
            self._log("\n[*] Building Timeline...")
            events = build_timeline(calls, sms, browser, firefox)
            self._log(f"[+] {len(events)} total events in timeline")

            # Suspicious activity
            self._log("\n[*] Running Suspicious Activity Detector...")
            flags = detect_suspicious(calls, sms, browser)
            self.flags_box.configure(state="normal")
            self.flags_box.delete("1.0", "end")
            if flags:
                self._log(
                    f"[!] {len(flags)} suspicious activities detected!")
                self.stat_flags.configure(text=f"Flags: {len(flags)}")
                for flag in flags:
                    clean = flag.encode(
                        'ascii', 'replace').decode('ascii')
                    self._log(f"    {clean}")
                    self.flags_box.insert("end", clean + "\n")
            else:
                self._log("[+] No suspicious activity detected")
                self.flags_box.insert("end",
                    "No suspicious activity detected.\n")
            self.flags_box.configure(state="disabled")

            self._events = events
            self._flags  = flags

            self._log("\n" + "=" * 55)
            self._log("  SCAN COMPLETE")
            self._log("=" * 55)
            self._log("\n[→] Click 'Generate Report' to save reports.")
            self._set_status("● DONE", "#3fb950")

        threading.Thread(target=task, daemon=True).start()

    # ── Generate Report ───────────────────────────────────────────
    def _run_report(self):
        def task():
            if not self._events:
                messagebox.showwarning("Warning",
                    "Please run a Full Scan first!")
                return
            self._set_status("● GENERATING", "#f0883e")
            os.makedirs("output", exist_ok=True)

            self._log("\n[*] Generating PDF Report...")
            generate_pdf_report(self._events, self._flags)
            self._log("[+] PDF  saved → output/forensic_report.pdf")

            self._log("\n[*] Generating HTML Report...")
            generate_html_report(
                self._events,
                self._flags,
                self._photos,
                self._deleted_sms
            )
            self._log("[+] HTML saved → output/forensic_report.html")

            self.stat_report.configure(
                text="Report: Generated ✓",
                text_color="#3fb950"
            )
            self._set_status("● READY", "#3fb950")
            messagebox.showinfo("Success",
                "Reports saved!\n\n"
                "PDF  → output/forensic_report.pdf\n"
                "HTML → output/forensic_report.html")

        threading.Thread(target=task, daemon=True).start()


# ── Entry point ───────────────────────────────────────────────────
if __name__ == "__main__":
    app = ForensicApp()
    app.mainloop()
