/**
 * Fake News Credibility Analyzer - Content Script
 * Extracts current page URL and article content.
 * Runs on all pages to provide article information to the popup.
 */

// Listen for messages from the popup
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === 'getUrl') {
        sendResponse({ url: window.location.href });
    }

    if (request.action === 'getArticleInfo') {
        // Try to extract article metadata
        const articleInfo = extractArticleInfo();
        sendResponse(articleInfo);
    }

    return true; // Keep message channel open for async response
});

/**
 * Extract article information from the page.
 */
function extractArticleInfo() {
    const info = {
        url: window.location.href,
        title: '',
        description: '',
    };

    // Try to get title from various sources
    info.title =
        document.querySelector('meta[property="og:title"]')?.content ||
        document.querySelector('meta[name="twitter:title"]')?.content ||
        document.querySelector('h1')?.textContent?.trim() ||
        document.title;

    // Try to get description
    info.description =
        document.querySelector('meta[property="og:description"]')?.content ||
        document.querySelector('meta[name="description"]')?.content ||
        document.querySelector('meta[name="twitter:description"]')?.content ||
        '';

    return info;
}

// Log that content script is loaded (for debugging)
console.log('Credibility Analyzer content script loaded');
