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

def get_trusted_domains():
    """
    Returns a set of trusted CORPORATE domains.
    Public email providers (Gmail, Yahoo, Outlook, etc.) are EXCLUDED
    because they are frequently used by phishers.
    """
    return {
        # Tech Giants (Corporate Only)
        "google.com", "youtube.com", "facebook.com", "amazon.com", "microsoft.com",
        "apple.com", "whatsapp.com", "instagram.com", "linkedin.com", "twitter.com",
        "x.com", "netflix.com", "openai.com", "zoom.us",
        "dropbox.com", "salesforce.com", "adobe.com", "ibm.com", "oracle.com",
        "intel.com", "cisco.com", "hp.com", "dell.com", "spotify.com", "reddit.com",
        "pinterest.com", "tumblr.com", "flickr.com", "github.com", "gitlab.com",
        "bitbucket.org", "stackoverflow.com", "slack.com", "atlassian.com", "trello.com",
        "asana.com", "notion.so", "figma.com", "canva.com",

        # E-commerce & Retail
        "ebay.com", "walmart.com", "target.com", "bestbuy.com", "costco.com",
        "homedepot.com", "ikea.com", "nike.com", "adidas.com", "shopify.com",
        "etsy.com", "aliexpress.com", "alibaba.com", "wayfair.com",

        # Finance & Payments
        "paypal.com", "stripe.com", "square.com", "visa.com", "mastercard.com",
        "amex.com", "chase.com", "bankofamerica.com", "wellsfargo.com", "citi.com",
        "hsbc.com", "barclays.com", "jpmorganchase.com", "goldmansachs.com",
        "morganstanley.com", "fidelity.com", "schwab.com", "vanguard.com",
        "intuit.com", "mint.com", "wise.com", "revolut.com", "coinbase.com",

        # News & Media
        "cnn.com", "bbc.com", "bbc.co.uk", "nytimes.com", "wsj.com", "forbes.com",
        "bloomberg.com", "reuters.com", "theguardian.com", "washingtonpost.com",
        "huffpost.com", "buzzfeed.com", "vice.com", "usatoday.com", "foxnews.com",
        "cnbc.com", "techcrunch.com", "wired.com", "theverge.com", "engadget.com",

        # Other Trusted Services
        "wikipedia.org", "archive.org", "medium.com", "stackexchange.com",
        "tripadvisor.com", "booking.com", "airbnb.com", "expedia.com",
        "uber.com", "lyft.com", "doordash.com", "grubhub.com", "instacart.com",
        "fedex.com", "ups.com", "dhl.com", "usps.com"
    }

def is_trusted_domain(sender_email):
    """
    Checks if the sender's domain is in the trusted whitelist.
    Supports subdomains (e.g., support.google.com is trusted if google.com is trusted).
    """
    if not sender_email or '@' not in sender_email:
        return False

    try:
        domain = sender_email.split('@')[-1].lower()
    except IndexError:
        return False

    trusted_domains = get_trusted_domains()

    # Check exact match
    if domain in trusted_domains:
        return True

    # Check subdomains (e.g., support.google.com -> google.com)
    for trusted in trusted_domains:
        if domain.endswith("." + trusted):
            return True

    return False

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

    # If it is a trusted domain, it's NOT a typosquatting attempt
    if is_trusted_domain(sender_email):
        return None

    # Map targets to their official domains
    targets = {
        "google.com": "Google",
        "paypal.com": "PayPal",
        "amazon.com": "Amazon",
        "microsoft.com": "Microsoft",
        "apple.com": "Apple",
        "netflix.com": "Netflix",
        "facebook.com": "Facebook",
        "instagram.com": "Instagram",
        "linkedin.com": "LinkedIn",
        "twitter.com": "Twitter",
        "dropbox.com": "Dropbox",
        "adobe.com": "Adobe",
        "ebay.com": "eBay",
        "walmart.com": "Walmart",
        "chase.com": "Chase",
        "bankofamerica.com": "Bank of America",
        "wellsfargo.com": "Wells Fargo"
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
