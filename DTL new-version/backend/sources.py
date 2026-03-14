"""
Source Reputation Database
Contains reputation scores for known news sources.
Scores range from 0-100 where higher means more trustworthy.
"""

from urllib.parse import urlparse

# Reputation scores for known sources
# Categories:
# - Trusted (85-95): Major established news organizations
# - Moderate (60-75): Regional/specialized sources
# - Low (10-50): Tabloids, satire, known unreliable sources
SOURCE_REPUTATION = {
    # Trusted International Sources (85-95)
    "bbc.com": 95,
    "bbc.co.uk": 95,
    "reuters.com": 95,
    "apnews.com": 95,
    "theguardian.com": 90,
    "nytimes.com": 90,
    "washingtonpost.com": 88,
    "economist.com": 90,
    "npr.org": 88,
    "pbs.org": 88,
    "aljazeera.com": 85,
    "dw.com": 88,
    "france24.com": 85,
    
    # Trusted Indian Sources (85-95)
    "thehindu.com": 90,
    "indianexpress.com": 88,
    "hindustantimes.com": 85,
    "ndtv.com": 85,
    "ddnews.gov.in": 90,  # DD News - Official government broadcaster
    "thewire.in": 82,
    "scroll.in": 80,
    "livemint.com": 85,
    "business-standard.com": 85,
    
    # Moderate Sources (60-75)
    "timesofindia.indiatimes.com": 70,
    "indiatoday.in": 72,
    "news18.com": 68,
    "firstpost.com": 70,
    "deccanherald.com": 75,
    "telegraphindia.com": 75,
    
    # Tabloids / Sensational Sources (30-50)
    "dailymail.co.uk": 40,
    "thesun.co.uk": 35,
    "nypost.com": 45,
    "mirror.co.uk": 40,
    
    # Known Satire Sites (10-20)
    "theonion.com": 15,
    "babylonbee.com": 15,
    "clickhole.com": 10,
    "fakingnews.com": 15,
}

# Default score for unknown sources
DEFAULT_SCORE = 60


def extract_domain(url: str) -> str:
    """
    Extract the domain from a URL.
    Handles www. prefix and subdomains.
    """
    try:
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        
        # Remove www. prefix
        if domain.startswith("www."):
            domain = domain[4:]
        
        return domain
    except Exception:
        return ""


def get_source_score(url: str) -> int:
    """
    Get the reputation score for a given URL's source.
    Returns DEFAULT_SCORE if the source is not in the database.
    """
    domain = extract_domain(url)
    
    # Direct match
    if domain in SOURCE_REPUTATION:
        return SOURCE_REPUTATION[domain]
    
    # Try matching parent domain (e.g., news.bbc.co.uk -> bbc.co.uk)
    parts = domain.split(".")
    if len(parts) > 2:
        # Try last two parts (e.g., bbc.co.uk)
        parent = ".".join(parts[-2:])
        if parent in SOURCE_REPUTATION:
            return SOURCE_REPUTATION[parent]
        
        # Try last three parts for .co.uk style domains
        if len(parts) > 3:
            parent = ".".join(parts[-3:])
            if parent in SOURCE_REPUTATION:
                return SOURCE_REPUTATION[parent]
    
    return DEFAULT_SCORE


def get_source_category(score: int) -> str:
    """
    Get the category label for a source based on its score.
    """
    if score >= 85:
        return "Trusted"
    elif score >= 60:
        return "Moderate"
    elif score >= 30:
        return "Low Reliability"
    else:
        return "Satire/Unreliable"


def is_trusted_source(url: str) -> bool:
    """
    Check if a URL is from a trusted source (score >= 80).
    """
    return get_source_score(url) >= 80
