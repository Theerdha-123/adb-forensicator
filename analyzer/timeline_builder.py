def build_timeline(calls, sms, browser, firefox=None):
    events = []

    if calls is not None:
        for _, row in calls.iterrows():
            events.append({
                'time'  : row['date'],
                'type'  : 'CALL',
                'icon'  : 'CALL',
                'detail': f"{row['type']} | {row['number']} | {row['duration']}s"
            })

    if sms is not None:
        for _, row in sms.iterrows():
            events.append({
                'time'  : row['date'],
                'type'  : 'SMS',
                'icon'  : 'SMS',
                'detail': f"{row['type']} | {row['address']} | {str(row['body'])[:60]}"
            })

    if browser is not None:
        for _, row in browser.iterrows():
            events.append({
                'time'  : row['last_visit_time'],
                'type'  : 'BROWSER',
                'icon'  : 'BROWSER',
                'detail': f"Chrome | {row['url'][:80]}"
            })

    if firefox is not None:
        for _, row in firefox.iterrows():
            events.append({
                'time'  : row['last_visit_date'],
                'type'  : 'BROWSER',
                'icon'  : 'BROWSER',
                'detail': f"Firefox | {row['url'][:80]}"
            })

    # Sort safely
    def safe_time(e):
        try:
            return str(e['time'])
        except:
            return ''

    events_valid = [e for e in events
                    if e['time'] is not None
                    and str(e['time']) != 'NaT'
                    and str(e['time']) != 'None']
    events_valid.sort(key=safe_time)
    return events_valid