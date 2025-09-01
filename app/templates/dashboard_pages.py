"""
Template HTML per le pagine della dashboard.
Contiene tutto il codice HTML/JS estratto dal documento markdown originale.
"""


def get_billing_plans_page() -> str:
    """Renderizza la pagina Subscription Plans con i bottoni Save per-riga."""
    return """
    <div class="mb-6">
        <h1 class="text-3xl font-bold">Subscription Plans</h1>
        <p class="text-base-content/60">Gestisci piani di abbonamento e pricing</p>
    </div>
    
    <!-- Auth Config -->
    <div class="card bg-base-100 shadow-xl mb-6">
        <div class="card-body">
            <h2 class="card-title">Configurazione</h2>
            <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div class="form-control">
                    <label class="label"><span class="label-text">Base URL Core</span></label>
                    <input id="base" type="text" placeholder="http://127.0.0.1:5050" class="input input-bordered" />
                </div>
                <div class="form-control">
                    <label class="label"><span class="label-text">Bearer Token</span></label>
                    <input id="token" type="text" placeholder="eyJhbGciOi..." class="input input-bordered" />
                </div>
                <div class="form-control">
                    <label class="label"><span class="label-text">Admin Key</span></label>
                    <input id="adm" type="text" placeholder="CORE_ADMIN_KEY" class="input input-bordered" />
                </div>
            </div>
        </div>
    </div>
    
    <!-- Tabs -->
    <div role="tablist" class="tabs tabs-boxed mb-6">
        <a role="tab" class="tab tab-active" onclick="showTab('db-plans')">Piani (DB)</a>
        <a role="tab" class="tab" onclick="showTab('config-plans')">Piani Configurabili</a>
        <a role="tab" class="tab" onclick="showTab('quick-setup')">Quick Setup</a>
        <a role="tab" class="tab" onclick="showTab('simulator')">Simulatore</a>
    </div>
    
    <!-- Tab: Piani DB -->
    <div id="tab-db-plans" class="tab-content" style="display: block;">
        <div class="card bg-base-100 shadow-xl">
            <div class="card-body">
                <div class="flex justify-between items-center mb-4">
                    <h3 class="text-xl font-semibold">Piani Subscription (Database)</h3>
                    <div>
                        <button class="btn btn-sm btn-primary" onclick="loadDbPlans()">🔄 Carica</button>
                        <button class="btn btn-sm btn-success" onclick="saveDbPlans()">💾 Salva tutti</button>
                    </div>
                </div>
                
                <div class="overflow-x-auto">
                    <table id="db_plans_table" class="table table-zebra">
                        <thead>
                            <tr>
                                <th>Plan ID</th>
                                <th>Nome</th>
                                <th>Tipo</th>
                                <th>Prezzo/mese</th>
                                <th>Crediti/mese</th>
                                <th>Rollout %</th>
                                <th>Max Rollover</th>
                                <th>Attivo</th>
                                <th>Azioni</th>
                            </tr>
                        </thead>
                        <tbody>
                            <!-- Popolato dinamicamente -->
                        </tbody>
                    </table>
                </div>
                
                <button class="btn btn-sm btn-primary mt-4" onclick="addDbPlanRow()">
                    <i class="fas fa-plus"></i> Aggiungi Piano
                </button>
            </div>
        </div>
    </div>
    
    <!-- Tab: Piani Configurabili -->
    <div id="tab-config-plans" class="tab-content" style="display: none;">
        <div class="card bg-base-100 shadow-xl">
            <div class="card-body">
                <div class="flex justify-between items-center mb-4">
                    <h3 class="text-xl font-semibold">Piani Configurabili (Config)</h3>
                    <div>
                        <button class="btn btn-sm btn-primary" onclick="loadPlans()">🔄 Carica</button>
                        <button class="btn btn-sm btn-success" onclick="savePlans()">💾 Salva tutti</button>
                    </div>
                </div>
                
                <div class="overflow-x-auto">
                    <table id="plans_table" class="table table-zebra">
                        <thead>
                            <tr>
                                <th>Plan ID</th>
                                <th>Nome</th>
                                <th>Tipo</th>
                                <th>Variant ID</th>
                                <th>Prezzo USD</th>
                                <th>Crediti</th>
                                <th>Azioni</th>
                            </tr>
                        </thead>
                        <tbody>
                            <!-- Popolato dinamicamente -->
                        </tbody>
                    </table>
                </div>
                
                <button class="btn btn-sm btn-primary mt-4" onclick="addPlanRow()">
                    <i class="fas fa-plus"></i> Aggiungi Piano
                </button>
            </div>
        </div>
    </div>
    
    <!-- Tab: Quick Setup -->
    <div id="tab-quick-setup" class="tab-content" style="display: none;">
        <div class="card bg-base-100 shadow-xl">
            <div class="card-body">
                <h3 class="text-xl font-semibold mb-4">Quick Setup Wizard</h3>
                
                <div class="space-y-6">
                    <div>
                        <h4 class="font-semibold mb-2">1. Configura Provider</h4>
                        <div class="grid grid-cols-2 gap-4">
                            <input type="text" id="qs_store_id" placeholder="Store ID (es: 199395)" class="input input-bordered" />
                            <label class="label cursor-pointer">
                                <span class="label-text">Test Mode</span>
                                <input type="checkbox" id="qs_test_mode" class="checkbox" />
                            </label>
                        </div>
                    </div>
                    
                    <div>
                        <h4 class="font-semibold mb-2">2. Definisci Piani Base</h4>
                        <div class="space-y-2">
                            <div class="grid grid-cols-4 gap-2">
                                <input placeholder="starter" class="input input-sm input-bordered" />
                                <input placeholder="Starter" class="input input-sm input-bordered" />
                                <input placeholder="$5" type="number" class="input input-sm input-bordered" />
                                <input placeholder="100 crediti" type="number" class="input input-sm input-bordered" />
                            </div>
                            <div class="grid grid-cols-4 gap-2">
                                <input placeholder="pro" class="input input-sm input-bordered" />
                                <input placeholder="Professional" class="input input-sm input-bordered" />
                                <input placeholder="$19" type="number" class="input input-sm input-bordered" />
                                <input placeholder="500 crediti" type="number" class="input input-sm input-bordered" />
                            </div>
                        </div>
                    </div>
                    
                    <button class="btn btn-primary w-full" onclick="runQuickSetup()">
                        <i class="fas fa-magic"></i> Configura Tutto Automaticamente
                    </button>
                </div>
            </div>
        </div>
    </div>
    
    <!-- Tab: Simulatore -->
    <div id="tab-simulator" class="tab-content" style="display: none;">
        <div class="card bg-base-100 shadow-xl">
            <div class="card-body">
                <h3 class="text-xl font-semibold mb-4">Simulatore Prezzi</h3>
                
                <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                        <h4 class="font-semibold mb-2">Parametri</h4>
                        <div class="space-y-3">
                            <div>
                                <label class="label">
                                    <span class="label-text">Piano</span>
                                </label>
                                <select id="sim_plan" class="select select-bordered w-full">
                                    <option value="">Seleziona piano...</option>
                                </select>
                            </div>
                            <div>
                                <label class="label">
                                    <span class="label-text">Utenti target</span>
                                </label>
                                <input type="number" id="sim_users" value="100" class="input input-bordered w-full" />
                            </div>
                            <div>
                                <label class="label">
                                    <span class="label-text">Conversione %</span>
                                </label>
                                <input type="number" id="sim_conversion" value="2" step="0.1" class="input input-bordered w-full" />
                            </div>
                        </div>
                        <button class="btn btn-primary w-full mt-4" onclick="runSimulation()">
                            Simula
                        </button>
                    </div>
                    
                    <div>
                        <h4 class="font-semibold mb-2">Risultati</h4>
                        <div id="sim_results" class="bg-base-200 rounded-lg p-4">
                            <p class="text-center text-base-content/60">Esegui una simulazione per vedere i risultati</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    """


def get_billing_plans_scripts() -> str:
    """Script JavaScript per la gestione dei piani con bottoni Save per-riga."""
    return """
    // ===== CONFIGURAZIONE =====
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
    
    // ===== TAB MANAGEMENT =====
    function showTab(tabName) {
        // Hide all tabs
        document.querySelectorAll('.tab-content').forEach(tab => {
            tab.style.display = 'none';
        });
        
        // Show selected tab
        document.getElementById(`tab-${tabName}`).style.display = 'block';
        
        // Update tab buttons
        document.querySelectorAll('.tab').forEach(tab => {
            tab.classList.remove('tab-active');
        });
        event.target.classList.add('tab-active');
    }
    
    // ===== PIANI DB (con bottoni Save per-riga) =====
    function addDbPlanRow(id='', name='', type='subscription', price='', credits='', rollout='100', rollover='', active=true){
        const tbody = document.querySelector('#db_plans_table tbody');
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td><input value="${id}" placeholder="starter" class="input input-sm input-bordered"/></td>
            <td><input value="${name}" placeholder="Starter" class="input input-sm input-bordered"/></td>
            <td>
                <select class="select select-sm select-bordered">
                    <option value="subscription" ${type==='subscription'?'selected':''}>Subscription</option>
                    <option value="pay_as_go" ${type==='pay_as_go'?'selected':''}>Pay-as-you-go</option>
                </select>
            </td>
            <td><input type="number" step="0.01" value="${price}" placeholder="19.00" class="input input-sm input-bordered"/></td>
            <td><input type="number" step="1" value="${credits}" placeholder="1000" class="input input-sm input-bordered"/></td>
            <td><input type="number" step="0.01" value="${rollout}" placeholder="100" class="input input-sm input-bordered"/></td>
            <td><input type="number" step="1" value="${rollover}" placeholder="2000" class="input input-sm input-bordered"/></td>
            <td style="text-align:center"><input type="checkbox" ${active? 'checked':''} class="checkbox"/></td>
            <td>
                <button class="btn btn-xs btn-success" onclick="saveDbPlanRow(this)">💾 Save</button>
                <button class="btn btn-xs btn-error" onclick="this.closest('tr').remove()">🗑</button>
            </td>
        `;
        tbody.appendChild(tr);
    }
    
    async function saveDbPlanRow(btn) {
        const tr = btn.closest('tr');
        const inputs = tr.querySelectorAll('input');
        const sel = tr.querySelector('select');
        
        const plan = {
            id: inputs[0].value.trim(),
            name: inputs[1].value.trim(),
            type: sel.value,
            price_per_month: parseFloat(inputs[2].value)||0,
            credits_per_month: parseInt(inputs[3].value)||0,
            rollout_percentage: parseFloat(inputs[4].value)||100,
            max_credits_rollover: parseInt(inputs[5].value)||0,
            is_active: inputs[6].checked
        };
        
        if(!plan.id){ 
            showToast('Inserisci un Plan ID', 'warning');
            return;
        }
        
        try {
            const base = getBase();
            const headers = authHeaders();
            const response = await fetch(`${base}/core/v1/admin/subscription-plans`, {
                method: 'PUT',
                headers: headers,
                body: JSON.stringify({ plans: [plan] })
            });
            
            if(response.ok){
                btn.textContent = '✅ Saved';
                setTimeout(() => { btn.textContent = '💾 Save'; }, 1500);
                showToast(`Piano "${plan.name}" salvato!`, 'success');
            } else {
                const error = await response.text();
                showToast(`Errore: ${error}`, 'error');
            }
        } catch(e) {
            showToast(`Errore di connessione: ${e.message}`, 'error');
        }
    }
    
    function readDbPlans(){
        const rows = Array.from(document.querySelectorAll('#db_plans_table tbody tr'));
        return rows.map(r => {
            const inputs = r.querySelectorAll('input');
            const sel = r.querySelector('select');
            return {
                id: inputs[0].value.trim(),
                name: inputs[1].value.trim(),
                type: sel.value,
                price_per_month: parseFloat(inputs[2].value)||0,
                credits_per_month: parseInt(inputs[3].value)||0,
                rollout_percentage: parseFloat(inputs[4].value)||100,
                max_credits_rollover: parseInt(inputs[5].value)||0,
                is_active: inputs[6].checked
            };
        });
    }
    
    function setDbPlans(plans){
        const tbody = document.querySelector('#db_plans_table tbody');
        tbody.innerHTML='';
        (plans||[]).forEach(p => addDbPlanRow(
            p.id,
            p.name,
            p.type||'subscription',
            p.price_per_month||0,
            p.credits_per_month||0,
            p.rollout_percentage||100,
            p.max_credits_rollover||0,
            p.is_active !== false
        ));
    }
    
    async function loadDbPlans(){
        try {
            const base = getBase();
            const headers = authHeaders();
            const response = await fetch(`${base}/core/v1/admin/subscription-plans`, { headers });
            const data = await response.json();
            setDbPlans(data.plans || []);
            showToast('Piani caricati dal database', 'success');
        } catch(e) {
            showToast(`Errore caricamento: ${e.message}`, 'error');
        }
    }
    
    async function saveDbPlans(){
        const plans = readDbPlans();
        if(!plans.length){
            showToast('Nessun piano da salvare', 'warning');
            return;
        }
        
        try {
            const base = getBase();
            const headers = authHeaders();
            const response = await fetch(`${base}/core/v1/admin/subscription-plans`, {
                method: 'PUT',
                headers: headers,
                body: JSON.stringify({ plans })
            });
            
            if(response.ok){
                showToast(`${plans.length} piani salvati!`, 'success');
            } else {
                const error = await response.text();
                showToast(`Errore: ${error}`, 'error');
            }
        } catch(e) {
            showToast(`Errore di connessione: ${e.message}`, 'error');
        }
    }
    
    // ===== PIANI CONFIGURABILI (con bottoni Save per-riga) =====
    function addPlanRow(id='', name='', type='subscription', variant='', price='', credits=''){
        const tbody = document.querySelector('#plans_table tbody');
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td><input value="${id}" placeholder="starter" class="input input-sm input-bordered"/></td>
            <td><input value="${name}" placeholder="Starter Plan" class="input input-sm input-bordered"/></td>
            <td>
                <select class="select select-sm select-bordered">
                    <option value="subscription" ${type==='subscription'?'selected':''}>Subscription</option>
                    <option value="one_time" ${type==='one_time'?'selected':''}>One-time</option>
                </select>
            </td>
            <td><input value="${variant}" placeholder="935638" class="input input-sm input-bordered"/></td>
            <td><input type="number" step="0.01" value="${price}" placeholder="19.00" class="input input-sm input-bordered"/></td>
            <td><input type="number" step="1" value="${credits}" placeholder="1000" class="input input-sm input-bordered"/></td>
            <td>
                <button class="btn btn-xs btn-success" onclick="savePlanRow(this)">💾 Save</button>
                <button class="btn btn-xs btn-error" onclick="this.closest('tr').remove()">🗑</button>
            </td>
        `;
        tbody.appendChild(tr);
    }
    
    async function savePlanRow(btn) {
        const tr = btn.closest('tr');
        const inputs = tr.querySelectorAll('input');
        const sel = tr.querySelector('select');
        const type = sel.value;
        
        const plan = {
            id: inputs[0].value.trim(),
            name: inputs[1].value.trim(),
            type: type,
            variant_id: inputs[2].value.trim(),
            price_usd: parseFloat(inputs[3].value)||0,
            credits: parseInt(inputs[4].value)||0
        };
        
        if(type === 'subscription'){
            plan.credits_per_month = plan.credits;
        }
        
        if(!plan.id || !plan.variant_id){
            showToast('Plan ID e Variant ID sono obbligatori', 'warning');
            return;
        }
        
        try {
            const base = getBase();
            const headers = authHeaders();
            
            // Prima carica la config esistente
            const getResp = await fetch(`${base}/core/v1/admin/billing/config`, { headers });
            const cfg = await getResp.json();
            const conf = cfg?.config || {};
            const plans = Array.isArray(conf.plans) ? conf.plans.slice() : [];
            
            // Aggiorna o aggiungi il piano
            const idx = plans.findIndex(p => p.id === plan.id);
            if(idx >= 0) {
                plans[idx] = plan;
            } else {
                plans.push(plan);
            }
            
            conf.plans = plans;
            
            // Salva la config aggiornata
            const putResp = await fetch(`${base}/core/v1/admin/billing/config`, {
                method: 'PUT',
                headers: headers,
                body: JSON.stringify(conf)
            });
            
            if(putResp.ok){
                btn.textContent = '✅ Saved';
                setTimeout(() => { btn.textContent = '💾 Save'; }, 1500);
                showToast(`Piano "${plan.name}" salvato!`, 'success');
            } else {
                const error = await putResp.text();
                showToast(`Errore: ${error}`, 'error');
            }
        } catch(e) {
            showToast(`Errore di connessione: ${e.message}`, 'error');
        }
    }
    
    function readPlans(){
        const rows = Array.from(document.querySelectorAll('#plans_table tbody tr'));
        return rows.map(r => {
            const inputs = r.querySelectorAll('input');
            const sel = r.querySelector('select');
            const type = sel.value;
            const plan = {
                id: inputs[0].value.trim(),
                name: inputs[1].value.trim(),
                type: type,
                variant_id: inputs[2].value.trim(),
                price_usd: parseFloat(inputs[3].value)||0,
                credits: parseInt(inputs[4].value)||0
            };
            if(type === 'subscription'){
                plan.credits_per_month = plan.credits;
            }
            return plan;
        });
    }
    
    function setPlans(plans){
        const tbody = document.querySelector('#plans_table tbody');
        tbody.innerHTML='';
        (plans||[]).forEach(p => addPlanRow(
            p.id,
            p.name,
            p.type||'subscription',
            p.variant_id||'',
            p.price_usd||0,
            p.credits||p.credits_per_month||0
        ));
    }
    
    async function loadPlans(){
        try {
            const base = getBase();
            const headers = authHeaders();
            const response = await fetch(`${base}/core/v1/admin/billing/config`, { headers });
            const data = await response.json();
            const plans = data?.config?.plans || [];
            setPlans(plans);
            showToast('Piani caricati dalla configurazione', 'success');
        } catch(e) {
            showToast(`Errore caricamento: ${e.message}`, 'error');
        }
    }
    
    async function savePlans(){
        const plans = readPlans();
        if(!plans.length){
            showToast('Nessun piano da salvare', 'warning');
            return;
        }
        
        try {
            const base = getBase();
            const headers = authHeaders();
            
            // Carica config esistente
            const getResp = await fetch(`${base}/core/v1/admin/billing/config`, { headers });
            const cfg = await getResp.json();
            const conf = cfg?.config || {};
            
            // Aggiorna piani
            conf.plans = plans;
            
            // Salva
            const putResp = await fetch(`${base}/core/v1/admin/billing/config`, {
                method: 'PUT',
                headers: headers,
                body: JSON.stringify(conf)
            });
            
            if(putResp.ok){
                showToast(`${plans.length} piani salvati!`, 'success');
            } else {
                const error = await putResp.text();
                showToast(`Errore: ${error}`, 'error');
            }
        } catch(e) {
            showToast(`Errore di connessione: ${e.message}`, 'error');
        }
    }
    
    // ===== QUICK SETUP =====
    async function runQuickSetup() {
        showToast('Quick setup in sviluppo...', 'info');
    }
    
    // ===== SIMULATORE =====
    async function runSimulation() {
        showToast('Simulatore in sviluppo...', 'info');
    }
    
    // ===== INIZIALIZZAZIONE PAGINA =====
    function init_billing_plans() {
        // Carica dati autenticazione salvati
        try {
            const savedBase = localStorage.getItem('flowstarter_base_url');
            if(savedBase) document.getElementById('base').value = savedBase;
            
            const authData = JSON.parse(localStorage.getItem('flowstarter_auth') || '{}');
            if(authData.token) document.getElementById('token').value = authData.token;
            if(authData.adm) document.getElementById('adm').value = authData.adm;
        } catch(e) {}
        
        // Carica piani iniziali
        loadDbPlans();
        loadPlans();
    }
    """
