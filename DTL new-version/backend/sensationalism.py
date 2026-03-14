"""
Sensationalism Detection Module
Analyzes article titles and content for clickbait indicators.
Returns a penalty score (0-30) where higher means more sensational.
"""

import re
from typing import Tuple

# Clickbait phrases that indicate sensationalism
CLICKBAIT_PHRASES = [
    "you won't believe",
    "will shock you",
    "this is why",
    "what happened next",
    "the reason why",
    "doctors hate",
    "one weird trick",
    "mind-blowing",
    "jaw-dropping",
    "can't stop laughing",
    "broke the internet",
    "going viral",
    "you need to see",
    "before it's too late",
    "what they don't want you to know",
    "the truth about",
    "exposed",
    "caught on camera",
    "is this the end",
    "you'll never guess",
]

# Sensational/emotional words
SENSATIONAL_WORDS = [
    "shocking",
    "bombshell",
    "explosive",
    "devastating",
    "horrifying",
    "terrifying",
    "outrageous",
    "unbelievable",
    "incredible",
    "insane",
    "crazy",
    "epic",
    "massive",
    "huge",
    "breaking",
    "urgent",
    "alert",
    "warning",
    "scandal",
    "controversy",
    "disaster",
    "crisis",
    "chaos",
    "fury",
    "rage",
    "slams",
    "destroys",
    "obliterates",
    "annihilates",
    "brutal",
    "savage",
]


def check_clickbait_phrases(text: str) -> Tuple[int, list[str]]:
    """
    Check for clickbait phrases in the text.
    
    Args:
        text: The text to analyze (usually title).
        
    Returns:
        Tuple of (penalty points, list of found phrases).
    """
    text_lower = text.lower()
    found_phrases = []
    
    for phrase in CLICKBAIT_PHRASES:
        if phrase in text_lower:
            found_phrases.append(phrase)
    
    # 3 points per clickbait phrase, max 12
    penalty = min(len(found_phrases) * 3, 12)
    return penalty, found_phrases


def check_sensational_words(text: str) -> Tuple[int, list[str]]:
    """
    Check for sensational/emotional words in the text.
    
    Args:
        text: The text to analyze.
        
    Returns:
        Tuple of (penalty points, list of found words).
    """
    text_lower = text.lower()
    found_words = []
    
    for word in SENSATIONAL_WORDS:
        # Use word boundary matching
        pattern = r'\b' + re.escape(word) + r'\b'
        if re.search(pattern, text_lower):
            found_words.append(word)
    
    # 2 points per sensational word, max 10
    penalty = min(len(found_words) * 2, 10)
    return penalty, found_words


def check_caps_abuse(title: str) -> int:
    """
    Check if the title has excessive capitalization.
    
    Args:
        title: The article title.
        
    Returns:
        Penalty points (0-5).
    """
    if not title or len(title) < 10:
        return 0
    
    # Count uppercase letters
    upper_count = sum(1 for c in title if c.isupper())
    letter_count = sum(1 for c in title if c.isalpha())
    
    if letter_count == 0:
        return 0
    
    caps_ratio = upper_count / letter_count
    
    # Penalize if more than 50% caps
    if caps_ratio > 0.7:
        return 5
    elif caps_ratio > 0.5:
        return 3
    
    return 0


def check_punctuation_abuse(title: str) -> int:
    """
    Check for excessive punctuation in the title.
    
    Args:
        title: The article title.
        
    Returns:
        Penalty points (0-3).
    """
    if not title:
        return 0
    
    # Count exclamation marks and question marks
    exclamation_count = title.count("!")
    question_count = title.count("?")
    
    penalty = 0
    
    # Multiple exclamation marks
    if exclamation_count > 1:
        penalty += min(exclamation_count, 2)
    
    # Multiple question marks
    if question_count > 1:
        penalty += 1
    
    # Check for !! or ?? patterns
    if "!!" in title or "??" in title or "!?" in title or "?!" in title:
        penalty += 1
    
    return min(penalty, 3)


def calculate_sensationalism_penalty(title: str, text: str = "") -> dict:
    """
    Calculate the total sensationalism penalty for an article.
    
    Args:
        title: The article title.
        text: The article text (optional, uses first 500 chars).
        
    Returns:
        Dictionary with penalty breakdown and total.
    """
    # Analyze title primarily
    clickbait_penalty, clickbait_phrases = check_clickbait_phrases(title)
    
    # Check for sensational words in title and first part of text
    combined_text = title + " " + text[:500] if text else title
    sensational_penalty, sensational_words = check_sensational_words(combined_text)
    
    caps_penalty = check_caps_abuse(title)
    punctuation_penalty = check_punctuation_abuse(title)
    
    total_penalty = clickbait_penalty + sensational_penalty + caps_penalty + punctuation_penalty
    
    # Cap total penalty at 30
    total_penalty = min(total_penalty, 30)
    
    return {
        "total_penalty": total_penalty,
        "clickbait_penalty": clickbait_penalty,
        "clickbait_phrases": clickbait_phrases,
        "sensational_penalty": sensational_penalty,
        "sensational_words": sensational_words,
        "caps_penalty": caps_penalty,
        "punctuation_penalty": punctuation_penalty,
    }
