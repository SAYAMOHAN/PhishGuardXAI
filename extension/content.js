// =============================================================================
// PhishGuard AI - Content Script (Real-Time In-Browser Popup Verification)
// Injects sleek dark cyber security alerts directly onto visited web pages
// =============================================================================

(function () {
    if (window.phishGuardInjected) return;
    window.phishGuardInjected = true;

    chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
        if (request.action === "PHISHGUARD_VERDICT_POPUP" && request.data) {
            renderSecurityPopup(request.data);
        }
    });

    function renderSecurityPopup(data) {
        // Remove existing popup if any
        const existing = document.getElementById("phishguard-alert-banner");
        if (existing) existing.remove();

        const decision = data.decision || {};
        const level = (decision.level || "SAFE").toUpperCase();
        const riskScore = decision.risk_score || 0;
        const colorClass = level.replace(/\s+/g, '-').toLowerCase();

        // Create alert container
        const banner = document.createElement("div");
        banner.id = "phishguard-alert-banner";
        banner.className = `phishguard-popup ${colorClass}`;

        const isThreat = level === "PHISHING" || level === "HIGH RISK" || level === "SUSPICIOUS";
        const badgeIcon = level === "PHISHING" ? "⛔" : level === "HIGH RISK" ? "🚨" : level === "SUSPICIOUS" ? "⚠️" : "🛡️";

        banner.innerHTML = `
            <style>
                #phishguard-alert-banner {
                    position: fixed;
                    top: 20px;
                    right: 20px;
                    z-index: 2147483647;
                    width: 360px;
                    background: rgba(10, 15, 26, 0.95);
                    backdrop-filter: blur(16px);
                    -webkit-backdrop-filter: blur(16px);
                    border: 1px solid rgba(255, 255, 255, 0.15);
                    border-radius: 14px;
                    padding: 16px 20px;
                    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.6), 0 0 20px rgba(0, 242, 254, 0.15);
                    font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
                    color: #f8fafc;
                    animation: pgSlideIn 0.4s cubic-bezier(0.16, 1, 0.3, 1);
                }
                #phishguard-alert-banner.phishing, #phishguard-alert-banner.high-risk {
                    border-color: rgba(255, 75, 75, 0.6);
                    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.7), 0 0 25px rgba(255, 75, 75, 0.3);
                }
                #phishguard-alert-banner.suspicious {
                    border-color: rgba(251, 191, 36, 0.6);
                    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.7), 0 0 25px rgba(251, 191, 36, 0.3);
                }
                #phishguard-alert-banner.safe {
                    border-color: rgba(0, 230, 153, 0.5);
                    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.7), 0 0 20px rgba(0, 230, 153, 0.2);
                }
                @keyframes pgSlideIn {
                    from { transform: translateY(-30px) scale(0.95); opacity: 0; }
                    to { transform: translateY(0) scale(1); opacity: 1; }
                }
                .pg-header {
                    display: flex;
                    align-items: center;
                    justify-content: space-between;
                    margin-bottom: 12px;
                }
                .pg-badge {
                    display: flex;
                    align-items: center;
                    gap: 8px;
                    font-weight: 700;
                    font-size: 13px;
                    letter-spacing: 0.5px;
                    text-transform: uppercase;
                    padding: 5px 12px;
                    border-radius: 20px;
                }
                .phishing .pg-badge, .high-risk .pg-badge { background: rgba(255, 75, 75, 0.2); color: #ff4b4b; border: 1px solid rgba(255, 75, 75, 0.4); }
                .suspicious .pg-badge { background: rgba(251, 191, 36, 0.2); color: #fbbf24; border: 1px solid rgba(251, 191, 36, 0.4); }
                .safe .pg-badge { background: rgba(0, 230, 153, 0.2); color: #00e699; border: 1px solid rgba(0, 230, 153, 0.4); }
                .pg-close {
                    background: none;
                    border: none;
                    color: #94a3b8;
                    font-size: 18px;
                    cursor: pointer;
                    line-height: 1;
                    padding: 2px 6px;
                    border-radius: 4px;
                }
                .pg-close:hover { color: #fff; background: rgba(255,255,255,0.1); }
                .pg-title {
                    font-size: 15px;
                    font-weight: 600;
                    margin-bottom: 6px;
                    color: #f1f5f9;
                }
                .pg-meta {
                    font-size: 12px;
                    color: #94a3b8;
                    margin-bottom: 12px;
                    line-height: 1.4;
                }
                .pg-scores {
                    display: grid;
                    grid-template-columns: repeat(3, 1fr);
                    gap: 6px;
                    margin-bottom: 12px;
                    background: rgba(15, 23, 42, 0.6);
                    padding: 8px;
                    border-radius: 8px;
                    text-align: center;
                }
                .pg-score-box label { font-size: 10px; color: #64748b; display: block; text-transform: uppercase; }
                .pg-score-box span { font-size: 13px; font-weight: 700; color: #00f2fe; }
                .pg-bar-wrap {
                    background: rgba(255,255,255,0.1);
                    height: 6px;
                    border-radius: 3px;
                    overflow: hidden;
                    margin-bottom: 14px;
                }
                .pg-bar-fill {
                    height: 100%;
                    transition: width 0.6s ease;
                }
                .phishing .pg-bar-fill, .high-risk .pg-bar-fill { background: linear-gradient(90deg, #ff4b4b, #ff7b00); }
                .suspicious .pg-bar-fill { background: linear-gradient(90deg, #fbbf24, #f59e0b); }
                .safe .pg-bar-fill { background: linear-gradient(90deg, #00e699, #00f2fe); }
                .pg-actions {
                    display: flex;
                    gap: 8px;
                }
                .pg-btn {
                    flex: 1;
                    padding: 8px 12px;
                    border-radius: 8px;
                    font-size: 12px;
                    font-weight: 600;
                    cursor: pointer;
                    border: none;
                    text-align: center;
                    transition: all 0.2s;
                }
                .pg-btn-danger {
                    background: linear-gradient(135deg, #ff4b4b, #d97706);
                    color: #fff;
                    box-shadow: 0 4px 12px rgba(255, 75, 75, 0.3);
                }
                .pg-btn-secondary {
                    background: rgba(255, 255, 255, 0.08);
                    color: #cbd5e1;
                    border: 1px solid rgba(255, 255, 255, 0.12);
                }
                .pg-btn:hover { opacity: 0.9; transform: translateY(-1px); }
            </style>
            <div class="pg-header">
                <div class="pg-badge">${badgeIcon} ${level}</div>
                <button class="pg-close" id="phishguard-close-btn">&times;</button>
            </div>
            <div class="pg-title">PhishGuard AI Detection Result</div>
            <div class="pg-meta">
                ${data.adaptive_risk_assessment ? data.adaptive_risk_assessment.risk_level_explanation : (isThreat ? 'High risk phishing pattern detected by ensemble models.' : 'No active phishing threats detected for this domain.')}
            </div>

            <div class="pg-scores">
                <div class="pg-score-box">
                    <label>BERT</label>
                    <span>${Math.round((data.bert_probability || 0) * 100)}%</span>
                </div>
                <div class="pg-score-box">
                    <label>GNN</label>
                    <span>${Math.round((data.gnn_probability || 0) * 100)}%</span>
                </div>
                <div class="pg-score-box">
                    <label>LightGBM</label>
                    <span>${Math.round((data.lightgbm_probability || 0) * 100)}%</span>
                </div>
            </div>

            <div style="display:flex; justify-content:space-between; font-size:11px; color:#94a3b8; margin-bottom:4px;">
                <span>Adaptive Risk Score</span>
                <span style="font-weight:700; color:#fff;">${riskScore.toFixed(1)}/100</span>
            </div>
            <div class="pg-bar-wrap">
                <div class="pg-bar-fill" style="width: ${Math.min(100, Math.max(5, riskScore))}%;"></div>
            </div>

            <div class="pg-actions">
                ${isThreat ? `<button class="pg-btn pg-btn-danger" id="phishguard-leave-btn">⚠️ Leave Page</button>` : ''}
                <button class="pg-btn pg-btn-secondary" id="phishguard-dismiss-btn">${isThreat ? 'Ignore Warning' : 'Dismiss'}</button>
            </div>
        `;

        document.body.appendChild(banner);

        document.getElementById("phishguard-close-btn").onclick = () => banner.remove();
        document.getElementById("phishguard-dismiss-btn").onclick = () => banner.remove();
        const leaveBtn = document.getElementById("phishguard-leave-btn");
        if (leaveBtn) {
            leaveBtn.onclick = () => {
                window.location.href = "about:blank";
            };
        }

        // Auto fadeout for safe links after 8 seconds
        if (!isThreat) {
            setTimeout(() => {
                if (document.body.contains(banner)) {
                    banner.style.opacity = '0';
                    banner.style.transition = 'opacity 0.5s ease';
                    setTimeout(() => banner.remove(), 500);
                }
            }, 8000);
        }
    }
})();
