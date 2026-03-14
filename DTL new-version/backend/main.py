"""
Fake News Credibility Analyzer - Backend API
FastAPI server providing article analysis endpoints.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl
from typing import Optional
import logging

from extractor import extract_article
from summarizer import summarize_text, get_key_sentences
from credibility import calculate_credibility

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Fake News Credibility Analyzer",
    description="API for analyzing news article credibility",
    version="1.0.0"
)

# Enable CORS for browser extension
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for extension
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class AnalyzeRequest(BaseModel):
    """Request model for article analysis."""
    url: str
    skip_corroboration: Optional[bool] = False


class AnalyzeResponse(BaseModel):
    """Response model for article analysis."""
    # Article info
    title: str
    summary: str
    url: str
    authors: list[str]
    
    # Credibility results
    credibility_score: int
    credibility_label: str
    label_color: str
    
    # Score breakdown
    source_score: int
    source_category: str
    sensationalism_penalty: int
    corroboration_bonus: int
    corroborated_sources: list[str]
    
    # Detailed explanation
    explanation: str
    
    # Sensationalism details
    sensationalism_details: dict
    
    # Success indicator
    success: bool
    error: Optional[str] = None


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "running",
        "service": "Fake News Credibility Analyzer",
        "version": "1.0.0"
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze_article(request: AnalyzeRequest):
    """
    Analyze an article for credibility.
    
    Takes a URL and returns:
    - Article title and summary
    - Credibility score (0-100) and label
    - Score breakdown (source, sensationalism, corroboration)
    - Human-readable explanation
    """
    logger.info(f"Analyzing article: {request.url}")
    
    try:
        # 1. Extract article content
        article = extract_article(request.url)
        
        if not article.success:
            logger.error(f"Extraction failed: {article.error}")
            raise HTTPException(
                status_code=400,
                detail=f"Failed to extract article: {article.error}"
            )
        
        logger.info(f"Extracted article: {article.title}")
        
        # 2. Generate summary
        summary = summarize_text(article.text)
        if not summary:
            # Fallback to key sentences
            summary = get_key_sentences(article.text, num_sentences=3)
            logger.info("Using fallback summary (key sentences)")
        
        logger.info(f"Generated summary: {summary[:100]}...")
        
        # 3. Calculate credibility
        credibility = calculate_credibility(
            url=request.url,
            title=article.title,
            text=article.text,
            summary=summary,
            skip_corroboration=request.skip_corroboration or False
        )
        
        logger.info(f"Credibility score: {credibility['credibility_score']} ({credibility['credibility_label']})")
        
        # 4. Build response
        return AnalyzeResponse(
            title=article.title,
            summary=summary,
            url=request.url,
            authors=article.authors,
            
            credibility_score=credibility["credibility_score"],
            credibility_label=credibility["credibility_label"],
            label_color=credibility["label_color"],
            
            source_score=credibility["source_score"],
            source_category=credibility["source_category"],
            sensationalism_penalty=credibility["sensationalism_penalty"],
            corroboration_bonus=credibility["corroboration_bonus"],
            corroborated_sources=credibility["corroboration_details"]["corroborated_sources"],
            
            explanation=credibility["explanation"],
            sensationalism_details=credibility["sensationalism_details"],
            
            success=True
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Analysis failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed: {str(e)}"
        )


@app.post("/analyze/quick")
async def analyze_quick(request: AnalyzeRequest):
    """
    Quick analysis without corroboration check.
    Faster but less comprehensive.
    """
    request.skip_corroboration = True
    return await analyze_article(request)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
