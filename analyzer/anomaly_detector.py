def detect_suspicious(calls, sms, browser):
    flags = []

    # Flag unknown numbers with high call frequency
    if calls is not None:
        freq = calls['number'].value_counts()
        for number, count in freq.items():
            if count >= 3:
                flags.append(f"⚠️  HIGH FREQUENCY CALLS to {number} ({count} times)")

    # Flag suspicious SMS keywords
    if sms is not None:
        keywords = ['transaction', 'password', 'otp', 'urgent', 'bank', 'location']
        for _, row in sms.iterrows():
            for keyword in keywords:
                if keyword.lower() in str(row['body']).lower():
                    flags.append(f"⚠️  SUSPICIOUS KEYWORD '{keyword}' found in SMS from {row['address']}")

    # Flag suspicious URLs
    if browser is not None:
        suspicious_domains = ['pastebin', 'ngrok', 'tor', 'onion', 'tempmail']
        for _, row in browser.iterrows():
            for domain in suspicious_domains:
                if domain.lower() in str(row['url']).lower():
                    flags.append(f"⚠️  SUSPICIOUS URL visited: {row['url']}")

    return flags