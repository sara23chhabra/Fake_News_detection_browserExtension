"""
Credibility Scoring Module
Combines all factors to calculate final credibility score.
"""

from sources import get_source_score, get_source_category
from sensationalism import calculate_sensationalism_penalty
from corroboration import get_corroboration_result
from typing import Optional


def get_credibility_label(score: int) -> str:
    """
    Get the credibility label for a given score.
    
    Args:
        score: Credibility score (0-100).
        
    Returns:
        Label string: "High", "Medium", or "Low".
    """
    if score >= 75:
        return "High"
    elif score >= 50:
        return "Medium"
    else:
        return "Low"


def get_label_color(label: str) -> str:
    """
    Get the display color for a credibility label.
    
    Args:
        label: Credibility label.
        
    Returns:
        Color code for UI display.
    """
    colors = {
        "High": "#22c55e",      # Green
        "Medium": "#f59e0b",    # Amber
        "Low": "#ef4444",       # Red
    }
    return colors.get(label, "#6b7280")


def calculate_credibility(
    url: str,
    title: str,
    text: str,
    summary: Optional[str] = None,
    skip_corroboration: bool = False
) -> dict:
    """
    Calculate the overall credibility score for an article.
    
    Formula:
        Final Score = Source Score - Sensationalism Penalty + Corroboration Bonus
    
    Args:
        url: The article URL (for source reputation).
        title: The article title.
        text: The full article text.
        summary: Optional summary for corroboration search.
        skip_corroboration: Skip RSS search (for faster results).
        
    Returns:
        Dictionary with complete credibility analysis.
    """
    # 1. Get source reputation score
    source_score = get_source_score(url)
    source_category = get_source_category(source_score)
    
    # 2. Calculate sensationalism penalty
    sensationalism = calculate_sensationalism_penalty(title, text)
    sensationalism_penalty = sensationalism["total_penalty"]
    
    # 3. Get corroboration bonus (optional)
    if skip_corroboration:
        corroboration = {
            "corroboration_bonus": 0,
            "corroborated_sources": [],
            "num_sources": 0,
            "matched_articles": [],
        }
    else:
        corroboration = get_corroboration_result(title, summary or "")
    
    corroboration_bonus = corroboration["corroboration_bonus"]
    
    # 4. Calculate final score
    final_score = source_score - sensationalism_penalty + corroboration_bonus
    
    # Clamp to 0-100 range
    final_score = max(0, min(100, final_score))
    
    # 5. Get label
    label = get_credibility_label(final_score)
    label_color = get_label_color(label)
    
    return {
        # Final results
        "credibility_score": final_score,
        "credibility_label": label,
        "label_color": label_color,
        
        # Score breakdown
        "source_score": source_score,
        "source_category": source_category,
        "sensationalism_penalty": sensationalism_penalty,
        "corroboration_bonus": corroboration_bonus,
        
        # Detailed breakdown
        "sensationalism_details": {
            "clickbait_penalty": sensationalism["clickbait_penalty"],
            "clickbait_phrases": sensationalism["clickbait_phrases"],
            "sensational_words": sensationalism["sensational_words"],
            "caps_penalty": sensationalism["caps_penalty"],
            "punctuation_penalty": sensationalism["punctuation_penalty"],
        },
        "corroboration_details": {
            "corroborated_sources": corroboration["corroborated_sources"],
            "num_sources": corroboration["num_sources"],
            "matched_articles": corroboration.get("matched_articles", []),
        },
        
        # Explanation
        "explanation": generate_explanation(
            final_score, label, source_score, source_category,
            sensationalism_penalty, corroboration_bonus,
            corroboration["corroborated_sources"]
        ),
    }


def generate_explanation(
    score: int,
    label: str,
    source_score: int,
    source_category: str,
    sensationalism_penalty: int,
    corroboration_bonus: int,
    corroborated_sources: list[str]
) -> str:
    """
    Generate a human-readable explanation of the credibility score.
    """
    parts = []
    
    # Source explanation
    parts.append(f"Source is rated as '{source_category}' ({source_score}/100).")
    
    # Sensationalism explanation
    if sensationalism_penalty > 0:
        parts.append(f"Detected sensational language (-{sensationalism_penalty} points).")
    else:
        parts.append("No significant sensationalism detected.")
    
    # Corroboration explanation
    if corroboration_bonus > 0:
        sources_str = ", ".join(corroborated_sources[:3])
        parts.append(f"Story corroborated by {len(corroborated_sources)} source(s): {sources_str} (+{corroboration_bonus} points).")
    else:
        parts.append("No independent corroboration found (no penalty applied).")
    
    # Overall assessment
    if label == "High":
        parts.append("Overall: This article appears to be from a credible source with quality journalism.")
    elif label == "Medium":
        parts.append("Overall: This article has moderate credibility. Consider cross-referencing with other sources.")
    else:
        parts.append("Overall: This article shows signs of low credibility. Exercise caution and verify claims independently.")
    
    return " ".join(parts)
