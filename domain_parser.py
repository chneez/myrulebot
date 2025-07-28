from urllib.parse import urlparse

def extract_domain(text):
    try:
        parsed = urlparse(text if '://' in text else 'http://' + text)
        hostname = parsed.hostname
        if not hostname:
            return None
        parts = hostname.split('.')
        return '.'.join(parts[-2:]) if len(parts) >= 2 else hostname
    except:
        return None
