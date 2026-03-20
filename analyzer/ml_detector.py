import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler


def ml_detect_call_anomalies(calls):
    if calls is None or len(calls) < 3:
        print("[-] Not enough call data for ML detection")
        return []

    print("[*] ML: Analyzing call patterns...")
    flags = []

    try:
        # ── Feature Engineering ───────────────────────────────────
        df = calls.copy()
        df['duration']     = pd.to_numeric(df['duration'], errors='coerce').fillna(0)
        df['hour']         = pd.to_datetime(df['date'], errors='coerce').dt.hour.fillna(0)
        df['is_missed']    = (df['type'] == 'Missed').astype(int)
        df['is_outgoing']  = (df['type'] == 'Outgoing').astype(int)

        # Count calls per number
        call_freq = df['number'].value_counts().to_dict()
        df['call_frequency'] = df['number'].map(call_freq)

        # Features for ML
        features = df[[
            'duration',
            'hour',
            'is_missed',
            'is_outgoing',
            'call_frequency'
        ]].fillna(0)

        # ── Isolation Forest ──────────────────────────────────────
        scaler = StandardScaler()
        scaled = scaler.fit_transform(features)

        model = IsolationForest(
            contamination=0.2,
            random_state=42,
            n_estimators=100
        )
        predictions = model.fit_predict(scaled)
        scores      = model.score_samples(scaled)

        # ── Flag Anomalies ────────────────────────────────────────
        for i, (pred, score) in enumerate(zip(predictions, scores)):
            if pred == -1:
                row = df.iloc[i]
                reason = []

                if row['duration'] > df['duration'].mean() + 2 * df['duration'].std():
                    reason.append(f"unusually long duration ({row['duration']}s)")

                if row['hour'] < 6 or row['hour'] > 23:
                    reason.append(f"odd hour ({int(row['hour'])}:00)")

                if row['call_frequency'] >= 3:
                    reason.append(
                        f"high frequency to {row['number']} "
                        f"({int(row['call_frequency'])} calls)"
                    )

                if not reason:
                    reason.append("unusual pattern detected by ML")

                flags.append(
                    f"ML CALL ANOMALY: {row['number']} | "
                    f"{str(row['date'])[:19]} | "
                    f"{', '.join(reason)} | "
                    f"Score: {score:.3f}"
                )

        print(f"[+] ML: {len(flags)} call anomalies detected!")

    except Exception as e:
        print(f"[-] ML call detection error: {e}")

    return flags


def ml_detect_sms_anomalies(sms):
    if sms is None or len(sms) < 3:
        print("[-] Not enough SMS data for ML detection")
        return []

    print("[*] ML: Analyzing SMS patterns...")
    flags = []

    try:
        df = sms.copy()
        df['hour']          = pd.to_datetime(df['date'], errors='coerce').dt.hour.fillna(0)
        df['body_length']   = df['body'].astype(str).apply(len)
        df['is_sent']       = (df['type'] == 'Sent').astype(int)

        # Count SMS per address
        sms_freq = df['address'].value_counts().to_dict()
        df['sms_frequency'] = df['address'].map(sms_freq)

        # Suspicious keywords score
        keywords = ['urgent', 'password', 'otp', 'bank',
                    'transaction', 'verify', 'click', 'free']
        def keyword_score(body):
            body_lower = str(body).lower()
            return sum(1 for k in keywords if k in body_lower)

        df['keyword_score'] = df['body'].apply(keyword_score)

        features = df[[
            'hour',
            'body_length',
            'is_sent',
            'sms_frequency',
            'keyword_score'
        ]].fillna(0)

        scaler = StandardScaler()
        scaled = scaler.fit_transform(features)

        model = IsolationForest(
            contamination=0.2,
            random_state=42,
            n_estimators=100
        )
        predictions = model.fit_predict(scaled)
        scores      = model.score_samples(scaled)

        for i, (pred, score) in enumerate(zip(predictions, scores)):
            if pred == -1:
                row = df.iloc[i]
                reason = []

                if row['hour'] < 6 or row['hour'] > 23:
                    reason.append(f"odd hour ({int(row['hour'])}:00)")

                if row['body_length'] > df['body_length'].mean() + 2 * df['body_length'].std():
                    reason.append(
                        f"unusually long message ({int(row['body_length'])} chars)")

                if row['keyword_score'] > 0:
                    reason.append(
                        f"contains {int(row['keyword_score'])} suspicious keywords")

                if row['sms_frequency'] >= 3:
                    reason.append(
                        f"high frequency from {row['address']} "
                        f"({int(row['sms_frequency'])} msgs)"
                    )

                if not reason:
                    reason.append("unusual pattern detected by ML")

                flags.append(
                    f"ML SMS ANOMALY: {row['address']} | "
                    f"{str(row['date'])[:19]} | "
                    f"{', '.join(reason)} | "
                    f"Score: {score:.3f}"
                )

        print(f"[+] ML: {len(flags)} SMS anomalies detected!")

    except Exception as e:
        print(f"[-] ML SMS detection error: {e}")

    return flags


def ml_detect_browser_anomalies(browser):
    if browser is None or len(browser) < 3:
        print("[-] Not enough browser data for ML detection")
        return []

    print("[*] ML: Analyzing browser patterns...")
    flags = []

    try:
        df = browser.copy()
        df['visit_count']  = pd.to_numeric(
            df.get('visit_count', 1), errors='coerce').fillna(1)
        df['url_length']   = df['url'].astype(str).apply(len)

        # Suspicious domain check
        suspicious = ['pastebin', 'ngrok', 'tor', 'onion',
                      'tempmail', 'protonmail', 'vpn']
        def suspicious_score(url):
            url_lower = str(url).lower()
            return sum(1 for s in suspicious if s in url_lower)

        df['suspicious_score'] = df['url'].apply(suspicious_score)

        features = df[[
            'visit_count',
            'url_length',
            'suspicious_score'
        ]].fillna(0)

        scaler = StandardScaler()
        scaled = scaler.fit_transform(features)

        model = IsolationForest(
            contamination=0.2,
            random_state=42,
            n_estimators=100
        )
        predictions = model.fit_predict(scaled)
        scores      = model.score_samples(scaled)

        for i, (pred, score) in enumerate(zip(predictions, scores)):
            if pred == -1:
                row = df.iloc[i]
                reason = []

                if row['suspicious_score'] > 0:
                    reason.append("suspicious domain detected")

                if row['url_length'] > 200:
                    reason.append(
                        f"unusually long URL ({int(row['url_length'])} chars)")

                if not reason:
                    reason.append("unusual browsing pattern")

                flags.append(
                    f"ML BROWSER ANOMALY: {str(row['url'])[:60]} | "
                    f"{', '.join(reason)} | "
                    f"Score: {score:.3f}"
                )

        print(f"[+] ML: {len(flags)} browser anomalies detected!")

    except Exception as e:
        print(f"[-] ML browser detection error: {e}")

    return flags


def run_ml_detection(calls, sms, browser):
    print("\n===== ML ANOMALY DETECTION =====")
    all_flags = []

    call_flags    = ml_detect_call_anomalies(calls)
    sms_flags     = ml_detect_sms_anomalies(sms)
    browser_flags = ml_detect_browser_anomalies(browser)

    all_flags.extend(call_flags)
    all_flags.extend(sms_flags)
    all_flags.extend(browser_flags)

    print(f"\n[+] ML Total: {len(all_flags)} anomalies detected!")
    return all_flags