"""
Cross-Source Corroboration Module
Searches RSS feeds from trusted sources to verify if the same story
is being reported by multiple independent outlets.
"""

import feedparser
import re
from typing import Tuple
from difflib import SequenceMatcher
import logging
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

# Configure feedparser to use requests for better reliability
feedparser.USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"

logger = logging.getLogger(__name__)

# RSS feeds from trusted news sources
# Using multiple reliable RSS feed endpoints
TRUSTED_RSS_FEEDS = {
    # International sources
    "bbc.com": "https://feeds.bbci.co.uk/news/world/rss.xml",
    "reuters.com": "https://www.reuters.com/rssfeed/worldnews",
    "theguardian.com": "https://www.theguardian.com/international/rss",
    "aljazeera.com": "https://www.aljazeera.com/xml/rss/all.xml",
    "npr.org": "https://feeds.npr.org/1001/rss.xml",
    "apnews.com": "https://rsshub.app/apnews/topics/apf-topnews",
    
    # Indian sources
    "thehindu.com": "https://www.thehindu.com/news/feeder/default.rss",
    "ndtv.com": "https://feeds.feedburner.com/ndtvnews-top-stories",
    "indianexpress.com": "https://indianexpress.com/feed/",
    "hindustantimes.com": "https://www.hindustantimes.com/rss/topnews/rssfeed.xml",
    
    # Additional international
    "cnn.com": "http://rss.cnn.com/rss/edition_world.rss",
    "nytimes.com": "https://rss.nytimes.com/services/xml/rss/nyt/World.xml",
}

# Cache for RSS feed entries (simple in-memory cache)
_feed_cache = {}


def extract_keywords(text: str, min_length: int = 4) -> set[str]:
    """
    Extract significant keywords from text for matching.
    
    Args:
        text: The text to extract keywords from.
        min_length: Minimum word length to consider.
        
    Returns:
        Set of lowercase keywords.
    """
    # Remove common stop words
    stop_words = {
        "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
        "of", "with", "by", "from", "as", "is", "was", "are", "were", "been",
        "be", "have", "has", "had", "do", "does", "did", "will", "would",
        "could", "should", "may", "might", "must", "shall", "can", "this",
        "that", "these", "those", "it", "its", "they", "them", "their",
        "he", "she", "him", "her", "his", "we", "us", "our", "you", "your",
        "what", "which", "who", "whom", "when", "where", "why", "how",
        "all", "each", "every", "both", "few", "more", "most", "other",
        "some", "such", "no", "nor", "not", "only", "own", "same", "so",
        "than", "too", "very", "just", "also", "now", "here", "there",
        "says", "said", "new", "news", "report", "reports", "according",
    }
    
    # Extract words
    words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
    
    # Filter by length and stop words
    keywords = {
        word for word in words
        if len(word) >= min_length and word not in stop_words
    }
    
    return keywords


def calculate_similarity(keywords1: set[str], keywords2: set[str]) -> float:
    """
    Calculate similarity between two sets of keywords.
    Uses both Jaccard similarity and overlap coefficient for better matching.
    
    Args:
        keywords1: First set of keywords.
        keywords2: Second set of keywords.
        
    Returns:
        Similarity score between 0 and 1.
    """
    if not keywords1 or not keywords2:
        return 0.0
    
    intersection = keywords1 & keywords2
    
    # If we have good intersection, that's a strong signal
    if len(intersection) >= 3:
        return 0.5 + (len(intersection) / max(len(keywords1), len(keywords2))) * 0.5
    
    # Jaccard similarity
    union = keywords1 | keywords2
    jaccard = len(intersection) / len(union)
    
    # Overlap coefficient (percentage of smaller set that overlaps)
    overlap = len(intersection) / min(len(keywords1), len(keywords2))
    
    # Use higher of the two for more lenient matching
    return max(jaccard, overlap * 0.7)


def fetch_feed_entries(feed_url: str, source: str) -> list[dict]:
    """
    Fetch and parse RSS feed entries.
    
    Args:
        feed_url: URL of the RSS feed.
        source: Source domain name.
        
    Returns:
        List of feed entry dictionaries.
    """
    try:
        feed = feedparser.parse(feed_url)
        entries = []
        
        for entry in feed.entries[:20]:  # Limit to recent 20 entries
            title = entry.get("title", "")
            summary = entry.get("summary", entry.get("description", ""))
            
            entries.append({
                "source": source,
                "title": title,
                "summary": summary,
                "keywords": extract_keywords(title + " " + summary),
                "link": entry.get("link", ""),
            })
        
        return entries
        
    except Exception as e:
        logger.warning(f"Failed to fetch feed from {source}: {e}")
        return []


def search_corroborating_sources(
    title: str,
    summary: str = "",
    threshold: float = 0.15  # Lowered for better matching across sources
) -> Tuple[int, list[str], list[dict]]:
    """
    Search for corroborating reports from trusted sources.
    
    Args:
        title: The article title to search for.
        summary: The article summary (optional).
        threshold: Minimum similarity threshold for a match.
        
    Returns:
        Tuple of (bonus points, list of corroborating domains, matched articles).
    """
    # Extract keywords from the source article
    source_text = title + " " + (summary or "")
    source_keywords = extract_keywords(source_text)
    
    if len(source_keywords) < 3:
        logger.info("Not enough keywords to search for corroboration")
        return 0, [], []
    
    corroborating_sources = []
    matched_articles = []
    
    # Search each trusted feed
    for source, feed_url in TRUSTED_RSS_FEEDS.items():
        try:
            entries = fetch_feed_entries(feed_url, source)
            
            for entry in entries:
                similarity = calculate_similarity(source_keywords, entry["keywords"])
                
                if similarity >= threshold:
                    if source not in corroborating_sources:
                        corroborating_sources.append(source)
                        matched_articles.append({
                            "source": source,
                            "title": entry["title"],
                            "similarity": round(similarity, 2),
                            "link": entry["link"],
                        })
                    break  # One match per source is enough
                    
        except Exception as e:
            logger.warning(f"Error searching {source}: {e}")
            continue
    
    # Calculate bonus
    num_sources = len(corroborating_sources)
    if num_sources >= 3:
        bonus = 15
    elif num_sources >= 1:
        bonus = 5
    else:
        bonus = 0
    
    logger.info(f"Found {num_sources} corroborating sources, bonus: {bonus}")
    
    return bonus, corroborating_sources, matched_articles


def get_corroboration_result(title: str, summary: str = "") -> dict:
    """
    Get full corroboration analysis result.
    
    Args:
        title: The article title.
        summary: The article summary.
        
    Returns:
        Dictionary with corroboration details.
    """
    bonus, sources, matches = search_corroborating_sources(title, summary)
    
    return {
        "corroboration_bonus": bonus,
        "corroborated_sources": sources,
        "num_sources": len(sources),
        "matched_articles": matches,
    }
