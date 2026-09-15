// =============================================================================
// PhishGuard AI - Browser Extension Background Service Worker (Manifest v3)
// Real-time tab monitoring and background multi-model API classification
// =============================================================================

const API_BASE_URL = "http://127.0.0.1:5000/api/scan";

// Listen for tab navigation completion
chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
    if (changeInfo.status === 'complete' && tab.url && /^https?:\/\//i.test(tab.url)) {
        // Skip local server and chrome extension internal pages
        if (tab.url.includes("127.0.0.1") || tab.url.includes("localhost") || tab.url.startsWith("chrome://")) {
            return;
        }
        analyzeTabUrl(tabId, tab.url);
    }
});

async function analyzeTabUrl(tabId, url) {
    try {
        const response = await fetch(`${API_BASE_URL}?url=${encodeURIComponent(url)}&source=Extension`);
        if (!response.ok) return;

        const data = await response.json();

        // Save scan result in storage mapped by tab URL
        chrome.storage.local.set({ [url]: data });

        // Send pop verification message to content script in active tab
        chrome.tabs.sendMessage(tabId, {
            action: "PHISHGUARD_VERDICT_POPUP",
            data: data
        }).catch(err => {
            // Content script may not be ready or injected
        });
    } catch (err) {
        console.log("[PhishGuard Extension Error]", err);
    }
}

// Handle popup menu requests for tab status
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === "GET_CURRENT_TAB_STATUS") {
        chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
            if (tabs && tabs[0] && tabs[0].url) {
                const url = tabs[0].url;
                chrome.storage.local.get([url], (res) => {
                    sendResponse({ data: res[url] || null, url: url });
                });
            } else {
                sendResponse({ data: null, url: "" });
            }
        });
        return true; // Async response
    }
});
