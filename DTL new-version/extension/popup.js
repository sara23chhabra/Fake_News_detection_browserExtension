/**
 * Fake News Credibility Analyzer - Popup Script
 * Handles UI logic and API communication with the backend.
 */

// Backend API URL
const API_URL = 'http://localhost:8000';

// DOM Elements
const loadingEl = document.getElementById('loading');
const errorEl = document.getElementById('error');
const notArticleEl = document.getElementById('not-article');
const resultsEl = document.getElementById('results');
const retryBtn = document.getElementById('retry-btn');
const errorMessageEl = document.getElementById('error-message');

// Results elements
const scoreValueEl = document.getElementById('score-value');
const scoreCircleEl = document.getElementById('score-circle');
const scoreLabelEl = document.getElementById('score-label');
const articleTitleEl = document.getElementById('article-title');
const summaryTextEl = document.getElementById('summary-text');
const sourceScoreEl = document.getElementById('source-score');
const sourceDetailEl = document.getElementById('source-detail');
const sensationalismPenaltyEl = document.getElementById('sensationalism-penalty');
const sensationalismDetailEl = document.getElementById('sensationalism-detail');
const corroborationBonusEl = document.getElementById('corroboration-bonus');
const corroborationDetailEl = document.getElementById('corroboration-detail');
const explanationTextEl = document.getElementById('explanation-text');

/**
 * Show a specific state and hide others.
 */
function showState(state) {
    loadingEl.classList.add('hidden');
    errorEl.classList.add('hidden');
    notArticleEl.classList.add('hidden');
    resultsEl.classList.add('hidden');

    switch (state) {
        case 'loading':
            loadingEl.classList.remove('hidden');
            break;
        case 'error':
            errorEl.classList.remove('hidden');
            break;
        case 'not-article':
            notArticleEl.classList.remove('hidden');
            break;
        case 'results':
            resultsEl.classList.remove('hidden');
            break;
    }
}

/**
 * Check if URL looks like a news article.
 */
function isNewsArticle(url) {
    // Skip common non-article pages
    const skipPatterns = [
        'chrome://',
        'chrome-extension://',
        'edge://',
        'about:',
        'file://',
        'localhost',
        'google.com/search',
        'bing.com/search',
        'duckduckgo.com',
        'facebook.com',
        'twitter.com',
        'instagram.com',
        'youtube.com',
        'amazon.com',
        'wikipedia.org',
    ];

    const urlLower = url.toLowerCase();
    for (const pattern of skipPatterns) {
        if (urlLower.includes(pattern)) {
            return false;
        }
    }

    return true;
}

/**
 * Get the current tab URL.
 */
async function getCurrentTabUrl() {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    return tab?.url || null;
}

/**
 * Analyze an article by URL.
 */
async function analyzeArticle(url) {
    const response = await fetch(`${API_URL}/analyze`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ url }),
    });

    if (!response.ok) {
        const error = await response.json().catch(() => ({}));
        throw new Error(error.detail || 'Failed to analyze article');
    }

    return response.json();
}

/**
 * Display analysis results.
 */
function displayResults(data) {
    // Score
    scoreValueEl.textContent = data.credibility_score;

    // Apply score color to circle
    const scoreColor = data.label_color || getScoreColor(data.credibility_score);
    scoreCircleEl.style.setProperty('--score-color', scoreColor);
    scoreValueEl.style.color = scoreColor;

    // Label
    scoreLabelEl.textContent = `${data.credibility_label} Credibility`;
    scoreLabelEl.className = 'score-label ' + data.credibility_label.toLowerCase();

    // Article title
    articleTitleEl.textContent = data.title || 'Untitled';

    // Summary
    summaryTextEl.textContent = data.summary || 'No summary available.';

    // Source score
    sourceScoreEl.textContent = `+${data.source_score}`;
    sourceDetailEl.textContent = `${data.source_category} source`;

    // Sensationalism penalty
    const penalty = data.sensationalism_penalty || 0;
    sensationalismPenaltyEl.textContent = penalty > 0 ? `-${penalty}` : '0';
    sensationalismPenaltyEl.className = 'breakdown-value ' + (penalty > 0 ? 'negative' : 'neutral');

    // Sensationalism detail
    const sensDetails = data.sensationalism_details || {};
    if (penalty > 0) {
        const issues = [];
        if (sensDetails.clickbait_phrases?.length > 0) {
            issues.push(`clickbait phrases`);
        }
        if (sensDetails.sensational_words?.length > 0) {
            issues.push(`sensational language`);
        }
        if (sensDetails.caps_penalty > 0) {
            issues.push(`excessive caps`);
        }
        if (sensDetails.punctuation_penalty > 0) {
            issues.push(`punctuation abuse`);
        }
        sensationalismDetailEl.textContent = issues.length > 0
            ? `Detected: ${issues.join(', ')}`
            : 'Issues detected';
    } else {
        sensationalismDetailEl.textContent = 'No sensationalism detected';
    }

    // Corroboration bonus
    const bonus = data.corroboration_bonus || 0;
    corroborationBonusEl.textContent = bonus > 0 ? `+${bonus}` : '0';
    corroborationBonusEl.className = 'breakdown-value ' + (bonus > 0 ? 'positive' : 'neutral');

    // Corroboration detail
    const sources = data.corroborated_sources || [];
    if (sources.length > 0) {
        corroborationDetailEl.textContent = `Verified by: ${sources.slice(0, 3).join(', ')}`;
    } else {
        corroborationDetailEl.textContent = 'No independent verification found';
    }

    // Explanation
    explanationTextEl.textContent = data.explanation || 'Analysis complete.';

    showState('results');
}

/**
 * Get color based on score.
 */
function getScoreColor(score) {
    if (score >= 75) return '#22c55e'; // Green
    if (score >= 50) return '#f59e0b'; // Amber
    return '#ef4444'; // Red
}

/**
 * Main initialization.
 */
async function init() {
    showState('loading');

    try {
        const url = await getCurrentTabUrl();

        if (!url) {
            showState('not-article');
            return;
        }

        if (!isNewsArticle(url)) {
            showState('not-article');
            return;
        }

        const result = await analyzeArticle(url);
        displayResults(result);

    } catch (error) {
        console.error('Analysis failed:', error);
        errorMessageEl.textContent = error.message || 'Failed to analyze article. Is the backend running?';
        showState('error');
    }
}

// Event listeners
retryBtn.addEventListener('click', init);

// Initialize on popup open
document.addEventListener('DOMContentLoaded', init);
