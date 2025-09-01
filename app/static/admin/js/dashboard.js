/**
 * Dashboard principale - Gestione navigazione e inizializzazione
 */

// Page templates cache
let pageTemplatesLoaded = false;

/**
 * Navigazione principale
 */
function navigate(page, tab = null) {
    State.currentPage = page;
    State.currentTab = tab;
    
    // Aggiorna UI navigazione
    document.querySelectorAll('.sidebar-link').forEach(link => {
        link.classList.remove('active');
        if (link.dataset.page === page) {
            link.classList.add('active');
        }
    });
    
    // Gestisci accordion
    const accordionMap = {
        'overview': null,
        'business-config': 'business-accordion',
        'business-costs': 'business-accordion',
        'business-simulator': 'business-accordion',
        'business-scenarios': 'business-accordion',
        'billing-provider': 'billing-accordion',
        'billing-plans': 'billing-accordion',
        'billing-credits': 'billing-accordion',
        'billing-checkout': 'billing-accordion',
        'observe-ai': 'observability-accordion',
        'observe-credits': 'observability-accordion',
        'observe-rollouts': 'observability-accordion',
        'config-flows': 'config-accordion',
        'config-security': 'config-accordion',
        'config-setup': 'config-accordion',
        'testing': null
    };
    
    const targetAccordion = accordionMap[page];
    document.querySelectorAll('details').forEach(details => {
        if (targetAccordion && details.id === targetAccordion) {
            details.open = true;
        }
    });
    
    loadPage(page, tab);
}

/**
 * Carica una pagina
 */
function loadPage(page, tab = null) {
    Utils.showLoading();
    
    // Prima carica i templates se non già caricati
    if (!pageTemplatesLoaded) {
        loadPageTemplates().then(() => {
            pageTemplatesLoaded = true;
            renderPage(page, tab);
        });
    } else {
        renderPage(page, tab);
    }
}

/**
 * Carica i page templates dinamicamente
 */
async function loadPageTemplates() {
    try {
        const response = await fetch('/static/admin/js/page-templates.js');
        const script = await response.text();
        eval(script);
        return true;
    } catch (error) {
        console.error('Failed to load page templates:', error);
        // Fallback: carica template di base
        window.pageTemplates = {
            overview: () => '<h1>Overview</h1><p>Loading...</p>',
            'business-config': () => '<h1>Business Config</h1><p>Loading...</p>',
            'business-costs': () => '<h1>App Affordability</h1><p>Loading...</p>',
            'billing-plans': () => '<h1>Billing Plans</h1><p>Loading...</p>'
        };
    }
}

/**
 * Renderizza la pagina
 */
function renderPage(page, tab) {
    setTimeout(() => {
        const template = window.pageTemplates?.[page];
        if (template) {
            document.getElementById('main-content').innerHTML = template();
            
            // Auto-switch to tab if specified
            if (tab) {
                setTimeout(() => switchTab(tab), 100);
            } else {
                // Activate first tab by default
                const firstTab = document.querySelector('.tab[data-tab]');
                if (firstTab) {
                    switchTab(firstTab.dataset.tab);
                }
            }
            
            // Load page-specific data
            loadPageData(page);
        }
        Utils.showLoading(false);
    }, 300);
}

/**
 * Cambia tab
 */
function switchTab(tabName) {
    // Update tab states
    document.querySelectorAll('.tab').forEach(tab => {
        tab.classList.remove('tab-active');
        if (tab.dataset.tab === tabName) {
            tab.classList.add('tab-active');
        }
    });
    
    // Show/hide tab contents
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.remove('active');
    });
    const activeContent = document.getElementById(`tab-${tabName}`);
    if (activeContent) {
        activeContent.classList.add('active');
    }
    
    State.currentTab = tabName;
}

/**
 * Setup tab handlers
 */
function setupTabHandlers() {
    document.addEventListener('click', (e) => {
        // Check if clicked element or its parent is a tab
        const tab = e.target.closest('.tab[data-tab]');
        if (tab) {
            e.preventDefault();
            switchTab(tab.dataset.tab);
        }
    });
}

/**
 * Carica dati specifici della pagina
 */
async function loadPageData(page) {
    switch (page) {
        case 'overview':
            await loadOverviewMetrics();
            break;
        case 'business-config':
            await PricingComponent.loadPricingConfig();
            break;
        case 'business-costs':
            await PricingComponent.loadAppAffordability();
            break;
        case 'business-simulator':
            await PricingComponent.loadPricingConfig();
            break;
        case 'billing-provider':
            await BillingComponent.loadBillingConfig();
            break;
        case 'billing-plans':
            await BillingComponent.loadPlansData();
            break;
        case 'billing-credits':
            await BillingComponent.loadCreditsConfig();
            break;
        case 'billing-checkout':
            await BillingComponent.loadCheckoutData();
            break;
    }
}

/**
 * Carica metriche overview
 */
async function loadOverviewMetrics() {
    try {
        // Check if credentials are configured
        if (!State.token && !State.adminKey) {
            document.getElementById('metric-users').textContent = '-';
            document.getElementById('metric-credits').textContent = '-';
            document.getElementById('metric-revenue').textContent = '-';
            const setupAlert = document.getElementById('setup-alert');
            if (setupAlert) setupAlert.style.display = 'block';
            return;
        }
        
        // Load user count
        try {
            const users = await API.get('/core/v1/admin/users?limit=1');
            const totalUsers = users.count || users.total || 0;
            document.getElementById('metric-users').textContent = totalUsers.toString();
            
            if (totalUsers === 1 && users.users && users.users.length === 1) {
                const fullCount = await API.get('/core/v1/admin/users?limit=1000');
                document.getElementById('metric-users').textContent = (fullCount.count || 0).toString();
            }
        } catch (e) {
            document.getElementById('metric-users').textContent = 'N/A';
            console.error('Failed to load users:', e);
        }
        
        // Load pricing config
        try {
            const pricing = await API.get('/core/v1/admin/pricing/config');
            const revenue = pricing.monthly_revenue_target_usd || 0;
            document.getElementById('metric-revenue').textContent = Utils.formatCurrency(revenue);
        } catch (e) {
            if (e.message && e.message.includes('422')) {
                document.getElementById('metric-revenue').textContent = '$0';
                console.log('No pricing config found, using defaults');
            } else {
                document.getElementById('metric-revenue').textContent = 'N/A';
                console.error('Failed to load pricing:', e);
            }
        }
        
        // Load total credits
        try {
            const users = await API.get('/core/v1/admin/users?limit=1000');
            const totalCredits = users.users ? users.users.reduce((sum, u) => sum + (u.credits || 0), 0) : 0;
            document.getElementById('metric-credits').textContent = Utils.formatNumber(totalCredits);
        } catch (e) {
            document.getElementById('metric-credits').textContent = 'N/A';
            console.error('Failed to load credits:', e);
        }
        
        // Hide setup alert if configured
        if (State.token || State.adminKey) {
            const setupAlert = document.getElementById('setup-alert');
            if (setupAlert && !document.querySelector('#metric-users').textContent.includes('N/A')) {
                setupAlert.style.display = 'none';
            }
        }
    } catch (error) {
        console.error('Failed to load metrics:', error);
        const setupAlert = document.getElementById('setup-alert');
        if (setupAlert) setupAlert.style.display = 'block';
    }
}

/**
 * Quick Setup Modal
 */
function showQuickSetup() {
    const modal = document.createElement('div');
    modal.className = 'modal modal-open';
    modal.id = 'quick-setup-modal';
    modal.innerHTML = `
        <div class="modal-box max-w-2xl">
            <h3 class="font-bold text-lg mb-4">Quick Setup</h3>
            <div class="space-y-4">
                <div class="form-control">
                    <label class="label">
                        <span class="label-text">Authentication Method</span>
                    </label>
                    <select class="select select-bordered" id="quick-auth-method" onchange="toggleAuthFields()">
                        <option value="token">Bearer Token (JWT)</option>
                        <option value="admin-key">Admin Key</option>
                        <option value="both">Both</option>
                    </select>
                </div>
                
                <div class="form-control" id="quick-token-field">
                    <label class="label">
                        <span class="label-text">Bearer Token</span>
                    </label>
                    <input type="text" class="input input-bordered" id="quick-token" placeholder="eyJhbGciOi..." />
                </div>
                
                <div class="form-control" id="quick-admin-field" style="display: none;">
                    <label class="label">
                        <span class="label-text">Admin Key</span>
                    </label>
                    <input type="text" class="input input-bordered" id="quick-admin-key" placeholder="sk-..." />
                </div>
                
                <div class="form-control">
                    <label class="label">
                        <span class="label-text">Base URL</span>
                    </label>
                    <input type="text" class="input input-bordered" id="quick-base-url" value="${State.baseUrl}" />
                </div>
            </div>
            <div class="modal-action">
                <button class="btn" onclick="document.getElementById('quick-setup-modal').remove()">Cancel</button>
                <button class="btn btn-primary" onclick="saveQuickSetup()">Save & Apply</button>
            </div>
        </div>
        <div class="modal-backdrop" onclick="document.getElementById('quick-setup-modal').remove()"></div>
    `;
    document.body.appendChild(modal);
    
    // Pre-fill current values
    document.getElementById('quick-token').value = State.token;
    document.getElementById('quick-admin-key').value = State.adminKey;
    
    // Show correct fields based on current auth
    if (State.token && State.adminKey) {
        document.getElementById('quick-auth-method').value = 'both';
        toggleAuthFields();
    } else if (State.adminKey) {
        document.getElementById('quick-auth-method').value = 'admin-key';
        toggleAuthFields();
    }
}

window.toggleAuthFields = function() {
    const method = document.getElementById('quick-auth-method').value;
    document.getElementById('quick-token-field').style.display = 
        (method === 'token' || method === 'both') ? 'block' : 'none';
    document.getElementById('quick-admin-field').style.display = 
        (method === 'admin-key' || method === 'both') ? 'block' : 'none';
}

window.saveQuickSetup = function() {
    const method = document.getElementById('quick-auth-method').value;
    
    if (method === 'token' || method === 'both') {
        State.token = document.getElementById('quick-token').value.trim();
    } else {
        State.token = '';
    }
    
    if (method === 'admin-key' || method === 'both') {
        State.adminKey = document.getElementById('quick-admin-key').value.trim();
    } else {
        State.adminKey = '';
    }
    
    State.baseUrl = document.getElementById('quick-base-url').value.trim();
    State.save();
    
    document.getElementById('quick-setup-modal').remove();
    Utils.showToast('Configuration saved!', 'success');
    
    // Reload current page to apply new credentials
    loadPage(State.currentPage);
}

/**
 * Inizializzazione
 */
document.addEventListener('DOMContentLoaded', () => {
    // Auto-save admin key if not already saved
    if (State.adminKey && !localStorage.getItem('flowstarter_admin_key')) {
        State.save();
        console.log('Auto-saved admin key to localStorage');
    }
    
    // Debug state
    console.log('Dashboard initialized with state:', {
        hasToken: !!State.token,
        hasAdminKey: !!State.adminKey,
        baseUrl: State.baseUrl,
        appId: State.appId
    });
    
    // Set up navigation
    document.querySelectorAll('[data-page]').forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const page = link.dataset.page;
            const tab = link.dataset.tab;
            navigate(page, tab);
        });
    });
    
    // Set up tab handlers
    setupTabHandlers();
    
    // Bind global functions
    window.showQuickSetup = showQuickSetup;
    window.clearAllData = () => State.clear();
    
    // Bind component functions to window
    window.PricingComponent = PricingComponent;
    window.BillingComponent = BillingComponent;
    window.ObservabilityComponent = ObservabilityComponent;
    window.ConfigurationComponent = ConfigurationComponent;
    window.TestingComponent = TestingComponent;
    
    // Load initial page
    navigate('overview');
});
