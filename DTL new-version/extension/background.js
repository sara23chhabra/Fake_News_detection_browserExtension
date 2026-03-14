/**
 * Fake News Credibility Analyzer - Background Service Worker
 * Handles message passing and extension lifecycle for Manifest V3.
 */

// Log when service worker starts
console.log('Credibility Analyzer background service worker started');

// Listen for installation
chrome.runtime.onInstalled.addListener((details) => {
    if (details.reason === 'install') {
        console.log('Extension installed');
    } else if (details.reason === 'update') {
        console.log('Extension updated');
    }
});

// Handle messages from popup or content scripts
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === 'checkBackend') {
        // Check if backend is running
        fetch('http://localhost:8000/health')
            .then(response => response.json())
            .then(data => sendResponse({ available: true, data }))
            .catch(error => sendResponse({ available: false, error: error.message }));

        return true; // Keep channel open for async response
    }

    if (request.action === 'analyzeUrl') {
        // Forward analysis request to backend
        fetch('http://localhost:8000/analyze', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ url: request.url }),
        })
            .then(response => {
                if (!response.ok) throw new Error('Analysis failed');
                return response.json();
            })
            .then(data => sendResponse({ success: true, data }))
            .catch(error => sendResponse({ success: false, error: error.message }));

        return true; // Keep channel open for async response
    }
});

// Keep service worker alive (Manifest V3)
chrome.runtime.onConnect.addListener((port) => {
    console.log('Connection established:', port.name);
});
