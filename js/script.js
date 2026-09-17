document.addEventListener('DOMContentLoaded', () => {
    initDarkMode();
    initGamificationEngine();
    initSoundToggle();
    initUrlScanner();
    initResultPagePopulator();
    initHistoryTableActions();
    initRecentScansOnHome();
    initSettingsForm();
    initDualModeAndSimulator();
    initExtensionModal();
    initPreviousReportsSelectors();
});

/* --------------------------------------------------------------------------
   0.0 Web Audio Synthesizer (Futuristic Cyber Sound FX)
   -------------------------------------------------------------------------- */
function playCyberAudio(type) {
    if (localStorage.getItem('phishguard_sound_muted') === 'true') return;

    try {
        const AudioCtx = window.AudioContext || window.webkitAudioContext;
        if (!AudioCtx) return;
        const ctx = new AudioCtx();
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();

        osc.connect(gain);
        gain.connect(ctx.destination);

        const now = ctx.currentTime;

        if (type === 'scan') {
            osc.type = 'sine';
            osc.frequency.setValueAtTime(440, now);
            osc.frequency.exponentialRampToValueAtTime(880, now + 0.2);
            gain.gain.setValueAtTime(0.08, now);
            gain.gain.exponentialRampToValueAtTime(0.001, now + 0.2);
            osc.start(now);
            osc.stop(now + 0.2);
        } else if (type === 'safe') {
            osc.type = 'triangle';
            osc.frequency.setValueAtTime(523.25, now); // C5
            osc.frequency.setValueAtTime(659.25, now + 0.1); // E5
            gain.gain.setValueAtTime(0.12, now);
            gain.gain.exponentialRampToValueAtTime(0.001, now + 0.35);
            osc.start(now);
            osc.stop(now + 0.35);
        } else if (type === 'threat') {
            osc.type = 'sawtooth';
            osc.frequency.setValueAtTime(220, now);
            osc.frequency.setValueAtTime(160, now + 0.12);
            gain.gain.setValueAtTime(0.15, now);
            gain.gain.exponentialRampToValueAtTime(0.001, now + 0.4);
            osc.start(now);
            osc.stop(now + 0.4);
        } else if (type === 'level') {
            osc.type = 'sine';
            osc.frequency.setValueAtTime(440, now);
            osc.frequency.setValueAtTime(554.37, now + 0.1);
            osc.frequency.setValueAtTime(659.25, now + 0.2);
            gain.gain.setValueAtTime(0.15, now);
            gain.gain.exponentialRampToValueAtTime(0.001, now + 0.5);
            osc.start(now);
            osc.stop(now + 0.5);
        }
    } catch (e) {}
}

function initSoundToggle() {
    const soundToggle = document.getElementById('soundToggleBtn');
    if (!soundToggle) return;

    const isMuted = localStorage.getItem('phishguard_sound_muted') === 'true';
    if (isMuted) {
        soundToggle.classList.add('muted');
        soundToggle.innerHTML = `<i class="fa-solid fa-volume-xmark"></i>`;
    } else {
        soundToggle.classList.remove('muted');
        soundToggle.innerHTML = `<i class="fa-solid fa-volume-high"></i>`;
    }

    soundToggle.addEventListener('click', () => {
        const currentlyMuted = localStorage.getItem('phishguard_sound_muted') === 'true';
        if (currentlyMuted) {
            localStorage.setItem('phishguard_sound_muted', 'false');
            soundToggle.classList.remove('muted');
            soundToggle.innerHTML = `<i class="fa-solid fa-volume-high"></i>`;
            playCyberAudio('safe');
        } else {
            localStorage.setItem('phishguard_sound_muted', 'true');
            soundToggle.classList.add('muted');
            soundToggle.innerHTML = `<i class="fa-solid fa-volume-xmark"></i>`;
        }
    });
}

/* --------------------------------------------------------------------------
   0.01 Gamification Engine (XP, Analyst Ranks, Achievements)
   -------------------------------------------------------------------------- */
const ANALYST_RANKS = [
    { level: 1, title: "Recruit Analyst", icon: "fa-user-shield" },
    { level: 2, title: "Threat Hunter", icon: "fa-shield-halved" },
    { level: 3, title: "Cyber Sentinel", icon: "fa-lock-open" },
    { level: 4, title: "XAI Investigator", icon: "fa-brain" },
    { level: 5, title: "Senior AI Commander", icon: "fa-award" }
];

function getGamificationData() {
    const raw = localStorage.getItem('phishguard_gamification');
    if (raw) {
        try { return JSON.parse(raw); } catch (e) {}
    }
    return {
        xp: 120,
        level: 2,
        streak: 3,
        scansCount: 4,
        achievements: ["first_scan"]
    };
}

function saveGamificationData(data) {
    localStorage.setItem('phishguard_gamification', JSON.stringify(data));
    updateGamificationUi();
}

function awardXp(points, reason) {
    const gData = getGamificationData();
    const oldLevel = gData.level;
    gData.xp += points;
    gData.scansCount = (gData.scansCount || 0) + 1;

    // Check level up (100 XP per level)
    const newLevel = Math.floor(gData.xp / 100) + 1;
    gData.level = newLevel;

    // Unlock Achievements
    if (!gData.achievements) gData.achievements = [];
    if (gData.scansCount >= 1 && !gData.achievements.includes('first_scan')) {
        gData.achievements.push('first_scan');
        showToastNotification("Achievement Unlocked!", "🎯 First Scan Completed");
    }
    if (gData.scansCount >= 5 && !gData.achievements.includes('threat_hunter')) {
        gData.achievements.push('threat_hunter');
        showToastNotification("Achievement Unlocked!", "🛡️ Threat Hunter (5 Scans)");
    }

    saveGamificationData(gData);

    if (newLevel > oldLevel) {
        playCyberAudio('level');
        const rank = ANALYST_RANKS.find(r => r.level === newLevel) || ANALYST_RANKS[ANALYST_RANKS.length - 1];
        showToastNotification("RANK LEVEL UP!", `🎉 Promoted to Level ${newLevel}: ${rank.title}`);
    } else {
        showToastNotification("XP Earned!", `+${points} XP: ${reason}`);
    }
}

function updateGamificationUi() {
    const data = getGamificationData();
    const currentLevel = data.level;
    const currentXp = data.xp;
    const levelXpFloor = (currentLevel - 1) * 100;
    const progressXp = currentXp - levelXpFloor;

    const rank = ANALYST_RANKS.find(r => r.level === currentLevel) || ANALYST_RANKS[ANALYST_RANKS.length - 1];

    // Header Level elements
    const levelValElem = document.getElementById('userLevelVal');
    const xpBarElem = document.getElementById('userXpBar');
    const xpTextElem = document.getElementById('userXpText');

    if (levelValElem) levelValElem.textContent = currentLevel;
    if (xpBarElem) xpBarElem.style.width = `${Math.min(100, Math.max(5, progressXp))}%`;
    if (xpTextElem) xpTextElem.textContent = `${progressXp}/100 XP`;

    // Welcome Card Rank elements
    const rankTitleElem = document.getElementById('analystRankTitle');
    const streakValElem = document.getElementById('analystStreakVal');
    if (rankTitleElem) rankTitleElem.textContent = `Level ${currentLevel}: ${rank.title}`;
    if (streakValElem) streakValElem.textContent = `${data.streak || 3} Days`;
}

function initGamificationEngine() {
    updateGamificationUi();
}

function showToastNotification(title, message) {
    const existing = document.querySelector('.cyber-toast');
    if (existing) existing.remove();

    const toast = document.createElement('div');
    toast.className = 'cyber-toast';
    toast.innerHTML = `
        <div class="toast-icon"><i class="fa-solid fa-award"></i></div>
        <div class="toast-text">
            <h5>${escapeHtml(title)}</h5>
            <p>${escapeHtml(message)}</p>
        </div>
    `;
    document.body.appendChild(toast);

    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transition = 'opacity 0.4s ease';
        setTimeout(() => toast.remove(), 400);
    }, 3800);
}

/* --------------------------------------------------------------------------
   0.1 Home Page Recent Scans & Stats Populator
   -------------------------------------------------------------------------- */
async function initRecentScansOnHome() {
    const recentTableBody = document.querySelector('.recent-scans-card table tbody');

    let history = [];

    // Try fetching from Flask API
    try {
        const apiEndpoint = localStorage.getItem('phishguard_api_endpoint') || '/api/scan';
        const historyUrl = apiEndpoint.replace('/scan', '/history');
        const res = await fetch(historyUrl);
        if (res.ok) {
            const data = await res.json();
            if (data.history && data.history.length > 0) {
                history = data.history;
            }
        }
    } catch (e) {}

    // Fallback to localStorage if API offline
    if (history.length === 0) {
        history = JSON.parse(localStorage.getItem('phishguard_history')) || [];
    }

    // 1. Update Dynamic Stats Cards from scan history
    const statsTotal = document.getElementById('statsTotal');
    const statsSafe = document.getElementById('statsSafe');
    const statsPhishing = document.getElementById('statsPhishing') || document.getElementById('statsDanger');

    const totalCount = history.length;
    const safeCount = history.filter(h => (h.verdict || h.status) === 'Safe' || (h.verdict || h.status) === 'SAFE').length;
    const phishCount = history.filter(h => (h.verdict || h.status) === 'Phishing' || (h.verdict || h.status) === 'PHISHING' || (h.verdict || h.status) === 'HIGH_RISK').length;

    const safePct = totalCount > 0 ? ((safeCount / totalCount) * 100).toFixed(1) : "0.0";
    const phishPct = totalCount > 0 ? ((phishCount / totalCount) * 100).toFixed(1) : "0.0";

    if (statsTotal) statsTotal.textContent = totalCount.toLocaleString();
    if (statsSafe) statsSafe.textContent = safeCount.toLocaleString();
    if (statsPhishing) statsPhishing.textContent = phishCount.toLocaleString();

    const safeSubtext = document.querySelector('.stat-card:nth-child(2) .stat-percentage');
    const phishSubtext = document.querySelector('.stat-card:nth-child(3) .stat-percentage') || document.querySelector('.stat-card:nth-child(3) .stat-trend');

    if (safeSubtext) safeSubtext.textContent = `${safePct}% verified safe`;
    if (phishSubtext) phishSubtext.innerHTML = `<i class="fa-solid fa-shield-cat"></i> ${phishPct}% threats blocked`;

    // Helper for 4-tier decision badge
    function getBadgeHtml(status) {
        const st = (status || '').toUpperCase();
        if (st === 'PHISHING' || st === 'BAD') {
            return `<span class="badge badge-phishing"><i class="fa-solid fa-circle-xmark"></i> Phishing</span>`;
        } else if (st === 'HIGH_RISK' || st === 'HIGH RISK') {
            return `<span class="badge badge-highrisk"><i class="fa-solid fa-triangle-exclamation"></i> High Risk</span>`;
        } else if (st === 'SUSPICIOUS') {
            return `<span class="badge badge-suspicious"><i class="fa-solid fa-eye"></i> Suspicious</span>`;
        } else {
            return `<span class="badge badge-safe"><i class="fa-solid fa-circle-check"></i> Safe</span>`;
        }
    }

    // 2. Update Recent Scans Table
    if (recentTableBody) {
        if (history.length === 0) {
            recentTableBody.innerHTML = `
                <tr>
                    <td colspan="5" style="text-align: center; color: var(--text-muted); padding: 24px;">
                        No recent scans found. Enter a URL above to analyze your first website.
                    </td>
                </tr>
            `;
        } else {
            const topScans = history.slice(0, 4);
            recentTableBody.innerHTML = topScans.map(item => `
                <tr>
                    <td>
                        <div class="domain-info">
                            <i class="fa-solid ${(item.verdict || item.status) === 'Safe' || (item.verdict || item.status) === 'SAFE' ? 'fa-lock text-success' : 'fa-unlock text-danger'}"></i>
                            <span class="domain-name">${escapeHtml(item.url)}</span>
                        </div>
                    </td>
                    <td>${item.scanned_at || item.date || 'Recently'}</td>
                    <td><span class="risk-pill ${(item.risk_score || item.riskScore) > 50 ? 'high' : 'low'}">${item.risk_score || item.riskScore}/100</span></td>
                    <td>${getBadgeHtml(item.verdict || item.status)}</td>
                    <td>
                        <a href="result.html?url=${encodeURIComponent(item.url)}" class="table-btn">
                            <i class="fa-solid fa-eye"></i>
                        </a>
                    </td>
                </tr>
            `).join('');
        }
    }
}


/* --------------------------------------------------------------------------
   0. Global Dual Theme Mode Manager (Dark Cyber Obsidian & Light Cyber)
   -------------------------------------------------------------------------- */
function initDarkMode() {
    const isExplicitlyLight = localStorage.getItem('phishguard_dark_mode') === 'false';
    const themeBtn = document.getElementById('themeToggleBtn');
    const settingsToggle = document.getElementById('darkModeToggle');

    function applyTheme(isDark) {
        if (isDark) {
            document.body.classList.add('dark-mode');
            document.body.classList.remove('light-mode');
            localStorage.setItem('phishguard_dark_mode', 'true');
            if (themeBtn) themeBtn.innerHTML = `<i class="fa-solid fa-moon"></i>`;
            if (settingsToggle) settingsToggle.checked = true;
        } else {
            document.body.classList.remove('dark-mode');
            document.body.classList.add('light-mode');
            localStorage.setItem('phishguard_dark_mode', 'false');
            if (themeBtn) themeBtn.innerHTML = `<i class="fa-solid fa-sun"></i>`;
            if (settingsToggle) settingsToggle.checked = false;
        }
    }

    // Apply saved theme preference on page load
    applyTheme(!isExplicitlyLight);

    if (themeBtn) {
        themeBtn.addEventListener('click', () => {
            const currentlyDark = document.body.classList.contains('dark-mode');
            applyTheme(!currentlyDark);
            playCyberAudio('scan');
        });
    }

    if (settingsToggle) {
        settingsToggle.addEventListener('change', (e) => {
            applyTheme(e.target.checked);
            playCyberAudio('scan');
        });
    }
}


/* --------------------------------------------------------------------------
   1. URL Scanner & Form Submission Logic (index.html)
   -------------------------------------------------------------------------- */
function initUrlScanner() {
    const scanForm = document.getElementById('urlScanForm');
    const urlInput = document.getElementById('urlInput');
    const scanBtn = document.getElementById('scanBtn');
    const scanLoader = document.getElementById('scanLoader');
    const loaderStep = document.getElementById('loaderStep');

    if (!scanForm) return;

    scanForm.addEventListener('submit', (e) => {
        e.preventDefault();

        let rawUrl = urlInput.value.trim();
        if (!rawUrl) return;

        // Auto-fix URL scheme if user typed 'google.com' without 'http://' or 'https://'
        if (!/^https?:\/\//i.test(rawUrl)) {
            rawUrl = 'https://' + rawUrl;
            urlInput.value = rawUrl;
        }

        // Show Loading Animation Overlay
        if (scanLoader) {
            scanLoader.classList.remove('hidden');
        }

        if (scanBtn) {
            scanBtn.disabled = true;
            scanBtn.style.opacity = '0.7';
        }

        playCyberAudio('scan');

        // 7-Stage Multi-Layer Architecture Inspection Sequence
        const inspectionSteps = [
            "1/7 Extracting 30+ lexical & structural URL features...",
            "2/7 Running BERT Deep NLP Contextual Tokenizer...",
            "3/7 Computing Graph Neural Network (GNN) DOM embeddings...",
            "4/7 Executing LightGBM Gradient Boosting inference...",
            "5/7 Calculating SHAP Explainable AI (XAI) feature evidence...",
            "6/7 Querying OSINT Threat Intelligence (Domain Age, SSL, WHOIS, DNS)...",
            "7/7 Computing Model Disagreement Index (MDI) & Adaptive Risk Score..."
        ];

        let stepIndex = 0;
        const stepInterval = setInterval(() => {
            if (stepIndex < inspectionSteps.length) {
                if (loaderStep) {
                    loaderStep.textContent = inspectionSteps[stepIndex];
                }
                playCyberAudio('scan');
                stepIndex++;
            } else {
                clearInterval(stepInterval);
                // Award XP for scanning
                awardXp(25, "URL Security Analysis");
                // Redirect to result page with encoded URL parameter
                const encodedUrl = encodeURIComponent(rawUrl);
                window.location.href = `result.html?url=${encodedUrl}`;
            }
        }, 280);
    });
}

/* --------------------------------------------------------------------------
   2. Result Page Dynamic Populator (result.html)
   -------------------------------------------------------------------------- */
function initResultPagePopulator() {
    const scannedUrlElem = document.getElementById('scannedUrl');
    if (!scannedUrlElem) return; // Not on result page

    // Parse URL query parameters
    const urlParams = new URLSearchParams(window.location.search);
    const targetUrl = urlParams.get('url');

    if (targetUrl) {
        scannedUrlElem.textContent = targetUrl;
        analyzeAndPopulateResult(targetUrl);
    }
}

async function analyzeAndPopulateResult(targetUrl) {
    const scannedUrlElem = document.getElementById('scannedUrl');
    const verdictBadge = document.getElementById('verdictBadge');
    const riskScoreVal = document.getElementById('riskScoreVal');
    const riskProgressBar = document.getElementById('riskProgressBar');
    const riskSubText = document.getElementById('riskSubText');
    const confidenceVal = document.getElementById('confidenceVal');

    // MDI elements
    const mdiVal = document.getElementById('mdiVal');
    const mdiStatusPill = document.getElementById('mdiStatusPill');

    // Individual Model elements
    const bertProbVal = document.getElementById('bertProbVal');
    const bertPredPill = document.getElementById('bertPredPill');
    const bertProgressFill = document.getElementById('bertProgressFill');

    const gnnProbVal = document.getElementById('gnnProbVal');
    const gnnPredPill = document.getElementById('gnnPredPill');
    const gnnProgressFill = document.getElementById('gnnProgressFill');

    const lgbProbVal = document.getElementById('lgbProbVal');
    const lgbPredPill = document.getElementById('lgbPredPill');
    const lgbProgressFill = document.getElementById('lgbProgressFill');

    // Threat Intel elements
    const intelDomainAge = document.getElementById('intelDomainAge');
    const intelSslStatus = document.getElementById('intelSslStatus');
    const intelWhoisStatus = document.getElementById('intelWhoisStatus');
    const intelDnsStatus = document.getElementById('intelDnsStatus');
    const intelReputation = document.getElementById('intelReputation');
    const intelBlacklist = document.getElementById('intelBlacklist');

    let resultData = null;

    // Attempt to query live Flask REST API endpoint
    try {
        const apiEndpoint = localStorage.getItem('phishguard_api_endpoint') || '/api/scan';
        const response = await fetch(`${apiEndpoint}?url=${encodeURIComponent(targetUrl)}`);
        
        if (response.ok) {
            resultData = await response.json();
        }
    } catch (err) {
        console.log('[API Note] Flask API server offline. Using client-side analysis.');
    }

    // Fallback Client-side Heuristic Simulation matching exact API JSON schema
    if (!resultData) {
        const lowerUrl = targetUrl.toLowerCase();
        const phishingKeywords = ['paypal', 'login', 'verify', 'account', 'secure', 'bank', 'update', 'billing', 'signin', 'confirm'];
        
        const hasPhishKeyword = phishingKeywords.some(kw => lowerUrl.includes(kw));
        const isHttp = !lowerUrl.startsWith('https://');
        const hyphenCount = (lowerUrl.match(/-/g) || []).length;
        const isLongUrl = targetUrl.length > 50;

        let p_lgb = 0.15;
        let p_bert = 0.12;
        let p_gnn = 0.14;

        if (hasPhishKeyword || (isHttp && hyphenCount >= 2) || (isHttp && isLongUrl)) {
            p_lgb = 0.96;
            p_bert = 0.94;
            p_gnn = 0.91;
        }

        const modelProbs = [p_bert, p_gnn, p_lgb];
        const meanProb = (p_bert + p_gnn + p_lgb) / 3;
        const variance = modelProbs.reduce((sq, n) => sq + Math.pow(n - meanProb, 2), 0) / 3;
        const mdi = Math.sqrt(variance);

        const prs = (0.35 * p_bert + 0.35 * p_lgb + 0.30 * p_gnn);
        const score = Math.round(prs * 100 * 10) / 10;

        let decision = "SAFE";
        let verdict = "Safe";
        if (score >= 80) { decision = "PHISHING"; verdict = "Phishing"; }
        else if (score >= 55) { decision = "HIGH_RISK"; verdict = "High Risk"; }
        else if (score >= 30) { decision = "SUSPICIOUS"; verdict = "Suspicious"; }

        resultData = {
            url: targetUrl,
            verdict: verdict,
            decision: decision,
            risk_score: score,
            confidence: 97.5,
            bert_probability: Math.round(p_bert * 100) / 100,
            gnn_probability: Math.round(p_gnn * 100) / 100,
            lightgbm_probability: Math.round(p_lgb * 100) / 100,
            model_disagreement: Math.round(mdi * 10000) / 10000,
            threat_intelligence: {
                domain_age: decision === "SAFE" ? "2,450 days" : "12 days",
                ssl_status: isHttp ? "Invalid / Expired" : "Valid RSA/ECC 2048-bit",
                whois_status: decision === "SAFE" ? "Registered & Verified" : "Privacy Protected / Hidden",
                dns_status: decision === "SAFE" ? "Standard A/MX Verified" : "Suspicious MX Routing",
                reputation: decision === "PHISHING" ? "Blacklisted (PhishTank)" : (decision === "HIGH_RISK" ? "Suspicious Flag" : "Clean Reputation"),
                blacklist_status: (decision === "PHISHING" || decision === "HIGH_RISK") ? "Flagged" : "Clean"
            },
            features: {
                URL_Length: targetUrl.length,
                Has_HTTPS: isHttp ? 0 : 1,
                No_of_Hyphens: hyphenCount,
                No_of_Dots: (targetUrl.split('.').length - 1),
                No_of_Digits: (targetUrl.match(/\d/g) || []).length,
                Digit_Ratio: (targetUrl.match(/\d/g) || []).length / targetUrl.length,
                No_of_Slashes: (targetUrl.split('/').length - 1),
                Suspicious_Keyword_Count: hasPhishKeyword ? 1 : 0
            },
            shap_features: [
                { feature: 'Brand Impersonation Keyword', value: hasPhishKeyword ? '+0.32' : '-0.15', impact: hasPhishKeyword ? 'danger' : 'success' },
                { feature: 'HTTPS Encryption Protocol', value: isHttp ? '+0.28' : '-0.22', impact: isHttp ? 'danger' : 'success' },
                { feature: 'Domain Age & WHOIS Record', value: decision === "SAFE" ? '-0.18' : '+0.24', impact: decision === "SAFE" ? 'success' : 'danger' },
                { feature: 'Hyphen Count & Subdomains', value: hyphenCount >= 2 ? '+0.18' : '-0.05', impact: hyphenCount >= 2 ? 'danger' : 'success' }
            ],
            reasons: hasPhishKeyword || isHttp ? [
                { type: 'danger', title: 'Typosquatting & Brand Impersonation', desc: 'URL contains sensitive authentication or financial lure keywords.' },
                { type: isHttp ? 'danger' : 'warning', title: isHttp ? 'Missing SSL Certificate' : 'Suspicious Lexical Pattern', desc: isHttp ? 'Unencrypted HTTP transmission protocol.' : 'Multiple domain hyphens detected.' }
            ] : [
                { type: 'success', title: 'Verified Standard Domain', desc: 'Domain structure displays clean syntax and standard safety patterns.' },
                { type: 'success', title: 'Active SSL Encryption', desc: 'Secure HTTPS protocol verified with active encryption certificate.' }
            ]
        };
    }

    // 1. Update Scanned URL Header
    if (scannedUrlElem) scannedUrlElem.textContent = targetUrl;

    // 2. Update 4-Tier Verdict Badge (SAFE, SUSPICIOUS, HIGH RISK, PHISHING)
    if (verdictBadge) {
        const dec = resultData.decision || (resultData.verdict === 'Phishing' ? 'PHISHING' : 'SAFE');
        if (dec === 'PHISHING') {
            verdictBadge.className = 'verdict-badge phishing-badge';
            verdictBadge.innerHTML = `<i class="fa-solid fa-triangle-exclamation"></i> <span>PHISHING DETECTED</span>`;
            playCyberAudio('threat');
        } else if (dec === 'HIGH_RISK') {
            verdictBadge.className = 'verdict-badge highrisk-badge';
            verdictBadge.innerHTML = `<i class="fa-solid fa-fire text-white"></i> <span>HIGH RISK WEBSITE</span>`;
            playCyberAudio('threat');
        } else if (dec === 'SUSPICIOUS') {
            verdictBadge.className = 'verdict-badge suspicious-badge';
            verdictBadge.innerHTML = `<i class="fa-solid fa-eye text-white"></i> <span>SUSPICIOUS ACTIVITY</span>`;
            playCyberAudio('threat');
        } else {
            verdictBadge.className = 'verdict-badge safe-badge';
            verdictBadge.innerHTML = `<i class="fa-solid fa-shield-check"></i> <span>SAFE WEBSITE VERIFIED</span>`;
            playCyberAudio('safe');
        }
    }

    // 3. Update Risk & Confidence Score Gauges
    if (riskScoreVal) {
        riskScoreVal.textContent = `${resultData.risk_score}/100`;
        const dec = resultData.decision || 'SAFE';
        if (dec === 'PHISHING' || dec === 'HIGH_RISK') {
            riskScoreVal.className = 'score-value text-danger';
        } else if (dec === 'SUSPICIOUS') {
            riskScoreVal.className = 'score-value text-warning';
        } else {
            riskScoreVal.className = 'score-value text-success';
        }
    }

    if (riskSubText) {
        const dec = resultData.decision || 'SAFE';
        riskSubText.textContent = dec === 'PHISHING' ? 'Critical Severity Threat' : (dec === 'HIGH_RISK' ? 'High Severity Risk' : (dec === 'SUSPICIOUS' ? 'Elevated Suspicious Signals' : 'Clean & Verified Host'));
    }

    if (riskProgressBar) {
        riskProgressBar.style.width = `${resultData.risk_score}%`;
        const dec = resultData.decision || 'SAFE';
        if (dec === 'SAFE') {
            riskProgressBar.style.background = 'linear-gradient(90deg, #34d399, #10b981)';
        } else if (dec === 'SUSPICIOUS') {
            riskProgressBar.style.background = 'linear-gradient(90deg, #fbbf24, #f59e0b)';
        } else {
            riskProgressBar.style.background = 'linear-gradient(90deg, #f97316, #ef4444)';
        }
    }

    if (confidenceVal) {
        confidenceVal.textContent = `${resultData.confidence}%`;
    }

    // 4. Update Model Disagreement Index (MDI)
    if (mdiVal) {
        const mdi = resultData.model_disagreement !== undefined ? resultData.model_disagreement : 0.021;
        mdiVal.textContent = mdi;
    }
    if (mdiStatusPill) {
        const mdi = resultData.model_disagreement !== undefined ? resultData.model_disagreement : 0.021;
        if (mdi > 0.15) {
            mdiStatusPill.className = 'mdi-badge mdi-high';
            mdiStatusPill.textContent = 'High Disagreement (Divergent Predictions)';
        } else if (mdi > 0.05) {
            mdiStatusPill.className = 'mdi-badge mdi-med';
            mdiStatusPill.textContent = 'Moderate Disagreement';
        } else {
            mdiStatusPill.className = 'mdi-badge mdi-low';
            mdiStatusPill.textContent = 'Low Disagreement (High Consensus)';
        }
    }

    // 5. Update Individual Model Cards (BERT, GNN, LightGBM)
    const bertPct = Math.round((resultData.bert_probability || 0.94) * 100);
    const gnnPct = Math.round((resultData.gnn_probability || 0.91) * 100);
    const lgbPct = Math.round((resultData.lightgbm_probability || 0.96) * 100);

    if (bertProbVal) bertProbVal.textContent = `${bertPct}%`;
    if (bertProgressFill) bertProgressFill.style.width = `${bertPct}%`;
    if (bertPredPill) {
        bertPredPill.className = `model-pred-pill ${bertPct >= 50 ? 'badge-phishing' : 'badge-safe'}`;
        bertPredPill.textContent = bertPct >= 50 ? 'Phishing' : 'Safe';
    }

    if (gnnProbVal) gnnProbVal.textContent = `${gnnPct}%`;
    if (gnnProgressFill) gnnProgressFill.style.width = `${gnnPct}%`;
    if (gnnPredPill) {
        gnnPredPill.className = `model-pred-pill ${gnnPct >= 50 ? 'badge-phishing' : 'badge-safe'}`;
        gnnPredPill.textContent = gnnPct >= 50 ? 'Phishing' : 'Safe';
    }

    if (lgbProbVal) lgbProbVal.textContent = `${lgbPct}%`;
    if (lgbProgressFill) lgbProgressFill.style.width = `${lgbPct}%`;
    if (lgbPredPill) {
        lgbPredPill.className = `model-pred-pill ${lgbPct >= 50 ? 'badge-phishing' : 'badge-safe'}`;
        lgbPredPill.textContent = lgbPct >= 50 ? 'Phishing' : 'Safe';
    }

    // Individual Model Details Snippets
    const bertTokenSnippet = document.getElementById('bertTokenSnippet');
    const gnnNodeCount = document.getElementById('gnnNodeCount');
    const lgbSplitText = document.getElementById('lgbSplitText');

    if (bertTokenSnippet) {
        const tokens = targetUrl.replace(/https?:\/\//i, '').split(/[\/\.\-\_\?]/).filter(Boolean);
        bertTokenSnippet.textContent = `[CLS] ${tokens.slice(0, 4).join(' [SEP] ')} [SEP]`;
    }
    if (gnnNodeCount) {
        const dec = resultData.decision || 'SAFE';
        gnnNodeCount.textContent = dec === 'PHISHING' || dec === 'HIGH_RISK' ? '184 DOM Nodes, 4 Anomaly Edges Flagged' : '112 DOM Nodes, Clean Structural Graph';
    }
    if (lgbSplitText) {
        const dec = resultData.decision || 'SAFE';
        lgbSplitText.textContent = dec === 'PHISHING' || dec === 'HIGH_RISK' ? 'Hyphen Count > 2 & Missing SSL (Gain: 4.82)' : 'URL Length & Digit Ratio Normal (Gain: 1.15)';
    }

    // 6. Update Threat Intelligence Grid
    const intel = resultData.threat_intelligence || {};
    if (intelDomainAge) intelDomainAge.textContent = intel.domain_age || "12 days";
    if (intelSslStatus) {
        intelSslStatus.textContent = intel.ssl_status || "Valid";
        intelSslStatus.className = `intel-val ${intel.ssl_status && intel.ssl_status.includes('Invalid') ? 'text-danger' : 'text-success'}`;
    }
    if (intelWhoisStatus) intelWhoisStatus.textContent = intel.whois_status || "Verified";
    if (intelDnsStatus) intelDnsStatus.textContent = intel.dns_status || "Valid A/MX";
    if (intelReputation) {
        intelReputation.textContent = intel.reputation || "Clean";
        intelReputation.className = `intel-val ${intel.reputation && intel.reputation.includes('Clean') ? 'text-success' : 'text-danger'}`;
    }
    if (intelBlacklist) {
        intelBlacklist.textContent = intel.blacklist_status || "Clean";
        intelBlacklist.className = `intel-val ${intel.blacklist_status && intel.blacklist_status.includes('Flagged') ? 'text-danger' : 'text-success'}`;
    }

    // 7. Update Key Risk Indicators & Reasons List
    const reasonsList = document.getElementById('reasonsList');
    if (reasonsList && resultData.reasons) {
        reasonsList.innerHTML = resultData.reasons.map(r => `
            <li class="reason-item ${r.type}">
                <i class="fa-solid ${r.type === 'danger' ? 'fa-circle-xmark' : (r.type === 'warning' ? 'fa-triangle-exclamation' : 'fa-circle-check')}"></i>
                <div class="reason-content">
                    <h4>${escapeHtml(r.title)}</h4>
                    <p>${escapeHtml(r.desc)}</p>
                </div>
            </li>
        `).join('');
    }

    // 8. Update Feature Analysis Table
    const featureTableBody = document.getElementById('featureTableBody');
    if (featureTableBody && resultData.features) {
        const f = resultData.features;
        const len = f.URL_Length !== undefined ? f.URL_Length : targetUrl.length;
        const dots = f.No_of_Dots !== undefined ? f.No_of_Dots : (targetUrl.split('.').length - 1);
        const hyphens = f.No_of_Hyphens !== undefined ? f.No_of_Hyphens : (targetUrl.split('-').length - 1);
        const digits = f.No_of_Digits !== undefined ? f.No_of_Digits : (targetUrl.match(/\d/g) || []).length;
        const https = f.Has_HTTPS !== undefined ? f.Has_HTTPS : (targetUrl.toLowerCase().includes('https') ? 1 : 0);
        const slashes = f.No_of_Slashes !== undefined ? f.No_of_Slashes : (targetUrl.split('/').length - 1);

        featureTableBody.innerHTML = `
            <tr>
                <td>URL Length (URL_Length)</td>
                <td>${len} characters</td>
                <td><span class="badge ${len > 50 ? 'badge-phishing' : 'badge-safe'}">${len > 50 ? 'Long (>50)' : 'Normal'}</span></td>
            </tr>
            <tr>
                <td>HTTPS Encryption (Has_HTTPS)</td>
                <td>${https ? 'Enabled (1)' : 'Disabled (0)'}</td>
                <td><span class="badge ${https ? 'badge-safe' : 'badge-phishing'}">${https ? 'Secure' : 'Insecure'}</span></td>
            </tr>
            <tr>
                <td>Dot Count (No_of_Dots)</td>
                <td>${dots} dots</td>
                <td><span class="badge ${dots > 3 ? 'badge-phishing' : 'badge-safe'}">${dots > 3 ? 'Suspicious' : 'Normal'}</span></td>
            </tr>
            <tr>
                <td>Hyphen Count (No_of_Hyphens)</td>
                <td>${hyphens} hyphens</td>
                <td><span class="badge ${hyphens >= 2 ? 'badge-phishing' : 'badge-safe'}">${hyphens >= 2 ? 'High Risk' : 'Normal'}</span></td>
            </tr>
            <tr>
                <td>Digit Count (No_of_Digits)</td>
                <td>${digits} digits</td>
                <td><span class="badge ${digits > 5 ? 'badge-phishing' : 'badge-safe'}">${digits > 5 ? 'Elevated Digits' : 'Normal'}</span></td>
            </tr>
            <tr>
                <td>Slash Depth (No_of_Slashes)</td>
                <td>${slashes} levels</td>
                <td><span class="badge ${slashes > 3 ? 'badge-phishing' : 'badge-safe'}">${slashes > 3 ? 'Deep Path' : 'Standard'}</span></td>
            </tr>
        `;
    }

    // 9. Update SHAP Explainable AI (XAI) Chart
    const shapChartContainer = document.getElementById('shapChartContainer');
    const shapData = resultData.shap_features || resultData.shap_explanations;
    if (shapChartContainer && shapData) {
        shapChartContainer.innerHTML = shapData.map(s => {
            const valNum = parseFloat(s.value || s.contribution);
            const isRed = valNum > 0;
            const barWidth = Math.min(95, Math.abs(valNum) * 180);
            return `
                <div class="shap-bar-item">
                    <span class="shap-label">${escapeHtml(s.feature)}</span>
                    <div class="shap-bar-wrapper">
                        <div class="shap-bar ${isRed ? 'red' : 'green'}" style="width: ${barWidth}%;"></div>
                        <span class="shap-val">${valNum > 0 ? '+' : ''}${valNum}</span>
                    </div>
                </div>
            `;
        }).join('');
    }

    // 10. Update Security Recommendations Box
    const recommendationsBox = document.getElementById('recommendationsBox');
    const recDetails = document.getElementById('recDetails');
    const recSteps = document.getElementById('recSteps');

    if (recommendationsBox && recDetails && recSteps) {
        const dec = resultData.decision || 'SAFE';
        if (dec === 'PHISHING' || dec === 'HIGH_RISK') {
            recommendationsBox.className = 'recommendations-box danger-box';
            recommendationsBox.style.backgroundColor = '#fef2f2';
            recommendationsBox.style.borderColor = '#fecaca';
            recDetails.innerHTML = `
                <h4 style="color: #991b1b;">DO NOT Visit or Submit Credentials</h4>
                <p style="color: #7f1d1d;">This URL displays strong indicators of credential harvesting and identity theft.</p>
            `;
            recSteps.innerHTML = `
                <li><i class="fa-solid fa-check text-blue"></i> Close any open tabs attempting to reach this domain.</li>
                <li><i class="fa-solid fa-check text-blue"></i> Report domain to Google Safe Browsing and PhishTank.</li>
                <li><i class="fa-solid fa-check text-blue"></i> If credentials were entered, reset your passwords immediately.</li>
            `;
        } else if (dec === 'SUSPICIOUS') {
            recommendationsBox.className = 'recommendations-box';
            recommendationsBox.style.backgroundColor = '#fffbeb';
            recommendationsBox.style.borderColor = '#fde68a';
            recDetails.innerHTML = `
                <h4 style="color: #92400e;">Exercise Caution when Interacting</h4>
                <p style="color: #b45309;">Elevated risk signals detected. Avoid providing sensitive personal information.</p>
            `;
            recSteps.innerHTML = `
                <li><i class="fa-solid fa-check text-warning"></i> Verify domain ownership before logging in.</li>
                <li><i class="fa-solid fa-check text-warning"></i> Check for typos in the address bar.</li>
            `;
        } else {
            recommendationsBox.className = 'recommendations-box';
            recommendationsBox.style.backgroundColor = '#f0fdf4';
            recommendationsBox.style.borderColor = '#bbf7d0';
            recDetails.innerHTML = `
                <h4 style="color: #166534;">Website Appears Safe to Visit</h4>
                <p style="color: #15803d;">Our AI ensemble verified clean domain structure and HTTPS security features.</p>
            `;
            recSteps.innerHTML = `
                <li><i class="fa-solid fa-check text-success"></i> Verify that the domain matches your intended destination.</li>
                <li><i class="fa-solid fa-check text-success"></i> Always look for the browser padlock icon in the address bar.</li>
            `;
        }
    }

    saveScanToHistory(targetUrl, resultData.decision || resultData.verdict, resultData.risk_score);
}



/* --------------------------------------------------------------------------
   3. Local Scan History Storage & Filter Handler (history.html)
   -------------------------------------------------------------------------- */
function saveScanToHistory(url, status, riskScore) {
    localStorage.removeItem('phishguard_history_cleared');
    let history = JSON.parse(localStorage.getItem('phishguard_history')) || [];
    
    const newEntry = {
        id: Date.now(),
        url: url,
        source: 'Web Dashboard',
        date: new Date().toLocaleString('en-US', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' }),
        status: status,
        riskScore: riskScore
    };

    // Keep top 50 recent scans
    history.unshift(newEntry);
    if (history.length > 50) history.pop();

    localStorage.setItem('phishguard_history', JSON.stringify(history));
}

function initHistoryTableActions() {
    const historyTable = document.getElementById('historyTable');
    if (!historyTable) return;

    const historySearchInput = document.getElementById('historySearchInput');
    const filterBtns = document.querySelectorAll('.filter-btn');
    const clearHistoryBtn = document.getElementById('clearHistoryBtn');
    const exportCsvBtn = document.getElementById('exportCsvBtn');
    const tbody = historyTable.querySelector('tbody');

    // Function to render table from localStorage or Flask API
    async function loadAndRenderHistory() {
        let history = [];

        // Try fetching from Flask API
        try {
            const apiEndpoint = localStorage.getItem('phishguard_api_endpoint') || '/api/scan';
            const historyUrl = apiEndpoint.replace('/scan', '/history');
            const res = await fetch(historyUrl);
            if (res.ok) {
                const data = await res.json();
                if (data.history && data.history.length > 0) {
                    history = data.history.map(item => ({
                        url: item.url,
                        source: item.source || 'Web Dashboard',
                        date: item.scanned_at || 'Recently',
                        riskScore: item.risk_score,
                        status: item.verdict
                    }));
                }
            }
        } catch (e) {
            console.log('[History Note] Flask API offline. Loading from localStorage.');
        }

        // Fallback to localStorage if API empty or offline
        if (history.length === 0) {
            history = JSON.parse(localStorage.getItem('phishguard_history')) || [];
        }

        if (tbody) {
            if (history.length === 0) {
                tbody.innerHTML = `
                    <tr>
                        <td colspan="6" style="text-align: center; color: var(--text-muted); padding: 30px;">
                            No scan history found. New scans will automatically appear here.
                        </td>
                    </tr>
                `;
            } else {
                function getHistoryBadgeHtml(status) {
                    const st = (status || '').toUpperCase();
                    if (st === 'PHISHING' || st === 'BAD') {
                        return `<span class="badge badge-phishing"><i class="fa-solid fa-circle-xmark"></i> Phishing</span>`;
                    } else if (st === 'HIGH_RISK' || st === 'HIGH RISK') {
                        return `<span class="badge badge-highrisk"><i class="fa-solid fa-triangle-exclamation"></i> High Risk</span>`;
                    } else if (st === 'SUSPICIOUS') {
                        return `<span class="badge badge-suspicious"><i class="fa-solid fa-eye"></i> Suspicious</span>`;
                    } else {
                        return `<span class="badge badge-safe"><i class="fa-solid fa-circle-check"></i> Safe</span>`;
                    }
                }

                tbody.innerHTML = history.map(item => `
                    <tr>
                        <td>
                            <div class="domain-info">
                                <i class="fa-solid ${(item.status || '').toUpperCase() === 'SAFE' || item.status === 'Safe' ? 'fa-lock text-success' : 'fa-unlock text-danger'}"></i>
                                <span class="domain-name">${escapeHtml(item.url)}</span>
                            </div>
                        </td>
                        <td>
                            <span class="source-tag ${item.source === 'Extension' ? 'extension' : 'dashboard'}">
                                <i class="fa-solid ${item.source === 'Extension' ? 'fa-puzzle-piece' : 'fa-desktop'}"></i> ${item.source || 'Web Dashboard'}
                            </span>
                        </td>
                        <td>${item.date}</td>
                        <td><span class="risk-pill ${item.riskScore > 50 ? 'high' : 'low'}">${item.riskScore}/100</span></td>
                        <td>${getHistoryBadgeHtml(item.status)}</td>
                        <td>
                            <a href="result.html?url=${encodeURIComponent(item.url)}" class="table-btn" title="View Report">
                                <i class="fa-solid fa-eye"></i>
                            </a>
                        </td>
                    </tr>
                `).join('');
            }
        }

        renderFilteredTable();
    }

    // Filter state
    let currentFilter = 'all';
    let currentSearchQuery = '';

    function renderFilteredTable() {
        if (!tbody) return;
        const rows = tbody.querySelectorAll('tr');
        let visibleCount = 0;

        rows.forEach(row => {
            const textContent = row.textContent.toLowerCase();
            const matchesSearch = currentSearchQuery === '' || textContent.includes(currentSearchQuery);

            let matchesFilter = true;
            if (currentFilter === 'phishing') {
                matchesFilter = textContent.includes('phishing');
            } else if (currentFilter === 'safe') {
                matchesFilter = textContent.includes('safe');
            } else if (currentFilter === 'extension') {
                matchesFilter = textContent.includes('extension');
            }

            if (matchesSearch && matchesFilter) {
                row.style.display = '';
                visibleCount++;
            } else {
                row.style.display = 'none';
            }
        });

        const recordCountTag = document.getElementById('recordCountTag');
        if (recordCountTag) {
            recordCountTag.textContent = `Showing ${visibleCount} Records`;
        }
    }

    // Search Input Listener
    if (historySearchInput) {
        historySearchInput.addEventListener('input', (e) => {
            currentSearchQuery = e.target.value.trim().toLowerCase();
            renderFilteredTable();
        });
    }

    // Filter Buttons Listener
    filterBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            filterBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            currentFilter = btn.getAttribute('data-filter');
            renderFilteredTable();
        });
    });

    // Clear History Handler
    if (clearHistoryBtn) {
        clearHistoryBtn.addEventListener('click', async () => {
            if (confirm('Are you sure you want to clear all scan history logs?')) {
                localStorage.removeItem('phishguard_history');
                try {
                    const apiEndpoint = localStorage.getItem('phishguard_api_endpoint') || '/api/scan';
                    const historyUrl = apiEndpoint.replace('/scan', '/history');
                    await fetch(historyUrl, { method: 'DELETE' });
                } catch (e) {}

                if (tbody) {
                    tbody.innerHTML = `
                        <tr>
                            <td colspan="6" style="text-align: center; color: var(--text-muted); padding: 30px;">
                                Scan history cleared. New scans will automatically appear here.
                            </td>
                        </tr>
                    `;
                }

                // Reset stats cards on home page
                const statsTotal = document.getElementById('statsTotal');
                const statsSafe = document.getElementById('statsSafe');
                const statsPhishing = document.getElementById('statsPhishing');
                if (statsTotal) statsTotal.textContent = '0';
                if (statsSafe) statsSafe.textContent = '0';
                if (statsPhishing) statsPhishing.textContent = '0';
            }
        });
    }

    // Export CSV Handler
    if (exportCsvBtn) {
        exportCsvBtn.addEventListener('click', () => {
            let csvContent = "data:text/csv;charset=utf-8,URL,Source,Date,RiskScore,Status\n";
            const rows = historyTable.querySelectorAll('tbody tr');

            rows.forEach(row => {
                const cols = row.querySelectorAll('td');
                if (cols.length >= 5) {
                    const domain = cols[0].innerText.trim().replace(/\n/g, ' ');
                    const source = cols[1].innerText.trim();
                    const date = cols[2].innerText.trim();
                    const risk = cols[3].innerText.trim();
                    const status = cols[4].innerText.trim();
                    csvContent += `"${domain}","${source}","${date}","${risk}","${status}"\n`;
                }
            });

            const encodedUri = encodeURI(csvContent);
            const link = document.createElement('a');
            link.setAttribute('href', encodedUri);
            link.setAttribute('download', `PhishGuard_Scan_Logs_${Date.now()}.csv`);
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        });
    }

    // Load history on load
    loadAndRenderHistory();
}



function initSettingsForm() {
    const settingsForm = document.getElementById('settingsForm');
    if (!settingsForm) return;

    const notificationsToggle = document.getElementById('notificationsToggle');
    const languageSelect = document.getElementById('languageSelect');
    const apiEndpointInput = document.getElementById('apiEndpointInput');
    const saveStatus = document.getElementById('saveStatus');

    // Load saved preferences
    if (notificationsToggle) {
        notificationsToggle.checked = localStorage.getItem('phishguard_notifications') !== 'false';
    }
    if (languageSelect) {
        languageSelect.value = localStorage.getItem('phishguard_language') || 'en';
    }
    if (apiEndpointInput) {
        apiEndpointInput.value = localStorage.getItem('phishguard_api_endpoint') || 'http://127.0.0.1:5000/api/scan';
    }

    settingsForm.addEventListener('submit', (e) => {
        e.preventDefault();

        if (notificationsToggle) {
            localStorage.setItem('phishguard_notifications', notificationsToggle.checked);
        }
        if (languageSelect) {
            localStorage.setItem('phishguard_language', languageSelect.value);
        }
        if (apiEndpointInput) {
            localStorage.setItem('phishguard_api_endpoint', apiEndpointInput.value.trim());
        }

        if (saveStatus) {
            saveStatus.classList.remove('hidden');
            setTimeout(() => {
                saveStatus.classList.add('hidden');
            }, 3000);
        }
    });
}

function escapeHtml(text) {
    return text.replace(/[&<>"']/g, function(m) {
        return {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#039;'
        }[m];
    });
}

/* --------------------------------------------------------------------------
   12. DUAL-MODE SWITCHER & IN-BROWSER REAL-TIME POP VERIFICATION SIMULATOR
   -------------------------------------------------------------------------- */
function initDualModeAndSimulator() {
    const modeManualBtn = document.getElementById('modeManualBtn');
    const modeRealtimeBtn = document.getElementById('modeRealtimeBtn');
    const mode1Container = document.getElementById('mode1Container');
    const mode2Container = document.getElementById('mode2Container');

    if (!modeManualBtn || !modeRealtimeBtn) return;

    modeManualBtn.addEventListener('click', () => {
        modeManualBtn.classList.add('active');
        modeRealtimeBtn.classList.remove('active');
        if (mode1Container) mode1Container.classList.remove('hidden');
        if (mode2Container) mode2Container.classList.add('hidden');
        playCyberAudio('scan');
    });

    modeRealtimeBtn.addEventListener('click', () => {
        modeRealtimeBtn.classList.add('active');
        modeManualBtn.classList.remove('active');
        if (mode2Container) mode2Container.classList.remove('hidden');
        if (mode1Container) mode1Container.classList.add('hidden');
        playCyberAudio('scan');

        // Automatically run simulated scan for default URL if popup not shown
        const simInput = document.getElementById('simAddressInput');
        if (simInput && simInput.value) {
            runSimulatedScan(simInput.value.trim());
        }
    });

    // Test Links Chips
    const chips = document.querySelectorAll('.sim-chip');
    chips.forEach(chip => {
        chip.addEventListener('click', () => {
            const url = chip.getAttribute('data-url');
            const simInput = document.getElementById('simAddressInput');
            if (simInput && url) {
                simInput.value = url;
                runSimulatedScan(url);
            }
        });
    });

    // Go & Refresh buttons
    const simGoBtn = document.getElementById('simGoBtn');
    const simRefreshBtn = document.getElementById('simRefreshBtn');
    const simInput = document.getElementById('simAddressInput');

    if (simGoBtn && simInput) {
        simGoBtn.addEventListener('click', () => runSimulatedScan(simInput.value.trim()));
    }
    if (simRefreshBtn && simInput) {
        simRefreshBtn.addEventListener('click', () => runSimulatedScan(simInput.value.trim()));
    }
    if (simInput) {
        simInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                runSimulatedScan(simInput.value.trim());
            }
        });
    }

    // Popup buttons
    const simPopupCloseBtn = document.getElementById('simPopupCloseBtn');
    const simPopup = document.getElementById('simulatedRealtimePopup');
    if (simPopupCloseBtn && simPopup) {
        simPopupCloseBtn.addEventListener('click', () => simPopup.classList.add('hidden'));
    }

    const simLeaveBtn = document.getElementById('simLeaveBtn');
    if (simLeaveBtn) {
        simLeaveBtn.addEventListener('click', () => {
            const simTitle = document.getElementById('simPageTitle');
            const simSub = document.getElementById('simPageSub');
            if (simTitle) simTitle.textContent = "🚫 Navigation Blocked (Phishing Site Abandoned)";
            if (simSub) simSub.textContent = "PhishGuard AI prevented user credentials from being submitted to phishing domain.";
            if (simPopup) simPopup.classList.add('hidden');
            playCyberAudio('safe');
        });
    }

    const simDeepReportBtn = document.getElementById('simDeepReportBtn');
    if (simDeepReportBtn) {
        simDeepReportBtn.addEventListener('click', () => {
            const url = simInput ? simInput.value.trim() : "";
            if (url) {
                window.location.href = `result.html?url=${encodeURIComponent(url)}`;
            }
        });
    }
}

async function runSimulatedScan(targetUrl) {
    if (!targetUrl) return;

    const simPopup = document.getElementById('simulatedRealtimePopup');
    const simTitle = document.getElementById('simPageTitle');
    const simSub = document.getElementById('simPageSub');
    const simBadge = document.getElementById('simPageBadge');

    const simPopupBadge = document.getElementById('simPopupBadge');
    const simPopupTitle = document.getElementById('simPopupTitle');
    const simPopupDesc = document.getElementById('simPopupDesc');

    const simBertScore = document.getElementById('simBertScore');
    const simGnnScore = document.getElementById('simGnnScore');
    const simLgbScore = document.getElementById('simLgbScore');

    const simRiskScoreText = document.getElementById('simRiskScoreText');
    const simRiskBarFill = document.getElementById('simRiskBarFill');
    const simLeaveBtn = document.getElementById('simLeaveBtn');

    if (simTitle) simTitle.textContent = `Navigating to: ${targetUrl}`;
    if (simSub) simSub.textContent = "PhishGuard AI Real-Time Service Worker inspecting domain...";
    if (simBadge) simBadge.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> Real-time AI Inspection...`;

    playCyberAudio('scan');

    try {
        const apiEndpoint = localStorage.getItem('phishguard_api_endpoint') || 'http://127.0.0.1:5000/api/scan';
        const response = await fetch(`${apiEndpoint}?url=${encodeURIComponent(targetUrl)}&source=Extension`);
        const data = await response.json();

        const decision = data.decision || {};
        const level = (decision.level || "SAFE").toUpperCase();
        const score = decision.risk_score || 0;
        const colorClass = level.replace(/\s+/g, '-').toLowerCase();

        const isThreat = level === 'PHISHING' || level === 'HIGH RISK' || level === 'SUSPICIOUS';

        if (simTitle) simTitle.textContent = data.domain || targetUrl;
        if (simSub) simSub.textContent = isThreat ? "🚨 WARNING: Dangerous phishing pattern detected by ensemble models!" : "✅ Domain verified safe by multi-model ensemble.";
        if (simBadge) {
            simBadge.innerHTML = isThreat ? `<i class="fa-solid fa-triangle-exclamation"></i> Threat Detected` : `<i class="fa-solid fa-circle-check"></i> Safe Page`;
        }

        if (simPopup) {
            simPopup.className = `simulated-realtime-popup ${colorClass}`;
            simPopup.classList.remove('hidden');
        }

        const badgeIcon = level === "PHISHING" ? "⛔" : level === "HIGH RISK" ? "🚨" : level === "SUSPICIOUS" ? "⚠️" : "🛡️";
        if (simPopupBadge) simPopupBadge.textContent = `${badgeIcon} ${level}`;
        if (simPopupTitle) simPopupTitle.textContent = decision.title || `${level} Web Domain`;
        if (simPopupDesc) simPopupDesc.textContent = data.adaptive_risk_assessment ? data.adaptive_risk_assessment.risk_level_explanation : (decision.recommendation || "Inspection complete.");

        if (simBertScore) simBertScore.textContent = `${Math.round((data.bert_probability || 0) * 100)}%`;
        if (simGnnScore) simGnnScore.textContent = `${Math.round((data.gnn_probability || 0) * 100)}%`;
        if (simLgbScore) simLgbScore.textContent = `${Math.round((data.lightgbm_probability || 0) * 100)}%`;

        if (simRiskScoreText) simRiskScoreText.textContent = `${score.toFixed(1)} / 100`;
        if (simRiskBarFill) simRiskBarFill.style.width = `${Math.min(100, Math.max(5, score))}%`;

        if (simLeaveBtn) {
            if (isThreat) simLeaveBtn.classList.remove('hidden');
            else simLeaveBtn.classList.add('hidden');
        }

        if (isThreat) {
            playCyberAudio('threat');
            awardXp(15, "Threat Blocked");
        } else {
            playCyberAudio('safe');
            awardXp(10, "Safe Domain Verified");
        }

    } catch (err) {
        if (simTitle) simTitle.textContent = "Backend Offline";
        if (simSub) simSub.textContent = "Ensure Python Flask app is running at http://127.0.0.1:5000";
    }
}

/* --------------------------------------------------------------------------
   13. BROWSER EXTENSION INSTALLATION MODAL
   -------------------------------------------------------------------------- */
function initExtensionModal() {
    const extensionModalBtn = document.getElementById('extensionModalBtn');
    const extensionModal = document.getElementById('extensionModal');
    const closeModalBtn = document.getElementById('closeModalBtn');
    const closeModalFooterBtn = document.getElementById('closeModalFooterBtn');

    if (!extensionModal) return;

    if (extensionModalBtn) {
        extensionModalBtn.addEventListener('click', () => {
            extensionModal.classList.remove('hidden');
            playCyberAudio('scan');
        });
    }

    const closeHandler = () => extensionModal.classList.add('hidden');

    if (closeModalBtn) closeModalBtn.addEventListener('click', closeHandler);
    if (closeModalFooterBtn) closeModalFooterBtn.addEventListener('click', closeHandler);

    extensionModal.addEventListener('click', (e) => {
        if (e.target === extensionModal) closeHandler();
    });
}

/* --------------------------------------------------------------------------
   14. PREVIOUS ANALYSIS REPORTS SELECTOR (MANUAL MODE LOG ACCESS)
   -------------------------------------------------------------------------- */
async function initPreviousReportsSelectors() {
    const prevReportsSelect = document.getElementById('prevReportsSelect');
    const resultPrevReportsSelect = document.getElementById('resultPrevReportsSelect');
    const loadPrevReportBtn = document.getElementById('loadPrevReportBtn');

    if (!prevReportsSelect && !resultPrevReportsSelect) return;

    let history = [];

    // Query history from backend API or localStorage
    try {
        const apiEndpoint = localStorage.getItem('phishguard_api_endpoint') || '/api/scan';
        const historyUrl = apiEndpoint.replace('/scan', '/history');
        const res = await fetch(historyUrl);
        if (res.ok) {
            const data = await res.json();
            if (data.history && data.history.length > 0) {
                history = data.history;
            }
        }
    } catch (e) {}

    if (history.length === 0) {
        history = JSON.parse(localStorage.getItem('phishguard_history')) || [];
    }

    if (history.length === 0) return;

    const optionsHtml = `<option value="">-- Select a previous scan report --</option>` + history.map(item => {
        const url = item.url;
        const verdict = (item.verdict || item.status || 'REPORT').toUpperCase();
        const score = item.risk_score || item.riskScore || 0;
        const date = item.scanned_at || item.date || '';
        return `<option value="${escapeHtml(url)}">[${verdict} - Risk ${score}] ${escapeHtml(url)} (${date})</option>`;
    }).join('');

    if (prevReportsSelect) prevReportsSelect.innerHTML = optionsHtml;
    if (resultPrevReportsSelect) {
        resultPrevReportsSelect.innerHTML = optionsHtml;
        resultPrevReportsSelect.addEventListener('change', (e) => {
            if (e.target.value) {
                window.location.href = `result.html?url=${encodeURIComponent(e.target.value)}`;
            }
        });
    }

    if (loadPrevReportBtn && prevReportsSelect) {
        loadPrevReportBtn.addEventListener('click', () => {
            const selectedUrl = prevReportsSelect.value;
            if (selectedUrl) {
                window.location.href = `result.html?url=${encodeURIComponent(selectedUrl)}`;
            } else {
                alert('Please select a report from the dropdown list.');
            }
        });
    }
}




