import re
from Levenshtein import distance

def clean_text(text):
    """
    Cleans and normalizes text by lowercasing and removing extra whitespace.
    """
    if not isinstance(text, str):
        return ""
    text = text.lower()
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def check_typosquatting(sender_email):
    """
    Checks if the sender email's domain is a typosquatting attempt against high-value targets.
    Returns a warning message if typosquatting is detected, otherwise None.
    """
    if not sender_email or '@' not in sender_email:
        return None

    try:
        domain = sender_email.split('@')[-1].lower()
    except IndexError:
        return None

    # Map targets to their official domains
    targets = {
        "google.com": "Google",
        "paypal.com": "PayPal",
        "amazon.com": "Amazon",
        "microsoft.com": "Microsoft",
        "apple.com": "Apple",
        "netflix.com": "Netflix"
    }

    for official_domain, target_name in targets.items():
        dist = distance(domain, official_domain)

        # Distance 0 means it matches the official domain exactly (Safe)
        if dist == 0:
            continue

        # Distance 1 or 2 means it is very close but not exact (Suspicious)
        if 1 <= dist <= 2:
            return f"⚠️ Suspicious Domain Detected: '{domain}' is very similar to {target_name} ({official_domain}). Possible Typosquatting!"

    return None
