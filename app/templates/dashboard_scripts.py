"""
Script JavaScript per la Dashboard Unificata.
Mantiene tutta la logica client-side in un formato modulare e mantenibile.
"""


def get_dashboard_scripts() -> str:
    """Ritorna tutti gli script JavaScript per la dashboard."""
    return f"""
    <script>
    // ===== CONFIGURAZIONE E UTILITIES =====
    {_get_config_utils()}
    
    // ===== NAVIGAZIONE E ROUTING =====
    {_get_navigation_scripts()}
    
    // ===== PAGINE DELLA DASHBOARD =====
    {_get_page_templates()}
    
    // ===== BUSINESS & PRICING =====
    {_get_business_pricing_scripts()}
    
    // ===== BILLING & PLANS =====
    {_get_billing_plans_scripts()}
    
    // ===== OBSERVABILITY =====
    {_get_observability_scripts()}
    
    // ===== CONFIGURATION =====
    {_get_configuration_scripts()}
    
    // ===== TESTING =====
    {_get_testing_scripts()}
    
    // ===== INIZIALIZZAZIONE =====
    {_get_initialization_scripts()}
    </script>
    """


def _get_config_utils() -> str:
    """Utilities di configurazione e helper functions."""
    return """
    // Base URL e autenticazione
    function getBase(){ 
        try{ 
            const raw=(document.getElementById('base')?.value||window.location.origin).trim(); 
            return raw.replace(/\/+$/,''); 
        }catch(_){ 
            return window.location.origin; 
        } 
    }
    
    function authHeaders(){ 
        const t=document.getElementById('token')?.value?.trim()||''; 
        const adm=document.getElementById('adm')?.value?.trim()||''; 
        const h={'Content-Type':'application/json'}; 
        if(t){ 
            try{ 
                const isJwt = t.split('.').length===3; 
                if(isJwt) h['Authorization']=`Bearer ${t}`; 
            }catch(_){ } 
        } 
        if(adm) h['X-Admin-Key']=adm; 
        return h; 
    }
    
    // Local storage management
    function saveLocalData() {
        const data = {
            base: document.getElementById('base')?.value || '',
            token: document.getElementById('token')?.value || '',
            adm: document.getElementById('adm')?.value || ''
        };
        localStorage.setItem('flowstarter_auth', JSON.stringify(data));
        showToast('Dati salvati localmente', 'success');
    }
    
    function loadLocalData() {
        try {
            const data = JSON.parse(localStorage.getItem('flowstarter_auth') || '{}');
            if (data.base) document.getElementById('base').value = data.base;
            if (data.token) document.getElementById('token').value = data.token;
            if (data.adm) document.getElementById('adm').value = data.adm;
        } catch (e) {
            console.error('Errore caricamento dati locali:', e);
        }
    }
    
    function clearLocalData() {
        if (confirm('Cancellare tutti i dati locali?')) {
            localStorage.removeItem('flowstarter_auth');
            localStorage.removeItem('flowstarter_base_url');
            location.reload();
        }
    }
    
    // Toast notifications
    function showToast(message, type = 'info') {
        const toast = document.createElement('div');
        toast.className = `alert alert-${type} fixed bottom-4 right-4 w-auto max-w-md z-50`;
        toast.innerHTML = `
            <span>${message}</span>
            <button class="btn btn-sm btn-ghost" onclick="this.parentElement.remove()">✕</button>
        `;
        document.body.appendChild(toast);
        setTimeout(() => toast.remove(), 5000);
    }
    
    // Make showToast available globally
    window.showToast = showToast;
    """


def _get_navigation_scripts() -> str:
    """Script per la navigazione tra pagine."""
    return """
    // Navigation state
    let currentPage = 'overview';
    
    // Page navigation
    function navigateTo(page) {
        console.log('Navigating to:', page);
        currentPage = page;
        
        // Update active states
        document.querySelectorAll('.sidebar-link').forEach(link => {
            if (link.dataset.page === page) {
                link.classList.add('active');
            } else {
                link.classList.remove('active');
            }
        });
        
        // Load page content
        const contentFn = window[`render_${page.replace(/-/g, '_')}`];
        if (contentFn) {
            document.getElementById('main-content').innerHTML = contentFn();
            
            // Execute page-specific initialization
            const initFn = window[`init_${page.replace(/-/g, '_')}`];
            if (initFn) {
                setTimeout(initFn, 50);
            }
        } else {
            document.getElementById('main-content').innerHTML = `
                <div class="alert alert-warning">
                    <i class="fas fa-exclamation-triangle"></i>
                    <span>Pagina "${page}" non ancora implementata</span>
                </div>
            `;
        }
        
        // Close mobile drawer
        document.getElementById('drawer-toggle').checked = false;
        
        // Update URL hash
        window.location.hash = page;
    }
    
    // Setup navigation listeners
    document.addEventListener('DOMContentLoaded', () => {
        // Link clicks
        document.querySelectorAll('[data-page]').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                navigateTo(link.dataset.page);
            });
        });
        
        // Load saved data
        loadLocalData();
        
        // Navigate to hash or default
        const hash = window.location.hash.slice(1);
        navigateTo(hash || 'overview');
    });
    
    // Handle browser back/forward
    window.addEventListener('hashchange', () => {
        const hash = window.location.hash.slice(1);
        if (hash && hash !== currentPage) {
            navigateTo(hash);
        }
    });
    """


def _get_page_templates() -> str:
    """Template HTML per le varie pagine."""
    return """
    // ===== OVERVIEW PAGE =====
    function render_overview() {
        return `
            <div class="space-y-6">
                <h1 class="text-3xl font-bold">Dashboard Overview</h1>
                
                <!-- Auth Configuration -->
                <div class="card bg-base-100 shadow-xl">
                    <div class="card-body">
                        <h2 class="card-title">
                            <i class="fas fa-key text-primary"></i>
                            Configurazione Autenticazione
                        </h2>
                        
                        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div class="form-control">
                                <label class="label">
                                    <span class="label-text">Base URL Core</span>
                                </label>
                                <input 
                                    id="base" 
                                    type="text" 
                                    placeholder="http://127.0.0.1:5050" 
                                    class="input input-bordered"
                                    onchange="saveLocalData()"
                                />
                            </div>
                            
                            <div class="form-control">
                                <label class="label">
                                    <span class="label-text">Bearer Token</span>
                                </label>
                                <input 
                                    id="token" 
                                    type="text" 
                                    placeholder="eyJhbGciOi..." 
                                    class="input input-bordered"
                                    onchange="saveLocalData()"
                                />
                            </div>
                            
                            <div class="form-control">
                                <label class="label">
                                    <span class="label-text">Admin Key (opzionale)</span>
                                </label>
                                <input 
                                    id="adm" 
                                    type="text" 
                                    placeholder="CORE_ADMIN_KEY" 
                                    class="input input-bordered"
                                    onchange="saveLocalData()"
                                />
                            </div>
                        </div>
                        
                        <div class="card-actions justify-end mt-4">
                            <button class="btn btn-primary" onclick="testConnection()">
                                <i class="fas fa-check"></i>
                                Test Connessione
                            </button>
                        </div>
                    </div>
                </div>
                
                <!-- Quick Stats -->
                <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div class="stat bg-base-100 shadow rounded-box">
                        <div class="stat-figure text-primary">
                            <i class="fas fa-users text-3xl"></i>
                        </div>
                        <div class="stat-title">Utenti Totali</div>
                        <div class="stat-value" id="total-users">-</div>
                    </div>
                    
                    <div class="stat bg-base-100 shadow rounded-box">
                        <div class="stat-figure text-secondary">
                            <i class="fas fa-coins text-3xl"></i>
                        </div>
                        <div class="stat-title">Crediti Utilizzati</div>
                        <div class="stat-value" id="total-credits">-</div>
                    </div>
                    
                    <div class="stat bg-base-100 shadow rounded-box">
                        <div class="stat-figure text-accent">
                            <i class="fas fa-dollar-sign text-3xl"></i>
                        </div>
                        <div class="stat-title">Revenue</div>
                        <div class="stat-value" id="total-revenue">-</div>
                    </div>
                </div>
                
                <!-- Quick Actions -->
                <div class="card bg-base-100 shadow-xl">
                    <div class="card-body">
                        <h2 class="card-title">Quick Actions</h2>
                        <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
                            <button class="btn btn-outline" onclick="navigateTo('billing-plans')">
                                <i class="fas fa-list"></i>
                                Gestisci Piani
                            </button>
                            <button class="btn btn-outline" onclick="navigateTo('billing-checkout')">
                                <i class="fas fa-shopping-cart"></i>
                                Crea Checkout
                            </button>
                            <button class="btn btn-outline" onclick="navigateTo('observability-ai')">
                                <i class="fas fa-chart-bar"></i>
                                Vedi Usage
                            </button>
                            <button class="btn btn-outline" onclick="navigateTo('config-flows')">
                                <i class="fas fa-stream"></i>
                                Config Flows
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }
    
    function init_overview() {
        // Carica statistiche
        loadDashboardStats();
    }
    
    async function testConnection() {
        try {
            const base = getBase();
            const headers = authHeaders();
            const response = await fetch(`${base}/core/v1/health`, { headers });
            
            if (response.ok) {
                showToast('Connessione OK!', 'success');
            } else {
                showToast(`Errore connessione: ${response.status}`, 'error');
            }
        } catch (e) {
            showToast(`Errore: ${e.message}`, 'error');
        }
    }
    
    async function loadDashboardStats() {
        // Placeholder - implementare chiamate API reali
        document.getElementById('total-users').textContent = '42';
        document.getElementById('total-credits').textContent = '125,430';
        document.getElementById('total-revenue').textContent = '$1,234';
    }
    """


def _get_business_pricing_scripts() -> str:
    """Script per la sezione Business & Pricing."""
    # Continuerò nell'implementazione successiva per mantenere il file gestibile
    return """
    // Business & Pricing scripts - Da implementare
    """


def _get_billing_plans_scripts() -> str:
    """Script per la gestione dei piani di abbonamento con bottoni Save per-riga."""
    from .dashboard_pages import get_billing_plans_page, get_billing_plans_scripts
    
    return f"""
    // ===== BILLING PLANS PAGE =====
    function render_billing_plans() {{
        return `{get_billing_plans_page()}`;
    }}
    
    {get_billing_plans_scripts()}
    """


def _get_observability_scripts() -> str:
    """Script per la sezione Observability."""
    return """
    // Observability scripts - Da implementare
    """


def _get_configuration_scripts() -> str:
    """Script per la sezione Configuration."""
    return """
    // Configuration scripts - Da implementare
    """


def _get_testing_scripts() -> str:
    """Script per la sezione Testing."""
    return """
    // Testing scripts - Da implementare
    """


def _get_initialization_scripts() -> str:
    """Script di inizializzazione finale."""
    return """
    // Initialize on load
    console.log('Dashboard initialized');
    """
