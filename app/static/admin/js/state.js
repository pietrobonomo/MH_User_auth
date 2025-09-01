/**
 * Gestione stato globale della dashboard
 */
const State = {
    // Dati autenticazione
    token: localStorage.getItem('flowstarter_token') || '',
    adminKey: localStorage.getItem('flowstarter_admin_key') || '',
    baseUrl: localStorage.getItem('flowstarter_base_url') || window.location.origin,
    
    // Stato applicazione
    appId: 'default',
    currentPage: 'overview',
    currentTab: null,
    
    // Dati configurabili
    configurablePlans: JSON.parse(localStorage.getItem('flowstarter_configurable_plans') || '{}'),
    
    // Metodi
    save() {
        localStorage.setItem('flowstarter_token', this.token);
        localStorage.setItem('flowstarter_admin_key', this.adminKey);
        localStorage.setItem('flowstarter_base_url', this.baseUrl);
        localStorage.setItem('flowstarter_configurable_plans', JSON.stringify(this.configurablePlans));
    },
    
    clear() {
        if (confirm('Sei sicuro di voler cancellare tutti i dati salvati?')) {
            localStorage.clear();
            window.location.reload();
        }
    },
    
    getBase() {
        const raw = (this.baseUrl || window.location.origin).trim();
        return raw.replace(/\/+$/, '');
    },
    
    getAuthHeaders() {
        const headers = { 'Content-Type': 'application/json' };
        if (this.token) {
            const isJwt = this.token.split('.').length === 3;
            if (isJwt) headers['Authorization'] = `Bearer ${this.token}`;
        }
        if (this.adminKey) headers['X-Admin-Key'] = this.adminKey;
        return headers;
    }
};
