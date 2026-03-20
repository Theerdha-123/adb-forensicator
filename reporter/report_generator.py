from fpdf import FPDF
from datetime import datetime
import os


def generate_pdf_report(events, flags=[],
                         output_path="output/forensic_report.pdf"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_margins(15, 15, 15)

    # ── Title ─────────────────────────────────────────────────────
    pdf.set_font("Helvetica", 'B', 16)
    pdf.cell(0, 10,
             "ADB Forensicator - Forensic Investigation Report",
             ln=True, align='C')
    pdf.set_font("Helvetica", '', 10)
    pdf.cell(0, 8,
             f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
             ln=True, align='C')
    pdf.ln(5)

    # ── Summary ───────────────────────────────────────────────────
    pdf.set_font("Helvetica", 'B', 12)
    pdf.cell(0, 8, "Summary", ln=True)
    pdf.set_font("Helvetica", '', 10)
    pdf.cell(0, 7, "Tool        : ADB Forensicator v1.0",  ln=True)
    pdf.cell(0, 7, "Evidence    : Android 11 Emulator",    ln=True)
    pdf.cell(0, 7, f"Total Events: {len(events)}",         ln=True)
    pdf.cell(0, 7,
             f"Call Logs   : "
             f"{sum(1 for e in events if e['type'] == 'CALL')}",
             ln=True)
    pdf.cell(0, 7,
             f"SMS Messages: "
             f"{sum(1 for e in events if e['type'] == 'SMS')}",
             ln=True)
    pdf.cell(0, 7,
             f"Browser Hits: "
             f"{sum(1 for e in events if e['type'] == 'BROWSER')}",
             ln=True)
    pdf.cell(0, 7, f"Flags Raised: {len(flags)}", ln=True)
    pdf.ln(5)

    # ── Suspicious Activity ───────────────────────────────────────
    if flags:
        pdf.set_font("Helvetica", 'B', 12)
        pdf.cell(0, 8, "Suspicious Activity Detected", ln=True)
        pdf.set_font("Helvetica", '', 9)
        for flag in flags:
            clean = flag.encode('latin-1', 'replace').decode('latin-1')
            pdf.cell(0, 7, clean[:90], ln=True)
        pdf.ln(5)

    # ── Timeline ──────────────────────────────────────────────────
    pdf.set_font("Helvetica", 'B', 12)
    pdf.cell(0, 8, "Activity Timeline", ln=True)
    pdf.ln(2)
    for event in events:
        pdf.set_font("Helvetica", 'B', 9)
        pdf.set_fill_color(230, 230, 230)
        pdf.cell(22, 7, event['type'], border=1, fill=True)
        pdf.set_font("Helvetica", '', 9)
        pdf.cell(42, 7, str(event['time'])[:19], border=1)
        pdf.cell(0,  7, str(event['detail'])[:60], border=1, ln=True)

    # ── Footer ────────────────────────────────────────────────────
    pdf.ln(5)
    pdf.set_font("Helvetica", 'I', 8)
    pdf.cell(0, 7,
             "--- End of Report | ADB Forensicator v1.0 | "
             "For Educational Purposes Only ---",
             ln=True, align='C')

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    pdf.output(output_path)
    print(f"[+] PDF report saved → {output_path}")


def generate_html_report(events, flags=[], photos=[],
                          deleted_sms=None,
                          output_path="output/forensic_report.html"):

    # ── Timeline rows ─────────────────────────────────────────────
    rows = ""
    for e in events:
        color = {
            'CALL'   : '#79c0ff',
            'SMS'    : '#a5d6ff',
            'BROWSER': '#56d364'
        }.get(e['type'], '#c9d1d9')
        rows += f"""
        <tr>
            <td style='color:#8b949e'>{str(e['time'])[:19]}</td>
            <td style='color:{color};font-weight:bold'>{e['type']}</td>
            <td>{str(e['detail'])[:100]}</td>
        </tr>"""

    # ── Flag rows ─────────────────────────────────────────────────
    flag_html = ""
    if flags:
        for f in flags:
            clean = f.encode('ascii', 'replace').decode('ascii')
            flag_html += f"<li>{clean}</li>"
    else:
        flag_html = (
            "<p style='color:#3fb950'>"
            "No suspicious activity detected.</p>"
        )

    # ── Photo rows ────────────────────────────────────────────────
    photo_rows = ""
    if photos:
        for p in photos:
            gps_link = "N/A"
            if p['gps_lat'] != 'N/A':
                gps_link = (
                    f"<a href='https://maps.google.com/?q="
                    f"{p['gps_lat']},{p['gps_lon']}' "
                    f"style='color:#58a6ff' target='_blank'>"
                    f"View on Maps</a>"
                )
            img_preview = (
                f"<img src='../real_data/photos/{p['filename']}' "
                f"style='width:80px;height:60px;object-fit:cover;"
                f"border-radius:4px;cursor:pointer;"
                f"border:1px solid #30363d;' "
                f"onclick=\"window.open('../real_data/photos/"
                f"{p['filename']}')\" "
                f"title='Click to open full image'>"
            )
            photo_rows += f"""
            <tr>
                <td>{img_preview}</td>
                <td style='color:#c9d1d9'>{p['filename']}</td>
                <td style='color:#8b949e'>{p['size_kb']} KB</td>
                <td style='color:#8b949e'>{p['dimensions']}</td>
                <td style='color:#8b949e'>{p['date_taken']}</td>
                <td style='color:#8b949e'>{p['camera']}</td>
                <td style='color:#8b949e'>{p['flash']}</td>
                <td>{gps_link}</td>
            </tr>"""

    # ── Deleted SMS rows ──────────────────────────────────────────
    deleted_rows = ""
    deleted_count = 0
    if deleted_sms is not None and len(deleted_sms) > 0:
        deleted_count = len(deleted_sms)
        for _, row in deleted_sms.iterrows():
            deleted_rows += f"""
            <tr>
                <td style='color:#f0883e'>
                    {str(row.get('address','Unknown'))}</td>
                <td style='color:#8b949e'>
                    {str(row.get('date','Unknown'))[:19]}</td>
                <td style='color:#c9d1d9'>
                    {str(row.get('body',''))[:100]}</td>
                <td style='color:#56d364'>
                    {str(row.get('recovery_method','Unknown'))}</td>
            </tr>"""

    # ── Counts ────────────────────────────────────────────────────
    total      = len(events)
    calls      = sum(1 for e in events if e['type'] == 'CALL')
    sms        = sum(1 for e in events if e['type'] == 'SMS')
    browser    = sum(1 for e in events if e['type'] == 'BROWSER')
    flagcount  = len(flags)
    photocount = len(photos) if photos else 0

    # ── Photo section ─────────────────────────────────────────────
    if photos:
        photo_section = f"""
    <h2>📷 Photo EXIF Metadata</h2>
    <table>
        <thead>
            <tr>
                <th>Preview</th><th>Filename</th><th>Size</th>
                <th>Dimensions</th><th>Date Taken</th>
                <th>Camera</th><th>Flash</th><th>GPS</th>
            </tr>
        </thead>
        <tbody>{photo_rows}</tbody>
    </table>"""
    else:
        photo_section = """
    <h2>📷 Photo EXIF Metadata</h2>
    <p style='color:#8b949e'>No photos found.</p>"""

    # ── Deleted SMS section ───────────────────────────────────────
    if deleted_count > 0:
        deleted_section = f"""
    <h2>🗑️ Recovered Deleted SMS ({deleted_count})</h2>
    <table>
        <thead>
            <tr>
                <th>From</th>
                <th>Date</th>
                <th>Message</th>
                <th>Recovery Method</th>
            </tr>
        </thead>
        <tbody>{deleted_rows}</tbody>
    </table>"""
    else:
        deleted_section = """
    <h2>🗑️ Recovered Deleted SMS</h2>
    <p style='color:#8b949e'>No deleted SMS recovered.</p>"""

    # ── Full HTML ─────────────────────────────────────────────────
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ADB Forensicator Report</title>
    <style>
        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}
        body {{
            background: #0d1117;
            color: #c9d1d9;
            font-family: 'Courier New', monospace;
            padding: 40px;
            line-height: 1.6;
        }}
        .header {{
            border-bottom: 1px solid #30363d;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }}
        .header h1 {{
            color: #58a6ff;
            font-size: 24px;
            margin-bottom: 5px;
        }}
        .header p {{
            color: #8b949e;
            font-size: 13px;
        }}
        .summary {{
            display: flex;
            gap: 12px;
            flex-wrap: wrap;
            margin: 20px 0;
        }}
        .badge {{
            background: #161b22;
            border: 1px solid #30363d;
            border-radius: 20px;
            padding: 6px 16px;
            font-size: 13px;
            font-weight: bold;
        }}
        .badge.calls   {{ color:#79c0ff; border-color:#79c0ff; }}
        .badge.sms     {{ color:#a5d6ff; border-color:#a5d6ff; }}
        .badge.browser {{ color:#56d364; border-color:#56d364; }}
        .badge.flags   {{ color:#f0883e; border-color:#f0883e; }}
        .badge.total   {{ color:#58a6ff; border-color:#58a6ff; }}
        .badge.photos  {{ color:#d2a8ff; border-color:#d2a8ff; }}
        .badge.deleted {{ color:#f0883e; border-color:#f0883e; }}
        h2 {{
            color: #58a6ff;
            font-size: 16px;
            margin: 30px 0 12px 0;
            padding-bottom: 8px;
            border-bottom: 1px solid #21262d;
        }}
        .flags-list {{
            list-style: none;
            background: #161b22;
            border: 1px solid #f0883e44;
            border-radius: 6px;
            padding: 15px 20px;
        }}
        .flags-list li {{
            color: #f0883e;
            padding: 5px 0;
            border-bottom: 1px solid #21262d;
            font-size: 13px;
        }}
        .flags-list li:last-child {{ border-bottom: none; }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 10px;
            font-size: 13px;
        }}
        thead tr {{ background: #161b22; }}
        th {{
            color: #58a6ff;
            padding: 10px 15px;
            text-align: left;
            border-bottom: 2px solid #30363d;
        }}
        td {{
            padding: 8px 15px;
            border-bottom: 1px solid #21262d;
            word-break: break-all;
        }}
        tr:hover td {{ background: #161b22; }}
        .footer {{
            margin-top: 40px;
            padding-top: 15px;
            border-top: 1px solid #21262d;
            color: #6e7681;
            font-size: 11px;
            text-align: center;
        }}
    </style>
</head>
<body>

    <div class="header">
        <h1>🔍 ADB Forensicator — Forensic Investigation Report</h1>
        <p>
            Generated : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            &nbsp;|&nbsp;
            Tool : ADB Forensicator v1.0
            &nbsp;|&nbsp;
            Evidence : Android 11 Emulator
        </p>
    </div>

    <h2>📊 Summary</h2>
    <div class="summary">
        <span class="badge total">   Total: {total}</span>
        <span class="badge calls">  📞 Calls: {calls}</span>
        <span class="badge sms">    💬 SMS: {sms}</span>
        <span class="badge browser">🌐 Browser: {browser}</span>
        <span class="badge photos"> 📷 Photos: {photocount}</span>
        <span class="badge deleted">🗑️ Deleted Recovered: {deleted_count}</span>
        <span class="badge flags">  ⚠️ Flags: {flagcount}</span>
    </div>

    <h2>⚠️ Suspicious Activity</h2>
    {'<ul class="flags-list">' + flag_html + '</ul>' if flags else flag_html}

    <h2>📋 Activity Timeline</h2>
    <table>
        <thead>
            <tr><th>Time</th><th>Type</th><th>Detail</th></tr>
        </thead>
        <tbody>{rows}</tbody>
    </table>

    {photo_section}

    {deleted_section}

    <div class="footer">
        <p>
            --- End of Report | ADB Forensicator v1.0 |
            For Educational Purposes Only ---
        </p>
    </div>

</body>
</html>"""

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"[+] HTML report saved → {output_path}")
