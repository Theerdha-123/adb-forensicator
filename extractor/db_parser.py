import sqlite3
import pandas as pd
import hashlib
import os

def hash_file(filepath):
    sha256 = hashlib.sha256()
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            sha256.update(chunk)
    return sha256.hexdigest()

def find_db(base_path, db_name):
    for root, dirs, files in os.walk(base_path):
        for file in files:
            if file == db_name:
                return os.path.join(root, file)
    return None

def extract_sms(base_path):
    db_path = find_db(base_path, "mmssms.db")
    if not db_path:
        print("[-] mmssms.db not found")
        return None
    print(f"[+] SMS DB found: {db_path}")
    print(f"[+] SHA256: {hash_file(db_path)}")
    conn = sqlite3.connect(db_path)
    try:
        df = pd.read_sql_query(
            "SELECT address, date, body, type FROM sms ORDER BY date DESC",
            conn
        )
        df['date'] = pd.to_datetime(df['date'], unit='ms')
        df['type'] = df['type'].map({1: 'Received', 2: 'Sent'})
        conn.close()
        return df
    except Exception as e:
        print(f"[-] SMS error: {e}")
        conn.close()
        return None

def extract_calls(base_path):
    db_path = find_db(base_path, "calllog.db")
    if not db_path:
        print("[-] calllog.db not found")
        return None
    print(f"[+] Calls DB found: {db_path}")
    print(f"[+] SHA256: {hash_file(db_path)}")
    conn = sqlite3.connect(db_path)
    try:
        df = pd.read_sql_query(
            "SELECT number, date, duration, type FROM calls ORDER BY date DESC",
            conn
        )
        df['date'] = pd.to_datetime(df['date'], unit='ms')
        df['type'] = df['type'].map({
            1: 'Incoming',
            2: 'Outgoing',
            3: 'Missed'
        })
        conn.close()
        return df
    except Exception as e:
        print(f"[-] Call log error: {e}")
        conn.close()
        return None

def extract_browser(base_path):
    db_path = find_db(base_path, "History")
    if not db_path:
        print("[-] Chrome History not found")
        return None
    print(f"[+] Browser DB found: {db_path}")
    print(f"[+] SHA256: {hash_file(db_path)}")
    conn = sqlite3.connect(db_path)
    try:
        df = pd.read_sql_query(
            "SELECT url, title, visit_count, last_visit_time FROM urls ORDER BY last_visit_time DESC",
            conn
        )
        def chrome_time(t):
            try:
                return pd.Timestamp((t - 11644473600000000) / 1000000, unit='s')
            except:
                return pd.NaT
        df['last_visit_time'] = df['last_visit_time'].apply(chrome_time)
        conn.close()
        return df
    except Exception as e:
        print(f"[-] Browser error: {e}")
        conn.close()
        return None

def extract_firefox(base_path):
    db_path = find_db(base_path, "places.sqlite")
    if not db_path:
        print("[-] Firefox places.sqlite not found")
        return None
    print(f"[+] Firefox DB found: {db_path}")
    print(f"[+] SHA256: {hash_file(db_path)}")
    conn = sqlite3.connect(db_path)
    try:
        df = pd.read_sql_query("""
            SELECT url, title,
                   visit_count_local,
                   visit_count_remote,
                   last_visit_date_local,
                   last_visit_date_remote
            FROM moz_places
            WHERE visit_count_local > 0
               OR visit_count_remote > 0
            ORDER BY last_visit_date_local DESC
        """, conn)
        df['last_visit_date'] = pd.to_datetime(
            df['last_visit_date_local'], unit='us', errors='coerce'
        )
        conn.close()
        return df
    except Exception as e:
        print(f"[-] Firefox error: {e}")
        conn.close()
        return None
  

def extract_contacts(base_path):
    db_path = find_db(base_path, "contacts2.db")
    if not db_path:
        print("[-] Contacts not found")
        return None
    print(f"[+] Contacts DB found: {db_path}")
    conn = sqlite3.connect(db_path)
    try:
        df = pd.read_sql_query("""
            SELECT _id, display_name, last_time_contacted
            FROM raw_contacts
            WHERE deleted = 0
            AND display_name IS NOT NULL
        """, conn)
        conn.close()
        return df
    except Exception as e:
        print(f"[-] Contacts error: {e}")
        conn.close()
        return None

from PIL import Image
from PIL.ExifTags import TAGS
import os

def extract_exif_metadata(base_path):
    photo_path = os.path.join(base_path, "photos")
    if not os.path.exists(photo_path):
        print("[-] No photos folder found")
        return None

    print(f"[+] Photos folder found: {photo_path}")
    results = []

    for root, dirs, files in os.walk(photo_path):
        for file in files:
            if file.lower().endswith(('.jpg', '.jpeg', '.png')):
                filepath = os.path.join(root, file)
                try:
                    img = Image.open(filepath)
                    exif_data = img._getexif()
                    metadata = {
                        'filename' : file,
                        'size_kb'  : os.path.getsize(filepath) // 1024,
                        'format'   : img.format,
                        'dimensions': f"{img.width}x{img.height}",
                        'date_taken': 'N/A',
                        'gps_lat'  : 'N/A',
                        'gps_lon'  : 'N/A',
                        'camera'   : 'N/A',
                        'flash'    : 'N/A',
                    }

                    if exif_data:
                        for tag_id, value in exif_data.items():
                            tag = TAGS.get(tag_id, tag_id)

                            if tag == 'DateTime':
                                metadata['date_taken'] = str(value)

                            elif tag == 'Make' or tag == 'Model':
                                metadata['camera'] = str(value)

                            elif tag == 'Flash':
                                metadata['flash'] = 'Yes' if value else 'No'

                            elif tag == 'GPSInfo':
                                try:
                                    gps = value
                                    # Extract latitude
                                    lat = gps.get(2)
                                    lat_ref = gps.get(1, 'N')
                                    if lat:
                                        lat_deg = float(lat[0])
                                        lat_min = float(lat[1])
                                        lat_sec = float(lat[2])
                                        latitude = lat_deg + lat_min/60 + lat_sec/3600
                                        if lat_ref == 'S':
                                            latitude = -latitude
                                        metadata['gps_lat'] = round(latitude, 6)

                                    # Extract longitude
                                    lon = gps.get(4)
                                    lon_ref = gps.get(3, 'E')
                                    if lon:
                                        lon_deg = float(lon[0])
                                        lon_min = float(lon[1])
                                        lon_sec = float(lon[2])
                                        longitude = lon_deg + lon_min/60 + lon_sec/3600
                                        if lon_ref == 'W':
                                            longitude = -longitude
                                        metadata['gps_lon'] = round(longitude, 6)
                                except:
                                    pass

                    results.append(metadata)
                    print(f"[+] Photo analyzed: {file}")

                except Exception as e:
                    print(f"[-] Error reading {file}: {e}")

    print(f"[+] Total photos analyzed: {len(results)}")
    return results  

import re

def recover_deleted_sms(base_path):
    db_path = find_db(base_path, "mmssms.db")
    if not db_path:
        print("[-] mmssms.db not found")
        return None

    print(f"[+] Scanning for deleted SMS: {db_path}")
    recovered = []

    # ── Method 1: Check deleted flag ─────────────────────────────
    print("[*] Method 1 — Checking deleted flag...")
    conn = sqlite3.connect(db_path)
    try:
        cursor = conn.execute("PRAGMA table_info(sms)")
        columns = [row[1] for row in cursor.fetchall()]

        if 'deleted' in columns:
            df = pd.read_sql_query(
                "SELECT address, date, body, type FROM sms WHERE deleted = 1",
                conn
            )
            if len(df) > 0:
                df['date'] = pd.to_datetime(df['date'], unit='ms')
                df['recovery_method'] = 'Deleted Flag'
                recovered.append(df)
                print(f"[+] Method 1: Found {len(df)} deleted SMS!")
            else:
                print("[-] Method 1: No deleted SMS found")
        else:
            print("[-] Method 1: No deleted flag column")
    except Exception as e:
        print(f"[-] Method 1 error: {e}")
    finally:
        conn.close()

    # ── Method 2: Check sms_restricted table ─────────────────────
    print("[*] Method 2 — Checking restricted table...")
    conn = sqlite3.connect(db_path)
    try:
        cursor = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        )
        tables = [row[0] for row in cursor.fetchall()]

        if 'sms_restricted' in tables:
            df = pd.read_sql_query(
                "SELECT address, date, body, type FROM sms_restricted",
                conn
            )
            if len(df) > 0:
                df['date'] = pd.to_datetime(df['date'], unit='ms')
                df['recovery_method'] = 'Restricted Table'
                recovered.append(df)
                print(f"[+] Method 2: Found {len(df)} restricted SMS!")
            else:
                print("[-] Method 2: No restricted SMS found")
        else:
            print("[-] Method 2: No sms_restricted table")
    except Exception as e:
        print(f"[-] Method 2 error: {e}")
    finally:
        conn.close()

    # ── Method 3: Raw binary scan of database file ────────────────
    print("[*] Method 3 — Scanning raw database for remnants...")
    try:
        with open(db_path, 'rb') as f:
            raw_data = f.read()

        # Convert to string for pattern matching
        raw_text = raw_data.decode('utf-8', errors='ignore')

        # Pattern to find phone numbers and text
        phone_pattern = re.compile(
            r'(\+?[\d\s\-]{7,15})'
        )
        # Look for SMS-like content between null bytes
        chunks = raw_text.split('\x00')
        chunks = [c.strip() for c in chunks
                  if len(c.strip()) > 5
                  and not c.strip().isdigit()]

        raw_recovered = []
        for chunk in chunks:
            # Filter meaningful text chunks
            if (len(chunk) > 3
                    and len(chunk) < 500
                    and any(c.isalpha() for c in chunk)
                    and chunk not in ['SMS', 'MMS',
                                      'address', 'body',
                                      'date', 'type']):
                raw_recovered.append({
                    'address': 'Unknown',
                    'date'   : 'Unknown',
                    'body'   : chunk[:200],
                    'type'   : 'Unknown',
                    'recovery_method': 'Raw Binary Scan'
                })

        if raw_recovered:
            df_raw = pd.DataFrame(raw_recovered[:20])
            recovered.append(df_raw)
            print(f"[+] Method 3: Found {len(raw_recovered)} raw remnants!")
        else:
            print("[-] Method 3: No raw remnants found")

    except Exception as e:
        print(f"[-] Method 3 error: {e}")

    # ── Combine all results ───────────────────────────────────────
    if recovered:
        final = pd.concat(recovered, ignore_index=True)
        print(f"\n[+] Total recovered: {len(final)} deleted SMS!")
        return final
    else:
        print("[-] No deleted SMS could be recovered")
        return None        