"""
Article Extractor Module
Uses newspaper3k to extract article content from URLs.
"""

from newspaper import Article
from typing import Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class ExtractedArticle:
    """Data class to hold extracted article information."""
    url: str
    title: str
    text: str
    authors: list[str]
    publish_date: Optional[datetime]
    top_image: Optional[str]
    success: bool
    error: Optional[str] = None


def extract_article(url: str) -> ExtractedArticle:
    """
    Extract article content from a given URL.
    
    Args:
        url: The URL of the article to extract.
        
    Returns:
        ExtractedArticle with the extracted content or error information.
    """
    try:
        # Create and download the article
        article = Article(url)
        article.download()
        article.parse()
        
        # Validate that we got meaningful content
        if not article.text or len(article.text.strip()) < 100:
            return ExtractedArticle(
                url=url,
                title="",
                text="",
                authors=[],
                publish_date=None,
                top_image=None,
                success=False,
                error="Could not extract sufficient article content"
            )
        
        return ExtractedArticle(
            url=url,
            title=article.title or "Untitled",
            text=article.text,
            authors=article.authors if article.authors else [],
            publish_date=article.publish_date,
            top_image=article.top_image,
            success=True
        )
        
    except Exception as e:
        return ExtractedArticle(
            url=url,
            title="",
            text="",
            authors=[],
            publish_date=None,
            top_image=None,
            success=False,
            error=f"Failed to extract article: {str(e)}"
        )


def get_article_preview(article: ExtractedArticle, max_chars: int = 500) -> str:
    """
    Get a preview of the article text.
    
    Args:
        article: The extracted article.
        max_chars: Maximum characters to include in preview.
        
    Returns:
        Truncated article text.
    """
    if not article.text:
        return ""
    
    text = article.text[:max_chars]
    if len(article.text) > max_chars:
        # Try to cut at a sentence boundary
        last_period = text.rfind(".")
        if last_period > max_chars * 0.5:
            text = text[:last_period + 1]
        else:
            text += "..."
    
    return text
