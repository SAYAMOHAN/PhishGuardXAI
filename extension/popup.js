// PhishGuard AI Extension Toolbar Popup Logic

document.addEventListener("DOMContentLoaded", () => {
    const currentUrlEl = document.getElementById("current-url");
    const verdictCard = document.getElementById("verdict-card");
    const verdictBadge = document.getElementById("verdict-badge");
    const verdictTitle = document.getElementById("verdict-title");
    const verdictSub = document.getElementById("verdict-sub");
    
    const scoreBert = document.getElementById("score-bert");
    const scoreGnn = document.getElementById("score-gnn");
    const scoreLgb = document.getElementById("score-lgb");
    
    const riskScoreVal = document.getElementById("risk-score-val");
    const riskBarFill = document.getElementById("risk-bar-fill");
    const mdiVal = document.getElementById("mdi-val");

    const btnRecheck = document.getElementById("btn-recheck");
    const btnDashboard = document.getElementById("btn-dashboard");

    // Request active tab status from background service worker
    loadTabStatus();

    btnRecheck.addEventListener("click", () => {
        verdictTitle.textContent = "Scanning URL...";
        verdictSub.textContent = "Querying BERT + GNN + LightGBM models";
        loadTabStatus(true);
    });

    btnDashboard.addEventListener("click", () => {
        chrome.tabs.create({ url: "http://127.0.0.1:5000" });
    });

    function loadTabStatus(forceRescan = false) {
        chrome.runtime.sendMessage({ action: "GET_CURRENT_TAB_STATUS" }, (response) => {
            if (!response || !response.url) {
                currentUrlEl.textContent = "No active URL target";
                verdictTitle.textContent = "Inactive Browser Tab";
                return;
            }

            const currentUrl = response.url;
            currentUrlEl.textContent = currentUrl;

            if (response.data && !forceRescan) {
                renderVerdict(response.data);
            } else {
                // Fetch directly from backend API
                fetch(`http://127.0.0.1:5000/api/scan?url=${encodeURIComponent(currentUrl)}&source=Extension`)
                    .then(res => res.json())
                    .then(data => {
                        // Store in storage
                        chrome.storage.local.set({ [currentUrl]: data });
                        renderVerdict(data);
                    })
                    .catch(err => {
                        verdictTitle.textContent = "Backend Offline";
                        verdictSub.textContent = "Start Flask backend server at http://127.0.0.1:5000";
                    });
            }
        });
    }

    function renderVerdict(data) {
        const decision = data.decision || {};
        const level = (decision.level || "SAFE").toUpperCase();
        const score = decision.risk_score || 0;
        const colorClass = level.replace(/\s+/g, '-').toLowerCase();

        verdictCard.className = `verdict-card ${colorClass}`;
        
        const badgeIcon = level === "PHISHING" ? "⛔" : level === "HIGH RISK" ? "🚨" : level === "SUSPICIOUS" ? "⚠️" : "🛡️";
        verdictBadge.textContent = `${badgeIcon} ${level}`;
        verdictTitle.textContent = decision.title || `${level} Web Domain`;
        verdictSub.textContent = data.adaptive_risk_assessment ? data.adaptive_risk_assessment.risk_level_explanation : (decision.recommendation || "Evaluation complete.");

        scoreBert.textContent = `${Math.round((data.bert_probability || 0) * 100)}%`;
        scoreGnn.textContent = `${Math.round((data.gnn_probability || 0) * 100)}%`;
        scoreLgb.textContent = `${Math.round((data.lightgbm_probability || 0) * 100)}%`;

        riskScoreVal.textContent = `${score.toFixed(1)} / 100`;
        riskBarFill.style.width = `${Math.min(100, Math.max(5, score))}%`;
        
        if (data.model_disagreement) {
            mdiVal.textContent = data.model_disagreement.mdi_score.toFixed(3);
        }
    }
});
