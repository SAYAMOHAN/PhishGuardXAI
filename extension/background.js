// =============================================================================
// PhishGuard AI - Browser Extension Background Service Worker (Manifest v3)
// Real-time tab monitoring and background multi-model API classification
// =============================================================================

const API_BASE_URL = "http://127.0.0.1:5000/api/scan";

// 1. Listen for tab updates (navigation complete)
chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
    if (changeInfo.status === 'complete' && tab.url && /^https?:\/\//i.test(tab.url)) {
        if (shouldSkipUrl(tab.url)) return;
        analyzeTabUrl(tabId, tab.url);
    }
});

// 2. Listen for webNavigation completions (backup listener)
if (chrome.webNavigation) {
    chrome.webNavigation.onCompleted.addListener((details) => {
        if (details.frameId === 0 && details.url && /^https?:\/\//i.test(details.url)) {
            if (shouldSkipUrl(details.url)) return;
            analyzeTabUrl(details.tabId, details.url);
        }
    });
}

function shouldSkipUrl(url) {
    return url.includes("127.0.0.1") || 
           url.includes("localhost") || 
           url.startsWith("chrome://") || 
           url.startsWith("chrome-extension://") ||
           url.startsWith("edge://") ||
           url.startsWith("about:");
}

async function analyzeTabUrl(tabId, url) {
    try {
        const response = await fetch(`${API_BASE_URL}?url=${encodeURIComponent(url)}&source=Extension`);
        if (!response.ok) return;

        const data = await response.json();

        // Save scan result in Chrome storage mapped by tab URL
        chrome.storage.local.set({ [url]: data });

        // Update Extension Badge on Toolbar Icon
        const decision = (data.decision || "SAFE").toUpperCase();
        if (decision === "PHISHING" || decision === "HIGH_RISK") {
            chrome.action.setBadgeBackgroundColor({ tabId: tabId, color: "#FF4B4B" });
            chrome.action.setBadgeText({ tabId: tabId, text: "⚠️" });
        } else if (decision === "SUSPICIOUS") {
            chrome.action.setBadgeBackgroundColor({ tabId: tabId, color: "#FBBF24" });
            chrome.action.setBadgeText({ tabId: tabId, text: "!" });
        } else {
            chrome.action.setBadgeBackgroundColor({ tabId: tabId, color: "#00E699" });
            chrome.action.setBadgeText({ tabId: tabId, text: "✓" });
        }

        // Send verdict message to content script in tab
        sendVerdictToTab(tabId, data);

    } catch (err) {
        console.log("[PhishGuard Background Error]", err);
    }
}

function sendVerdictToTab(tabId, data) {
    chrome.tabs.sendMessage(tabId, {
        action: "PHISHGUARD_VERDICT_POPUP",
        data: data
    }).catch(() => {
        // Content script may not be injected yet. Dynamically inject and retry.
        if (chrome.scripting) {
            chrome.scripting.executeScript({
                target: { tabId: tabId },
                files: ["content.js"]
            }).then(() => {
                setTimeout(() => {
                    chrome.tabs.sendMessage(tabId, {
                        action: "PHISHGUARD_VERDICT_POPUP",
                        data: data
                    }).catch(e => console.log("[PhishGuard Inject Error]", e));
                }, 100);
            }).catch(e => console.log("[PhishGuard Scripting Error]", e));
        }
    });
}

// 3. Handle popup toolbar menu queries
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
