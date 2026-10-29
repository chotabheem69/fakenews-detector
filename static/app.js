/**
 * VeritasAI - Frontend Client Application
 * Handles interactivity, API communication, XAI token highlighting,
 * Chart.js visualizations, and API key management.
 */

document.addEventListener('DOMContentLoaded', () => {
    // Initialize Lucide Icons
    if (window.lucide) {
        window.lucide.createIcons();
    }

    // State
    const state = {
        activeTab: 'detector',
        inputMode: 'text', // 'text' or 'url'
        provider: localStorage.getItem('veritas_llm_provider') || 'freellmapi',
        apiKey: localStorage.getItem('veritas_llm_api_key') || localStorage.getItem('veritas_gemini_api_key') || '',
        baseUrl: localStorage.getItem('veritas_llm_base_url') || 'https://api.freellmapi.com/v1',
        model: localStorage.getItem('veritas_llm_model') || 'llama-3.1-70b',
        currentAnalysis: null,
        historyChart: null,
        datasetPage: 1,
        datasetLimit: 6,
        datasetCategory: 'All',
        datasetLabel: 'All',
        datasetSearch: '',
        cachedDatasetItems: []
    };

    // DOM Elements
    const elements = {
        themeToggleBtn: document.getElementById('themeToggleBtn'),
        themeIcon: document.getElementById('themeIcon'),
        navTabs: document.querySelectorAll('.nav-tab'),
        tabPanels: document.querySelectorAll('.tab-panel'),
        sampleChips: document.getElementById('sampleChips'),
        modeTextBtn: document.getElementById('modeTextBtn'),
        modeUrlBtn: document.getElementById('modeUrlBtn'),
        textModeForm: document.getElementById('textModeForm'),
        urlModeForm: document.getElementById('urlModeForm'),
        headlineInput: document.getElementById('headlineInput'),
        contentInput: document.getElementById('contentInput'),
        urlInput: document.getElementById('urlInput'),
        charCount: document.getElementById('charCount'),
        analyzeBtn: document.getElementById('analyzeBtn'),
        clearInputBtn: document.getElementById('clearInputBtn'),
        deepCheckCheckbox: document.getElementById('deepCheckCheckbox'),
        apiKeyStatusBadge: document.getElementById('apiKeyStatusBadge'),
        engineStatus: document.getElementById('engineStatus'),
        loadingState: document.getElementById('loadingState'),
        resultsContainer: document.getElementById('resultsContainer'),
        
        // Verdict elements
        verdictBanner: document.getElementById('verdictBanner'),
        verdictIcon: document.getElementById('verdictIcon'),
        verdictBadge: document.getElementById('verdictBadge'),
        verdictHeadline: document.getElementById('verdictHeadline'),
        verdictSubtext: document.getElementById('verdictSubtext'),
        credibilityScoreVal: document.getElementById('credibilityScoreVal'),
        
        // Metrics
        sensationalismVal: document.getElementById('sensationalismVal'),
        sensationalismBar: document.getElementById('sensationalismBar'),
        sensationalismDesc: document.getElementById('sensationalismDesc'),
        clickbaitVal: document.getElementById('clickbaitVal'),
        clickbaitBar: document.getElementById('clickbaitBar'),
        clickbaitDesc: document.getElementById('clickbaitDesc'),
        biasVal: document.getElementById('biasVal'),
        biasBar: document.getElementById('biasBar'),
        biasDesc: document.getElementById('biasDesc'),
        attributionVal: document.getElementById('attributionVal'),
        attributionBar: document.getElementById('attributionBar'),
        attributionDesc: document.getElementById('attributionDesc'),

        // XAI & Gemini
        highlightedTextBox: document.getElementById('highlightedTextBox'),
        flagsSummary: document.getElementById('flagsSummary'),
        geminiAuditCard: document.getElementById('geminiAuditCard'),
        geminiAuditContent: document.getElementById('geminiAuditContent'),
        geminiModelBadge: document.getElementById('geminiModelBadge'),
        
        // Toolbars
        copyReportBtn: document.getElementById('copyReportBtn'),
        downloadJsonBtn: document.getElementById('downloadJsonBtn'),
        googleVerifyBtn: document.getElementById('googleVerifyBtn'),
        
        // Settings Modal
        settingsModal: document.getElementById('settingsModal'),
        openSettingsBtn: document.getElementById('openSettingsBtn'),
        closeSettingsBtn: document.getElementById('closeSettingsBtn'),
        providerSelect: document.getElementById('providerSelect'),
        providerInfoText: document.getElementById('providerInfoText'),
        baseUrlGroup: document.getElementById('baseUrlGroup'),
        baseUrlInput: document.getElementById('baseUrlInput'),
        apiKeyLabel: document.getElementById('apiKeyLabel'),
        apiKeyInput: document.getElementById('apiKeyInput'),
        toggleApiKeyVisibility: document.getElementById('toggleApiKeyVisibility'),
        eyeIcon: document.getElementById('eyeIcon'),
        modelNameInput: document.getElementById('modelNameInput'),
        modelLabel: document.getElementById('modelLabel'),
        modelHelperText: document.getElementById('modelHelperText'),
        testApiKeyBtn: document.getElementById('testApiKeyBtn'),
        saveApiKeyBtn: document.getElementById('saveApiKeyBtn'),
        keyValidationMsg: document.getElementById('keyValidationMsg'),

        // History & Stats
        refreshHistoryBtn: document.getElementById('refreshHistoryBtn'),
        clearHistoryBtn: document.getElementById('clearHistoryBtn'),
        historyTableBody: document.getElementById('historyTableBody'),
        statTotalScans: document.getElementById('statTotalScans'),
        statFakeCount: document.getElementById('statFakeCount'),
        statRealCount: document.getElementById('statRealCount'),
        statAvgScore: document.getElementById('statAvgScore'),

        // Compare Tab
        loadSampleABtn: document.getElementById('loadSampleABtn'),
        loadSampleBBtn: document.getElementById('loadSampleBBtn'),
        compareTitleA: document.getElementById('compareTitleA'),
        compareTextA: document.getElementById('compareTextA'),
        compareTitleB: document.getElementById('compareTitleB'),
        compareTextB: document.getElementById('compareTextB'),
        analyzeCompareBtnA: document.getElementById('analyzeCompareBtnA'),
        analyzeCompareBtnB: document.getElementById('analyzeCompareBtnB'),
        compareResultA: document.getElementById('compareResultA'),
        compareResultB: document.getElementById('compareResultB'),

        // IEEE Dataset Explorer Elements
        dsTotalArticles: document.getElementById('dsTotalArticles'),
        dsFakeArticles: document.getElementById('dsFakeArticles'),
        dsRealArticles: document.getElementById('dsRealArticles'),
        dsAvgWords: document.getElementById('dsAvgWords'),
        datasetSearchInput: document.getElementById('datasetSearchInput'),
        datasetCategoryFilter: document.getElementById('datasetCategoryFilter'),
        datasetLabelFilter: document.getElementById('datasetLabelFilter'),
        datasetCardsContainer: document.getElementById('datasetCardsContainer'),
        prevPageBtn: document.getElementById('prevPageBtn'),
        nextPageBtn: document.getElementById('nextPageBtn'),
        pageIndicator: document.getElementById('pageIndicator'),

        toastContainer: document.getElementById('toastContainer')
    };

    // =========================================================================
    // Theme Management
    // =========================================================================
    const savedTheme = localStorage.getItem('veritas_theme') || 'dark';
    document.documentElement.setAttribute('data-theme', savedTheme);
    updateThemeIcon(savedTheme);

    elements.themeToggleBtn.addEventListener('click', () => {
        const currentTheme = document.documentElement.getAttribute('data-theme');
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        document.documentElement.setAttribute('data-theme', newTheme);
        localStorage.setItem('veritas_theme', newTheme);
        updateThemeIcon(newTheme);
    });

    function updateThemeIcon(theme) {
        if (theme === 'dark') {
            elements.themeIcon.setAttribute('data-lucide', 'sun');
        } else {
            elements.themeIcon.setAttribute('data-lucide', 'moon');
        }
        if (window.lucide) window.lucide.createIcons();
    }

    // =========================================================================
    // Tab Navigation
    // =========================================================================
    elements.navTabs.forEach(tab => {
        tab.addEventListener('click', () => {
            const targetTab = tab.getAttribute('data-tab');
            elements.navTabs.forEach(t => t.classList.remove('active'));
            elements.tabPanels.forEach(p => p.classList.remove('active'));

            tab.classList.add('active');
            const panel = document.getElementById(`tab-${targetTab}`);
            if (panel) panel.classList.add('active');
            state.activeTab = targetTab;

            if (targetTab === 'history') {
                loadHistoryAndStats();
            } else if (targetTab === 'dataset') {
                loadDatasetStats();
                loadDatasetItems();
            }
        });
    });

    // =========================================================================
    // Input Mode Toggles (Text vs URL)
    // =========================================================================
    elements.modeTextBtn.addEventListener('click', () => {
        elements.modeTextBtn.classList.add('active');
        elements.modeUrlBtn.classList.remove('active');
        elements.textModeForm.classList.remove('hidden');
        elements.urlModeForm.classList.add('hidden');
        state.inputMode = 'text';
    });

    elements.modeUrlBtn.addEventListener('click', () => {
        elements.modeUrlBtn.classList.add('active');
        elements.modeTextBtn.classList.remove('active');
        elements.urlModeForm.classList.remove('hidden');
        elements.textModeForm.classList.add('hidden');
        state.inputMode = 'url';
    });

    // Character counter
    elements.contentInput.addEventListener('input', () => {
        elements.charCount.textContent = elements.contentInput.value.length;
    });

    // Clear input
    elements.clearInputBtn.addEventListener('click', () => {
        elements.headlineInput.value = '';
        elements.contentInput.value = '';
        elements.urlInput.value = '';
        elements.charCount.textContent = '0';
        elements.resultsContainer.classList.add('hidden');
    });

    // =========================================================================
    // LLM Provider & Settings Modal
    // =========================================================================
    updateApiKeyBadge();

    // Provider select change handler
    elements.providerSelect.addEventListener('change', () => {
        applyProviderUi(elements.providerSelect.value);
    });

    function applyProviderUi(provider) {
        if (provider === 'gemini') {
            elements.baseUrlGroup.classList.add('hidden');
            elements.apiKeyLabel.textContent = 'Google Gemini API Key';
            elements.apiKeyInput.placeholder = 'AIzaSy...';
            elements.modelNameInput.value = 'gemini-2.5-flash';
            elements.modelLabel.textContent = 'Gemini Model';
            elements.modelHelperText.innerHTML = 'Supported: <code>gemini-2.5-flash</code>, <code>gemini-2.0-flash</code>, <code>gemini-1.5-flash</code>';
            elements.providerInfoText.innerHTML = `
                <strong>Google Gemini Configuration:</strong>
                <p>Uses your Google AI Studio API key for multimodal and structured factual verification.</p>
                <a href="https://aistudio.google.com/app/apikey" target="_blank" rel="noopener" class="external-link">Get a free Gemini API key <i data-lucide="external-link"></i></a>
            `;
        } else if (provider === 'freellmapi') {
            elements.baseUrlGroup.classList.remove('hidden');
            elements.baseUrlInput.value = state.baseUrl || 'https://api.freellmapi.com/v1';
            elements.apiKeyLabel.textContent = 'FreeLLMAPI Key';
            elements.apiKeyInput.placeholder = 'Enter your FreeLLMAPI key or proxy key...';
            elements.modelNameInput.value = state.model || 'llama-3.1-70b';
            elements.modelLabel.textContent = 'Model Identifier';
            elements.modelHelperText.innerHTML = 'Popular free models: <code>llama-3.1-70b</code>, <code>mistral-7b-instruct</code>, <code>gpt-3.5-turbo</code>';
            elements.providerInfoText.innerHTML = `
                <strong>FreeLLMAPI Configuration:</strong>
                <p>Insert your FreeLLMAPI key. It routes through OpenAI-compatible free LLM tiers to perform deep claim-by-claim forensic audits.</p>
            `;
        } else { // openai_compatible
            elements.baseUrlGroup.classList.remove('hidden');
            elements.baseUrlInput.value = state.baseUrl || 'https://openrouter.ai/api/v1';
            elements.apiKeyLabel.textContent = 'OpenAI-Compatible API Key';
            elements.apiKeyInput.placeholder = 'sk-... or your custom API key';
            elements.modelNameInput.value = state.model || 'meta-llama/llama-3.1-70b-instruct';
            elements.modelLabel.textContent = 'Model Identifier';
            elements.modelHelperText.innerHTML = 'Custom models e.g. <code>meta-llama/llama-3.1-70b-instruct</code>, <code>gpt-4o-mini</code>, etc.';
            elements.providerInfoText.innerHTML = `
                <strong>Custom OpenAI-Compatible API:</strong>
                <p>Connect any standard OpenAI-compatible gateway (OpenRouter, GroqCloud, Ollama, vLLM).</p>
            `;
        }
        if (window.lucide) window.lucide.createIcons();
    }

    elements.openSettingsBtn.addEventListener('click', () => {
        elements.providerSelect.value = state.provider;
        elements.apiKeyInput.value = state.apiKey;
        elements.baseUrlInput.value = state.baseUrl;
        elements.modelNameInput.value = state.model;
        elements.keyValidationMsg.textContent = '';
        applyProviderUi(state.provider);
        elements.settingsModal.classList.remove('hidden');
    });

    elements.closeSettingsBtn.addEventListener('click', () => {
        elements.settingsModal.classList.add('hidden');
    });

    elements.settingsModal.addEventListener('click', (e) => {
        if (e.target === elements.settingsModal) {
            elements.settingsModal.classList.add('hidden');
        }
    });

    elements.toggleApiKeyVisibility.addEventListener('click', () => {
        const isPassword = elements.apiKeyInput.type === 'password';
        elements.apiKeyInput.type = isPassword ? 'text' : 'password';
        elements.eyeIcon.setAttribute('data-lucide', isPassword ? 'eye-off' : 'eye');
        if (window.lucide) window.lucide.createIcons();
    });

    // Test API Key
    elements.testApiKeyBtn.addEventListener('click', async () => {
        const key = elements.apiKeyInput.value.trim();
        const provider = elements.providerSelect.value;
        const baseUrl = elements.baseUrlInput.value.trim();
        const model = elements.modelNameInput.value.trim();

        if (!key) {
            elements.keyValidationMsg.innerHTML = '<span class="text-danger">Please enter an API key first.</span>';
            return;
        }

        elements.keyValidationMsg.innerHTML = `<span class="text-accent"><i data-lucide="loader"></i> Testing connection to ${provider.toUpperCase()}...</span>`;
        if (window.lucide) window.lucide.createIcons();

        try {
            const res = await fetch('/api/verify-key', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                    api_key: key,
                    provider: provider,
                    base_url: baseUrl,
                    model: model
                })
            });
            const data = await res.json();
            if (data.valid) {
                elements.keyValidationMsg.innerHTML = `<span class="text-success">✓ ${data.message}</span>`;
                showToast('API credentials verified successfully!', 'success');
            } else {
                elements.keyValidationMsg.innerHTML = `<span class="text-danger">✗ ${data.message}</span>`;
                showToast('Verification failed.', 'error');
            }
        } catch (err) {
            elements.keyValidationMsg.innerHTML = `<span class="text-danger">Connection error: ${err.message}</span>`;
        }
    });

    // Save API Key & Credentials
    elements.saveApiKeyBtn.addEventListener('click', async () => {
        const key = elements.apiKeyInput.value.trim();
        const provider = elements.providerSelect.value;
        const baseUrl = elements.baseUrlInput.value.trim();
        const model = elements.modelNameInput.value.trim();

        state.apiKey = key;
        state.provider = provider;
        state.baseUrl = baseUrl;
        state.model = model;

        localStorage.setItem('veritas_llm_api_key', key);
        localStorage.setItem('veritas_llm_provider', provider);
        localStorage.setItem('veritas_llm_base_url', baseUrl);
        localStorage.setItem('veritas_llm_model', model);

        updateApiKeyBadge();

        // Also persist to backend .env
        if (key) {
            try {
                await fetch('/api/save-key', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        api_key: key,
                        provider: provider,
                        base_url: baseUrl,
                        model: model
                    })
                });
            } catch (e) {
                console.log("Could not write to .env:", e);
            }
        }

        elements.settingsModal.classList.add('hidden');
        showToast('LLM credentials successfully saved!', 'success');
    });

    function updateApiKeyBadge() {
        if (state.apiKey && state.apiKey.length > 5) {
            const provName = state.provider === 'freellmapi' ? 'FreeLLMAPI' : 
                             state.provider === 'gemini' ? 'Gemini' : 'LLM';
            elements.apiKeyStatusBadge.textContent = `${provName} Active`;
            elements.apiKeyStatusBadge.className = 'api-status-badge active';
            elements.engineStatus.innerHTML = `
                <span class="status-dot"></span>
                <span class="status-label">BERT + ${provName} Live</span>
            `;
        } else {
            elements.apiKeyStatusBadge.textContent = 'Local BERT';
            elements.apiKeyStatusBadge.className = 'api-status-badge';
            elements.engineStatus.innerHTML = `
                <span class="status-dot"></span>
                <span class="status-label">Local BERT Active</span>
            `;
        }
    }

    // =========================================================================
    // Preset Samples Loader
    // =========================================================================
    async function loadSamples() {
        try {
            const res = await fetch('/api/samples');
            const data = await res.json();
            if (data.samples && data.samples.length > 0) {
                elements.sampleChips.innerHTML = '';
                data.samples.forEach(sample => {
                    const btn = document.createElement('button');
                    btn.className = `chip ${sample.expected === 'REAL' ? 'chip-real' : 'chip-fake'}`;
                    btn.innerHTML = `
                        <i data-lucide="${sample.expected === 'REAL' ? 'check-circle' : 'alert-circle'}"></i>
                        <span>${sample.category}: ${sample.expected}</span>
                    `;
                    btn.addEventListener('click', () => {
                        elements.modeTextBtn.click();
                        elements.headlineInput.value = sample.title;
                        elements.contentInput.value = sample.text;
                        elements.charCount.textContent = sample.text.length;
                        showToast(`Loaded sample: "${sample.title.slice(0, 35)}..."`, 'info');
                    });
                    elements.sampleChips.appendChild(btn);
                });
                if (window.lucide) window.lucide.createIcons();
            }
        } catch (err) {
            elements.sampleChips.innerHTML = '<span class="text-muted">Presets offline</span>';
        }
    }
    loadSamples();

    // =========================================================================
    // Main Analysis Trigger
    // =========================================================================
    elements.analyzeBtn.addEventListener('click', () => runAnalysis());

    async function runAnalysis() {
        const isUrlMode = state.inputMode === 'url';
        const url = elements.urlInput.value.trim();
        const headline = elements.headlineInput.value.trim();
        const content = elements.contentInput.value.trim();
        const enableDeep = elements.deepCheckCheckbox.checked;

        if (isUrlMode) {
            if (!url) {
                showToast('Please enter an article URL.', 'error');
                return;
            }
        } else {
            if (!content && !headline) {
                showToast('Please enter headline or article content to analyze.', 'error');
                return;
            }
        }

        // Show loading state
        elements.resultsContainer.classList.add('hidden');
        elements.loadingState.classList.remove('hidden');
        elements.analyzeBtn.disabled = true;

        try {
            let res, data;
            const headers = { 'Content-Type': 'application/json' };
            if (state.apiKey) {
                headers['X-API-Key'] = state.apiKey;
            }

            if (isUrlMode) {
                res = await fetch('/api/analyze-url', {
                    method: 'POST',
                    headers: headers,
                    body: JSON.stringify({
                        url: url,
                        api_key: state.apiKey,
                        provider: state.provider,
                        base_url: state.baseUrl,
                        model: state.model,
                        enable_deep_factcheck: enableDeep
                    })
                });
            } else {
                res = await fetch('/api/analyze', {
                    method: 'POST',
                    headers: headers,
                    body: JSON.stringify({
                        title: headline,
                        content: content,
                        api_key: state.apiKey,
                        provider: state.provider,
                        base_url: state.baseUrl,
                        model: state.model,
                        enable_deep_factcheck: enableDeep
                    })
                });
            }

            if (!res.ok) {
                const errData = await res.json();
                throw new Error(errData.detail || 'Analysis request failed.');
            }

            data = await res.json();
            state.currentAnalysis = data;
            renderResults(data);

        } catch (err) {
            showToast(`Analysis Error: ${err.message}`, 'error');
        } finally {
            elements.loadingState.classList.add('hidden');
            elements.analyzeBtn.disabled = false;
        }
    }

    // =========================================================================
    // Render Results View
    // =========================================================================
    function renderResults(data) {
        const verdict = data.verdict; // 'REAL', 'FAKE', or 'UNCERTAIN'
        const score = data.credibility_score;
        const nlp = data.nlp_metrics || {};
        const gemini = data.gemini_audit;

        // 1. Verdict Banner Styling
        elements.verdictBanner.className = 'verdict-banner';
        if (verdict === 'REAL') {
            elements.verdictBanner.classList.add('verdict-real');
            elements.verdictIcon.innerHTML = '<i data-lucide="shield-check"></i>';
            elements.verdictBadge.textContent = 'LIKELY AUTHENTIC NEWS';
            elements.verdictHeadline.textContent = 'High Journalistic Credibility & Neutral Framing';
            elements.verdictSubtext.textContent = 'The language is factual, objective, and aligns with standard verified journalistic reporting.';
        } else if (verdict === 'FAKE') {
            elements.verdictBanner.classList.add('verdict-fake');
            elements.verdictIcon.innerHTML = '<i data-lucide="shield-alert"></i>';
            elements.verdictBadge.textContent = 'DECEPTIVE / HIGH MISINFORMATION RISK';
            elements.verdictHeadline.textContent = 'Substantial Sensationalism or Fact Discrepancies';
            elements.verdictSubtext.textContent = 'Contains extreme hyperbole, unverified conspiracy phrasing, clickbait traps, or debunked claims.';
        } else {
            elements.verdictBanner.classList.add('verdict-uncertain');
            elements.verdictIcon.innerHTML = '<i data-lucide="help-circle"></i>';
            elements.verdictBadge.textContent = 'UNCERTAIN / MIXED CREDIBILITY';
            elements.verdictHeadline.textContent = 'Mixed Signals or Insufficient Attributed Facts';
            elements.verdictSubtext.textContent = 'Some claims appear plausible, but lack sufficient neutral citations or contain selective presentation.';
        }

        elements.credibilityScoreVal.textContent = `${score}%`;

        // 2. Metrics Progress Bars
        const sens = nlp.sensationalism_score || 0;
        elements.sensationalismVal.textContent = `${sens}%`;
        elements.sensationalismBar.style.width = `${sens}%`;
        elements.sensationalismDesc.textContent = sens > 40 ? 'High sensationalist wording' : 'Objective and calm vocabulary';

        const clickbait = nlp.clickbait_score || 0;
        elements.clickbaitVal.textContent = `${clickbait}%`;
        elements.clickbaitBar.style.width = `${clickbait}%`;
        elements.clickbaitDesc.textContent = clickbait > 35 ? 'Aggressive engagement-bait hooks' : 'No clickbait framing detected';

        const bias = nlp.bias_score || 0;
        elements.biasVal.textContent = `${bias}%`;
        elements.biasBar.style.width = `${bias}%`;
        elements.biasDesc.textContent = bias > 30 ? 'Strong ideological / conspiracy markers' : 'Low bias indicators';

        const attr = nlp.source_attribution_score || 50;
        elements.attributionVal.textContent = `${attr}%`;
        elements.attributionBar.style.width = `${attr}%`;
        elements.attributionDesc.textContent = attr > 60 ? 'Cites verified institutions/journals' : 'Vague or ghost attribution';

        // 3. XAI Highlighter
        renderXaiText(elements.contentInput.value || (data.url_details ? data.url_details.content : ''), nlp.highlight_tokens || []);

        // 4. LLM Deep AI Card
        if (gemini && gemini.enabled) {
            elements.geminiAuditCard.classList.remove('hidden');
            if (gemini.model_used) {
                elements.geminiModelBadge.textContent = gemini.model_used;
            } else {
                elements.geminiModelBadge.textContent = state.provider.toUpperCase();
            }
            let claimsHtml = '';
            if (gemini.claims_analysis && gemini.claims_analysis.length > 0) {
                claimsHtml = `
                    <table class="claims-table">
                        <thead>
                            <tr>
                                <th>Extracted Claim</th>
                                <th>Status</th>
                                <th>Fact-Check Context</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${gemini.claims_analysis.map(c => `
                                <tr>
                                    <td><strong>"${c.claim}"</strong></td>
                                    <td>
                                        <span class="claim-status-badge ${
                                            c.status === 'VERIFIED' ? 'status-verified' : 
                                            c.status === 'DISPROVEN' ? 'status-disproven' : 'status-unsubstantiated'
                                        }">${c.status}</span>
                                    </td>
                                    <td>${c.explanation}</td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                `;
            }

            let fallaciesHtml = '';
            if (gemini.logical_fallacies && gemini.logical_fallacies.length > 0) {
                fallaciesHtml = `
                    <div style="margin-top: 1rem;">
                        <strong style="font-size: 0.85rem; color: var(--text-secondary);">Logical Fallacies Detected:</strong><br>
                        ${gemini.logical_fallacies.map(f => `<span class="fallacy-tag">${f}</span>`).join('')}
                    </div>
                `;
            }

            elements.geminiAuditContent.innerHTML = `
                <p style="font-size: 0.95rem; margin-bottom: 0.85rem; line-height: 1.7;">
                    <strong>Executive Forensic Summary:</strong> ${gemini.detailed_reasoning || gemini.summary_verdict}
                </p>
                ${claimsHtml}
                ${fallaciesHtml}
            `;

            // Update Google search query button
            if (gemini.cross_reference_search_query) {
                elements.googleVerifyBtn.href = `https://www.google.com/search?q=${encodeURIComponent(gemini.cross_reference_search_query)}`;
            } else {
                elements.googleVerifyBtn.href = `https://www.google.com/search?q=${encodeURIComponent(data.title || 'news fact check')}`;
            }
        } else {
            elements.geminiAuditCard.classList.remove('hidden');
            elements.geminiModelBadge.textContent = 'Standby';
            elements.geminiAuditContent.innerHTML = `
                <p style="font-size: 0.9rem; color: var(--text-secondary);">
                    <em>Deep AI verification is paused. Add your FreeLLMAPI, Gemini, or OpenAI API key in <strong>Settings (⚙️)</strong> to unlock claim-by-claim forensic audits, logical fallacy analysis, and automated cross-referencing.</em>
                </p>
            `;
            elements.googleVerifyBtn.href = `https://www.google.com/search?q=${encodeURIComponent(data.title || 'news fact check')}`;
        }

        // Show container
        elements.resultsContainer.classList.remove('hidden');
        if (window.lucide) window.lucide.createIcons();
        elements.resultsContainer.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }

    // =========================================================================
    // Explainable AI (XAI) Token Highlighter
    // =========================================================================
    function renderXaiText(rawText, tokens) {
        if (!rawText) {
            elements.highlightedTextBox.textContent = 'No text provided.';
            elements.flagsSummary.innerHTML = '';
            return;
        }

        let highlighted = escapeHtml(rawText);

        tokens.forEach(token => {
            const term = escapeHtml(token.term);
            const regex = new RegExp(`\\b(${term})\\b`, 'gi');
            highlighted = highlighted.replace(regex, (match) => {
                return `<span class="hl-token hl-${token.category}" title="${token.description}">${match}</span>`;
            });
        });

        elements.highlightedTextBox.innerHTML = highlighted;

        // Render flags chips
        if (tokens.length === 0) {
            elements.flagsSummary.innerHTML = '<span class="text-muted" style="font-size: 0.8rem;">✓ No suspicious manipulation patterns or hyperbole detected.</span>';
        } else {
            elements.flagsSummary.innerHTML = tokens.map(t => `
                <span class="flag-chip">
                    <strong>${t.term}</strong>: ${t.description}
                </span>
            `).join('');
        }
    }

    function escapeHtml(str) {
        return str
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#039;');
    }

    // =========================================================================
    // Copy & Export Features
    // =========================================================================
    elements.copyReportBtn.addEventListener('click', () => {
        if (!state.currentAnalysis) return;
        const d = state.currentAnalysis;
        const text = `
=== VeritasAI Misinformation Audit Report ===
Title: ${d.title || 'Untitled'}
Verdict: ${d.verdict} (Truth Score: ${d.credibility_score}%)
Confidence: ${d.confidence * 100}%
Sensationalism: ${d.nlp_metrics.sensationalism_score}%
Clickbait Level: ${d.nlp_metrics.clickbait_score}%
Source Attribution: ${d.nlp_metrics.source_attribution_score}%
Model Used: ${d.bert_details.model_used}
Generated by VeritasAI Fake News Platform
=============================================
        `.trim();

        navigator.clipboard.writeText(text).then(() => {
            showToast('Audit report copied to clipboard!', 'success');
        });
    });

    elements.downloadJsonBtn.addEventListener('click', () => {
        if (!state.currentAnalysis) return;
        const blob = new Blob([JSON.stringify(state.currentAnalysis, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `veritas_audit_${Date.now()}.json`;
        a.click();
        URL.revokeObjectURL(url);
        showToast('JSON report downloaded.', 'success');
    });

    // =========================================================================
    // Side-by-Side Comparison Tab
    // =========================================================================
    elements.loadSampleABtn.addEventListener('click', () => {
        elements.compareTitleA.value = 'SHOCKING: Boiling Lemon Peels Cures All Cancers, Big Pharma Secret Exposed!';
        elements.compareTextA.value = 'What happens next will blow your mind! Insiders reveal that boiling lemon peels completely destroys 100% of cancer tumors in just 48 hours. The mainstream media is silent!';
    });

    elements.loadSampleBBtn.addEventListener('click', () => {
        elements.compareTitleB.value = 'Oncology Clinical Trials Evaluate Dietary Flavonoid Compounds in Cancer Research';
        elements.compareTextB.value = 'Researchers at the National Cancer Institute have published findings examining how citrus polyphenols interact with cellular metabolic pathways, emphasizing that human clinical trials remain ongoing.';
    });

    elements.analyzeCompareBtnA.addEventListener('click', async () => {
        runSideCompare('A', elements.compareTitleA.value, elements.compareTextA.value, elements.compareResultA);
    });

    elements.analyzeCompareBtnB.addEventListener('click', async () => {
        runSideCompare('B', elements.compareTitleB.value, elements.compareTextB.value, elements.compareResultB);
    });

    async function runSideCompare(side, title, text, resultEl) {
        if (!text) {
            showToast(`Please enter text for Version ${side}`, 'error');
            return;
        }
        resultEl.innerHTML = '<span class="text-accent">Analyzing...</span>';
        resultEl.classList.remove('hidden');

        try {
            const res = await fetch('/api/analyze', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ title, content: text, enable_deep_factcheck: false })
            });
            const data = await res.json();
            resultEl.innerHTML = `
                <div style="margin-top: 1rem; padding: 1rem; border-radius: var(--radius-sm); background: var(--bg-input); border-left: 4px solid ${
                    data.verdict === 'REAL' ? 'var(--success)' : 'var(--danger)'
                }">
                    <strong>Verdict: ${data.verdict}</strong>
                    <div style="font-size: 1.5rem; font-weight: 800; font-family: var(--font-mono); margin: 0.35rem 0;">
                        ${data.credibility_score}%
                    </div>
                    <small style="color: var(--text-secondary);">
                        Sensationalism: ${data.nlp_metrics.sensationalism_score}% | Clickbait: ${data.nlp_metrics.clickbait_score}%
                    </small>
                </div>
            `;
        } catch (e) {
            resultEl.innerHTML = `<span class="text-danger">Error: ${e.message}</span>`;
        }
    }

    // =========================================================================
    // Analytics & History
    // =========================================================================
    async function loadHistoryAndStats() {
        try {
            // Stats
            const statsRes = await fetch('/api/stats');
            const stats = await statsRes.json();
            
            elements.statTotalScans.textContent = stats.total_scans;
            elements.statFakeCount.textContent = stats.fake_count;
            elements.statRealCount.textContent = stats.real_count;
            elements.statAvgScore.textContent = `${stats.avg_credibility_score}%`;

            renderHistoryChart(stats);

            // History table
            const histRes = await fetch('/api/history?limit=30');
            const hist = await histRes.json();
            renderHistoryTable(hist.history || []);

        } catch (e) {
            console.error('Failed to load history:', e);
        }
    }

    elements.refreshHistoryBtn.addEventListener('click', loadHistoryAndStats);

    elements.clearHistoryBtn.addEventListener('click', async () => {
        if (!confirm('Are you sure you want to clear all scan history?')) return;
        await fetch('/api/history/clear', { method: 'POST' });
        loadHistoryAndStats();
        showToast('History cleared successfully.', 'info');
    });

    function renderHistoryTable(records) {
        if (records.length === 0) {
            elements.historyTableBody.innerHTML = `
                <tr><td colspan="7" class="text-center text-muted">No scan records found. Run an analysis!</td></tr>
            `;
            return;
        }

        elements.historyTableBody.innerHTML = records.map(r => `
            <tr>
                <td style="font-size: 0.75rem; color: var(--text-muted); font-family: var(--font-mono);">${r.created_at || 'Just now'}</td>
                <td style="max-width: 280px; font-weight: 600;">
                    <div style="white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">
                        ${r.title || r.content_preview || 'Untitled'}
                    </div>
                </td>
                <td><span style="font-size: 0.75rem; text-transform: uppercase;">${r.source_type}</span></td>
                <td>
                    <span class="claim-status-badge ${
                        r.verdict === 'REAL' ? 'status-verified' : 
                        r.verdict === 'FAKE' ? 'status-disproven' : 'status-unsubstantiated'
                    }">${r.verdict}</span>
                </td>
                <td style="font-family: var(--font-mono); font-weight: 700;">${r.credibility_score}%</td>
                <td style="font-size: 0.75rem; color: var(--text-muted);">${r.model_used || 'BERT'}</td>
                <td>
                    <button class="btn-text text-danger" onclick="window.deleteRecord(${r.id})">
                        Delete
                    </button>
                </td>
            </tr>
        `).join('');
    }

    window.deleteRecord = async (id) => {
        await fetch(`/api/history/${id}`, { method: 'DELETE' });
        loadHistoryAndStats();
        showToast('Record deleted.', 'info');
    };

    function renderHistoryChart(stats) {
        if (!window.Chart) return;
        const ctx = document.getElementById('historyChart').getContext('2d');
        if (state.historyChart) {
            state.historyChart.destroy();
        }

        state.historyChart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Verified Authentic', 'Deceptive / Fake', 'Uncertain / Mixed'],
                datasets: [{
                    data: [
                        stats.real_count || 0,
                        stats.fake_count || 0,
                        stats.uncertain_count || 0
                    ],
                    backgroundColor: ['#10b981', '#ef4444', '#f59e0b'],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            color: document.documentElement.getAttribute('data-theme') === 'dark' ? '#9ca3af' : '#475569'
                        }
                    }
                }
            }
        });
    }

    // =========================================================================
    // =========================================================================
    // IEEE DataPort Dataset Explorer
    // =========================================================================
    async function loadDatasetStats() {
        try {
            const res = await fetch('/api/dataset/stats');
            const data = await res.json();
            if (elements.dsTotalArticles) elements.dsTotalArticles.textContent = data.total_articles;
            if (elements.dsFakeArticles) elements.dsFakeArticles.textContent = data.fake_count;
            if (elements.dsRealArticles) elements.dsRealArticles.textContent = data.real_count;
            if (elements.dsAvgWords) elements.dsAvgWords.textContent = data.average_word_length;
        } catch (e) {
            console.error('Failed to load dataset stats:', e);
        }
    }

    async function loadDatasetItems() {
        if (!elements.datasetCardsContainer) return;
        elements.datasetCardsContainer.innerHTML = '<div class="text-center text-muted" style="grid-column: 1 / -1; padding: 2rem;">Loading IEEE DataPort items...</div>';

        const params = new URLSearchParams({
            page: state.datasetPage,
            limit: state.datasetLimit,
            category: state.datasetCategory,
            label: state.datasetLabel
        });
        if (state.datasetSearch) {
            params.append('search', state.datasetSearch);
        }

        try {
            const res = await fetch(`/api/dataset/items?${params.toString()}`);
            const data = await res.json();

            // Populate category filter if needed
            if (data.available_categories && elements.datasetCategoryFilter && elements.datasetCategoryFilter.options.length <= 1) {
                data.available_categories.forEach(cat => {
                    const opt = document.createElement('option');
                    opt.value = cat;
                    opt.textContent = cat;
                    elements.datasetCategoryFilter.appendChild(opt);
                });
            }

            // Render cards
            if (!data.items || data.items.length === 0) {
                elements.datasetCardsContainer.innerHTML = `
                    <div class="text-center text-muted" style="grid-column: 1 / -1; padding: 3rem;">
                        <i data-lucide="inbox" style="width: 36px; height: 36px; margin-bottom: 0.5rem;"></i>
                        <p>No IEEE news items matched your search filter.</p>
                    </div>
                `;
                if (window.lucide) window.lucide.createIcons();
                if (elements.pageIndicator) elements.pageIndicator.textContent = 'Page 0 of 0';
                if (elements.prevPageBtn) elements.prevPageBtn.disabled = true;
                if (elements.nextPageBtn) elements.nextPageBtn.disabled = true;
                return;
            }

            elements.datasetCardsContainer.innerHTML = data.items.map(item => `
                <div class="glass-card dataset-card ${item.label === 1 ? 'card-real' : 'card-fake'}">
                    <div>
                        <div class="dataset-card-header">
                            <span class="dataset-category-tag">${escapeHtml(item.category)}</span>
                            <span class="claim-status-badge ${item.label === 1 ? 'status-verified' : 'status-disproven'}">
                                ${item.label === 1 ? 'VERIFIED REAL' : 'DECEPTIVE FAKE'}
                            </span>
                        </div>
                        <h3 class="dataset-card-title">${escapeHtml(item.title)}</h3>
                        <p class="dataset-card-snippet">${escapeHtml(item.text)}</p>
                    </div>
                    <div class="dataset-card-footer">
                        <span><i data-lucide="bookmark" style="width: 12px; height: 12px; vertical-align: middle;"></i> ${escapeHtml(item.source)}</span>
                        <button class="btn btn-primary btn-sm" onclick="window.testIeeeSample('${item.id}')">
                            <i data-lucide="search-check"></i> Test in Detector
                        </button>
                    </div>
                </div>
            `).join('');

            if (window.lucide) window.lucide.createIcons();

            // Store current items in state for quick retrieval
            state.cachedDatasetItems = data.items;

            // Pagination
            if (elements.pageIndicator) elements.pageIndicator.textContent = `Page ${data.page} of ${data.total_pages}`;
            if (elements.prevPageBtn) elements.prevPageBtn.disabled = data.page <= 1;
            if (elements.nextPageBtn) elements.nextPageBtn.disabled = data.page >= data.total_pages;

        } catch (e) {
            elements.datasetCardsContainer.innerHTML = `<div class="text-danger" style="grid-column: 1 / -1; padding: 2rem;">Error loading items: ${e.message}</div>`;
        }
    }

    // Global helper to load IEEE sample into Live Detector
    window.testIeeeSample = (id) => {
        const item = (state.cachedDatasetItems || []).find(x => x.id === id);
        if (!item) return;

        // Switch to detector tab
        const detectorTabBtn = document.querySelector('.nav-tab[data-tab="detector"]');
        if (detectorTabBtn) detectorTabBtn.click();

        elements.modeTextBtn.click();
        elements.headlineInput.value = item.title;
        elements.contentInput.value = item.text;
        elements.charCount.textContent = item.text.length;

        showToast(`Loaded IEEE article: "${item.title.slice(0, 30)}..."`, 'info');
        const inputCard = document.querySelector('.input-card');
        if (inputCard) inputCard.scrollIntoView({ behavior: 'smooth' });
    };

    if (elements.datasetSearchInput) {
        let debounceTimer;
        elements.datasetSearchInput.addEventListener('input', () => {
            clearTimeout(debounceTimer);
            debounceTimer = setTimeout(() => {
                state.datasetSearch = elements.datasetSearchInput.value.trim();
                state.datasetPage = 1;
                loadDatasetItems();
            }, 300);
        });
    }

    if (elements.datasetCategoryFilter) {
        elements.datasetCategoryFilter.addEventListener('change', () => {
            state.datasetCategory = elements.datasetCategoryFilter.value;
            state.datasetPage = 1;
            loadDatasetItems();
        });
    }

    if (elements.datasetLabelFilter) {
        elements.datasetLabelFilter.addEventListener('change', () => {
            state.datasetLabel = elements.datasetLabelFilter.value;
            state.datasetPage = 1;
            loadDatasetItems();
        });
    }

    if (elements.prevPageBtn) {
        elements.prevPageBtn.addEventListener('click', () => {
            if (state.datasetPage > 1) {
                state.datasetPage--;
                loadDatasetItems();
            }
        });
    }

    if (elements.nextPageBtn) {
        elements.nextPageBtn.addEventListener('click', () => {
            state.datasetPage++;
            loadDatasetItems();
        });
    }

    // Notification Toast System
    // =========================================================================
    function showToast(message, type = 'info') {
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        const icon = type === 'success' ? 'check-circle' : type === 'error' ? 'alert-octagon' : 'info';
        toast.innerHTML = `<i data-lucide="${icon}"></i> <span>${message}</span>`;
        elements.toastContainer.appendChild(toast);
        if (window.lucide) window.lucide.createIcons();

        setTimeout(() => {
            toast.style.opacity = '0';
            toast.style.transform = 'translateY(10px)';
            toast.style.transition = 'all 0.3s ease';
            setTimeout(() => toast.remove(), 300);
        }, 3500);
    }
});

