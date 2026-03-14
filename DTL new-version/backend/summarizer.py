"""
Article Summarizer Module
Uses HuggingFace Transformers to generate article summaries.
"""

from transformers import pipeline
from typing import Optional
import logging

logger = logging.getLogger(__name__)

# Global summarizer instance (lazy loaded)
_summarizer = None


def get_summarizer():
    """
    Get or initialize the summarization pipeline.
    Uses lazy loading to reduce startup time.
    """
    global _summarizer
    
    if _summarizer is None:
        logger.info("Loading summarization model (facebook/bart-large-cnn)...")
        try:
            _summarizer = pipeline(
                "summarization",
                model="facebook/bart-large-cnn",
                device=-1  # Use CPU (-1), set to 0 for GPU
            )
            logger.info("Summarization model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load primary model, trying t5-small: {e}")
            # Fallback to smaller model
            _summarizer = pipeline(
                "summarization",
                model="t5-small",
                device=-1
            )
            logger.info("Fallback model (t5-small) loaded successfully")
    
    return _summarizer


def summarize_text(text: str, max_length: int = 130, min_length: int = 30) -> Optional[str]:
    """
    Generate a summary of the given text.
    
    Args:
        text: The article text to summarize.
        max_length: Maximum length of the summary in tokens.
        min_length: Minimum length of the summary in tokens.
        
    Returns:
        A 2-4 sentence summary or None if summarization fails.
    """
    if not text or len(text.strip()) < 100:
        return None
    
    try:
        summarizer = get_summarizer()
        
        # Truncate text if too long (BART has 1024 token limit)
        # Roughly estimate 4 characters per token
        max_input_chars = 4000
        if len(text) > max_input_chars:
            text = text[:max_input_chars]
            # Try to cut at sentence boundary
            last_period = text.rfind(".")
            if last_period > max_input_chars * 0.7:
                text = text[:last_period + 1]
        
        # Generate summary
        result = summarizer(
            text,
            max_length=max_length,
            min_length=min_length,
            do_sample=False,
            truncation=True
        )
        
        if result and len(result) > 0:
            return result[0]["summary_text"]
        
        return None
        
    except Exception as e:
        logger.error(f"Summarization failed: {e}")
        return None


def get_key_sentences(text: str, num_sentences: int = 3) -> str:
    """
    Fallback method: Extract key sentences from the beginning of the article.
    Used when ML summarization is unavailable.
    
    Args:
        text: The article text.
        num_sentences: Number of sentences to extract.
        
    Returns:
        First few sentences of the article.
    """
    if not text:
        return ""
    
    sentences = []
    current = ""
    
    for char in text:
        current += char
        if char in ".!?" and len(current.strip()) > 20:
            sentences.append(current.strip())
            current = ""
            if len(sentences) >= num_sentences:
                break
    
    return " ".join(sentences)
