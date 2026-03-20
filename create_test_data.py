import sqlite3
import os
import time

os.makedirs("test_data", exist_ok=True)

# Chrome timestamp = (unix_timestamp * 1000000) + 11644473600000000
chrome_now = int(time.time() * 1000000) + 11644473600000000

# ── SMS Database ─────────────────────────────────────────────────
conn = sqlite3.connect("test_data/mmssms.db")
conn.execute("DROP TABLE IF EXISTS sms")
conn.execute("CREATE TABLE sms (address TEXT, date INTEGER, body TEXT, type INTEGER)")
messages = [
    ("+91-9876543210", int(time.time()*1000) - 7200000,  "Are you coming tonight?",       1),
    ("+91-9123456789", int(time.time()*1000) - 5400000,  "Yes I'll be there at 8",         2),
    ("+91-9876543210", int(time.time()*1000) - 3600000,  "Bring the documents",            1),
    ("+91-9000000000", int(time.time()*1000) - 1800000,  "Transaction of 50000 done",      1),
    ("+91-9111111111", int(time.time()*1000) - 900000,   "Location shared on maps",        2),
]
conn.executemany("INSERT INTO sms VALUES (?,?,?,?)", messages)
conn.commit()
conn.close()
print("[+] mmssms.db created successfully")

# ── Call Logs Database ───────────────────────────────────────────
conn = sqlite3.connect("test_data/contacts2.db")
conn.execute("DROP TABLE IF EXISTS calls")
conn.execute("CREATE TABLE calls (number TEXT, date INTEGER, duration INTEGER, type INTEGER)")
calls = [
    ("+91-9876543210", int(time.time()*1000) - 86400000, 240,  2),
    ("+91-9123456789", int(time.time()*1000) - 43200000, 0,    3),
    ("+91-9000000000", int(time.time()*1000) - 21600000, 512,  1),
    ("+91-9111111111", int(time.time()*1000) - 10800000, 183,  2),
    ("+91-9222222222", int(time.time()*1000) - 5400000,  0,    3),
]
conn.executemany("INSERT INTO calls VALUES (?,?,?,?)", calls)
conn.commit()
conn.close()
print("[+] contacts2.db created successfully")

# ── Browser History Database ─────────────────────────────────────
conn = sqlite3.connect("test_data/History")
conn.execute("DROP TABLE IF EXISTS urls")
conn.execute("CREATE TABLE urls (url TEXT, title TEXT, visit_count INTEGER, last_visit_time INTEGER)")
urls = [
    ("https://google.com",                 "Google",            45, chrome_now - 1000000000),
    ("https://youtube.com/watch?v=abc",    "Tutorial Video",     3, chrome_now - 2000000000),
    ("https://pastebin.com/xK9mZ2",        "Untitled",           1, chrome_now - 3000000000),
    ("https://maps.google.com?q=airport",  "Airport Location",   2, chrome_now - 4000000000),
    ("https://gmail.com",                  "Gmail",             12, chrome_now - 5000000000),
]
conn.executemany("INSERT INTO urls VALUES (?,?,?,?)", urls)
conn.commit()
conn.close()
print("[+] History (browser) created successfully")

print("\n[+] All test databases created in test_data/ folder!")
print("[+] You can now run: python main.py")

# ── WhatsApp Database ─────────────────────────────────────────────
conn = sqlite3.connect("test_data/msgstore.db")
conn.execute("DROP TABLE IF EXISTS messages")
conn.execute("CREATE TABLE messages (key_remote_jid TEXT, data TEXT, timestamp INTEGER)")
whatsapp = [
    ("91987654321@s.whatsapp.net", "Hey! Did you get the file?",     int(time.time()*1000) - 7200000),
    ("91912345678@s.whatsapp.net", "Meeting postponed to tomorrow",   int(time.time()*1000) - 3600000),
    ("91900000000@s.whatsapp.net", "Send me the location",            int(time.time()*1000) - 1800000),
]
conn.executemany("INSERT INTO messages VALUES (?,?,?)", whatsapp)
conn.commit()
conn.close()
print("[+] msgstore.db (WhatsApp) created successfully")