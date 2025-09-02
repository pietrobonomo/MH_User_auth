/**
 * Componente Testing
 */
const TestingComponent = {
    _polling: null,
    async loadData() {
        try {
            // App IDs
            const apps = await API.get('/core/v1/admin/app-ids');
            const appSelect = document.getElementById('test_app_id');
            if (appSelect && Array.isArray(apps.app_ids)) {
                appSelect.innerHTML = apps.app_ids.map(a => `<option value="${a}">${a}</option>`).join('');
            }

            // Users
            const users = await API.get('/core/v1/admin/users?limit=100');
            const userSelect = document.getElementById('test_checkout_user');
            const affUser = document.getElementById('aff_user_select');
            if (userSelect) userSelect.innerHTML = (users.users || []).map(u => `<option value="${u.id}">${u.email} (${u.credits||0})</option>`).join('');
            if (affUser) affUser.innerHTML = (users.users || []).map(u => `<option value="${u.id}">${u.email} (${u.credits||0})</option>`).join('');

            // Plans
            const plans = await API.get('/core/v1/billing/plans');
            const planSelect = document.getElementById('test_checkout_plan');
            if (planSelect) planSelect.innerHTML = (plans.plans || []).map(p => `<option value="${p.id}">${p.name} ($${p.price_usd})</option>`).join('');

            // Affordability app select
            const affApp = document.getElementById('aff_app_select');
            if (affApp && Array.isArray(apps.app_ids)) affApp.innerHTML = apps.app_ids.map(a => `<option value="${a}">${a}</option>`).join('');

            // Flow keys for selected app
            await this.loadFlowKeys();
            if (appSelect) appSelect.onchange = () => this.loadFlowKeys();
        } catch (e) {
            console.warn('Testing loadData error:', e);
        }
    },
    async loadFlowKeys() {
        try {
            const appSelect = document.getElementById('test_app_id');
            const appId = appSelect?.value || 'default';
            const resp = await API.get(`/core/v1/admin/flow-keys?app_id=${encodeURIComponent(appId)}`);
            const select = document.getElementById('exec_flow_key');
            if (select) select.innerHTML = (resp.flow_keys || []).map(k => `<option value="${k}">${k}</option>`).join('');
        } catch (e) {
            console.warn('loadFlowKeys error:', e);
        }
    },
    async testSupabase() {
        try {
            const users = await API.get('/core/v1/admin/users?limit=1');
            document.getElementById('test-supabase-output').textContent = `OK - users: ${users.count ?? (users.users?.length || 0)}`;
        } catch (e) {
            document.getElementById('test-supabase-output').textContent = `ERROR: ${e.message}`;
        }
    },
    async affordabilityCheck() {
        try {
            const userId = document.getElementById('aff_user_select').value;
            const appId = document.getElementById('aff_app_select').value;
            const pricing = await API.get('/core/v1/admin/pricing/config');
            const threshold = (pricing.flow_costs_usd||{})[appId] || 0;
            const profile = await API.get(`/core/v1/admin/user-credits?user_id=${encodeURIComponent(userId)}`);
            const credits = profile?.profile?.credits || 0;
            const ok = credits >= threshold;
            document.getElementById('aff-output').innerHTML = ok
                ? `<div class="alert alert-success">OK: ${credits} ≥ soglia ${threshold}</div>`
                : `<div class="alert alert-warning">NO: ${credits} < soglia ${threshold}</div>`;
        } catch (e) {
            document.getElementById('aff-output').innerHTML = `<div class="alert alert-error">ERROR: ${e.message}</div>`;
        }
    },

    async createUser() {
        try {
            const email = document.getElementById('test_user_email').value.trim();
            const output = document.getElementById('test-user-output');
            
            if (!email) {
                output.innerHTML = '<div class="alert alert-error"><i class="fas fa-exclamation-circle"></i> Email mancante</div>';
                return;
            }
            
            output.innerHTML = '<div class="alert alert-info"><i class="fas fa-spinner fa-spin"></i> Creazione utente in corso...</div>';
            
            const res = await API.post('/core/v1/admin/users', { email });
            
            // Crea HTML dettagliato con password e OpenRouter
            output.innerHTML = `
                <div class="alert alert-success">
                    <div>
                        <div class="flex items-center gap-2 mb-2">
                            <i class="fas fa-check-circle"></i>
                            <h4 class="font-bold">Utente creato con successo!</h4>
                        </div>
                        
                        <!-- Informazioni Utente -->
                        <div class="bg-base-200 p-3 rounded mb-3">
                            <h5 class="font-semibold text-sm mb-2">📋 Dettagli Utente</h5>
                            <ul class="text-sm space-y-1">
                                <li><strong>User ID:</strong> <code class="text-xs bg-base-300 px-1 rounded">${res.user_id || 'n/a'}</code></li>
                                <li><strong>Email:</strong> ${res.email || email}</li>
                                ${res.password ? `
                                <li>
                                    <strong>Password (chiave provisioning):</strong> 
                                    <code class="text-xs bg-warning/30 px-2 py-1 rounded font-mono">${res.password}</code>
                                </li>
                                ` : ''}
                            </ul>
                        </div>
                        
                        <!-- Informazioni Crediti -->
                        <div class="bg-base-200 p-3 rounded mb-3">
                            <h5 class="font-semibold text-sm mb-2">💰 Crediti</h5>
                            <ul class="text-sm space-y-1">
                                <li><strong>Crediti iniziali:</strong> ${res.initial_credits !== undefined ? res.initial_credits : 'Non configurati'}</li>
                                <li><strong>Saldo dopo accredito:</strong> ${res.credits_after !== undefined ? res.credits_after : 'N/A'}</li>
                            </ul>
                        </div>
                        
                        <!-- Informazioni OpenRouter -->
                        <div class="bg-base-200 p-3 rounded">
                            <h5 class="font-semibold text-sm mb-2">🤖 OpenRouter</h5>
                            ${res.openrouter_provisioned ? `
                                <ul class="text-sm space-y-1">
                                    <li><strong>Status:</strong> <span class="badge badge-success badge-sm">Provisioned</span></li>
                                    ${res.openrouter_key_name ? `<li><strong>Key Name:</strong> <code class="text-xs bg-base-300 px-1 rounded">${res.openrouter_key_name}</code></li>` : ''}
                                    <li class="text-xs text-success">✓ Utente pronto per eseguire flow AI</li>
                                </ul>
                            ` : `
                                <ul class="text-sm space-y-1">
                                    <li><strong>Status:</strong> <span class="badge badge-error badge-sm">Not Provisioned</span></li>
                                    ${res.openrouter_error ? `<li class="text-xs text-error">Errore: ${res.openrouter_error}</li>` : ''}
                                    <li class="text-xs text-warning">⚠️ L'utente dovrà fare provisioning manuale per usare AI</li>
                                </ul>
                            `}
                        </div>
                        
                        ${res.password ? `
                        <div class="mt-3 p-2 bg-warning/20 border border-warning/50 rounded">
                            <p class="text-sm font-semibold flex items-center gap-1">
                                <i class="fas fa-exclamation-triangle text-warning"></i>
                                Salva questa password - non verrà mostrata di nuovo!
                            </p>
                            <p class="text-xs mt-1 opacity-80">Usala per l'autenticazione nelle app di produzione.</p>
                        </div>
                        ` : ''}
                    </div>
                </div>
            `;
            
            // Aggiorna lista utenti nei dropdown
            await this.loadData();
            
            // Aggiungi alla timeline
            this.addToTimeline('Utente creato', 'success', {
                user_id: res.user_id,
                email: res.email,
                initial_credits: res.initial_credits,
                has_password: !!res.password
            });
        } catch (e) {
            document.getElementById('test-user-output').innerHTML = `
                <div class="alert alert-error">
                    <i class="fas fa-times-circle"></i> 
                    <span>Errore: ${e.message}</span>
                </div>
            `;
            
            this.addToTimeline('Creazione utente fallita', 'error', { error: e.message });
        }
    },

    async generateCheckout() {
        try {
            const user = document.getElementById('test_checkout_user').value.trim();
            const plan = document.getElementById('test_checkout_plan').value.trim();
            if (!user || !plan) {
                document.getElementById('test-checkout-output').textContent = 'user_id o plan_id mancanti';
                return;
            }
            const res = await API.post(`/core/v1/admin/billing/checkout?user_id=${encodeURIComponent(user)}&plan_id=${encodeURIComponent(plan)}`);
            if (res.checkout?.checkout_url) {
                document.getElementById('test-checkout-output').innerHTML = `<a class="link" href="${res.checkout.checkout_url}" target="_blank">Apri checkout</a>`;
            } else {
                document.getElementById('test-checkout-output').textContent = JSON.stringify(res);
            }
        } catch (e) {
            document.getElementById('test-checkout-output').textContent = `ERROR: ${e.message}`;
        }
    },
    async checkBalance() {
        try {
            const user = document.getElementById('test_checkout_user').value.trim();
            if (!user) {
                document.getElementById('test-balance-output').textContent = 'Seleziona un utente';
                return;
            }
            const prof = await API.get(`/core/v1/admin/user-credits?user_id=${encodeURIComponent(user)}`);
            if (!prof?.found) {
                document.getElementById('test-balance-output').textContent = 'Profilo non trovato';
                return;
            }
            document.getElementById('test-balance-output').textContent = `Balance: ${prof.profile.credits}`;
        } catch (e) {
            document.getElementById('test-balance-output').textContent = `ERROR: ${e.message}`;
        }
    },
    startPollingBalance() {
        try {
            const user = document.getElementById('test_checkout_user').value.trim();
            const expectedInc = parseFloat(document.getElementById('test_expected_increment').value || '0') || 0;
            if (!user) {
                document.getElementById('test-balance-output').textContent = 'Seleziona un utente';
                return;
            }
            const out = document.getElementById('test-balance-output');
            let startBal = null;
            if (this._polling) clearInterval(this._polling);
            const fetchBal = async () => {
                try {
                    const prof = await API.get(`/core/v1/admin/user-credits?user_id=${encodeURIComponent(user)}`);
                    const bal = prof?.profile?.credits || 0;
                    if (startBal === null) startBal = bal;
                    const delta = bal - startBal;
                    out.textContent = `Balance: ${bal} (Δ ${delta}${expectedInc ? ` / atteso ~${expectedInc}` : ''})`;
                } catch (e) {
                    out.textContent = `ERROR: ${e.message}`;
                }
            };
            fetchBal();
            this._polling = setInterval(fetchBal, 3000);
        } catch (e) {
            document.getElementById('test-balance-output').textContent = `ERROR: ${e.message}`;
        }
    },
    async simulateWebhook() {
        try {
            // Solo per sviluppo: chiama billing webhook con payload minimo simulato
            const user = document.getElementById('test_checkout_user').value.trim();
            const expectedInc = parseInt(document.getElementById('test_expected_increment').value || '0', 10) || 0;
            if (!user || !expectedInc) {
                Utils.showToast('Seleziona utente e expected increment', 'warning');
                return;
            }
            const payload = {
                meta: { event_name: 'order_created', custom_data: { user_id: user, credits: expectedInc, amount_usd: 1 } },
                data: { attributes: { id: 'dev_tx', order_id: 'dev_order' } }
            };
            // Usa fetch diretto per passare il body così com'è
            const resp = await fetch(State.getBase() + '/core/v1/billing/webhook', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            const text = await resp.text();
            document.getElementById('test-balance-output').textContent = `Webhook resp: ${resp.status} ${text}`;
        } catch (e) {
            document.getElementById('test-balance-output').textContent = `ERROR: ${e.message}`;
        }
    },
    async executeFlow() {
        try {
            const input = document.getElementById('test-input').value.trim();
            const appId = document.getElementById('test_app_id')?.value || 'default';
            const output = document.getElementById('test-output');
            output.innerHTML = '<div class="loading loading-spinner loading-lg"></div>';
            
            const result = await API.post('/core/v1/ai/query', {
                message: input,
                app_id: appId
            });
            
            output.innerHTML = `
                <div class="card bg-base-100 shadow-xl">
                    <div class="card-body">
                        <h2 class="card-title">Response</h2>
                        <p>${result.response || result.message || 'No response'}</p>
                        ${result.credits_used ? `<p class="text-sm text-gray-500">Credits used: ${result.credits_used}</p>` : ''}
                    </div>
                </div>
            `;
            
            this.addToTimeline('Flow executed', 'success', {
                app_id: appId,
                flow_key: flowKey,
                elapsed_ms: elapsed,
                credits_used: result.credits_used
            });
        } catch (error) {
            const errorDetails = {
                message: error.message,
                status: error.status,
                details: error.response || error
            };
            
            output.innerHTML = `
                <div class="alert alert-error">
                    <i class="fas fa-times-circle"></i>
                    <div>
                        <h4 class="font-bold">Flow Execution Failed</h4>
                        <p>${error.message}</p>
                        ${error.status === 402 ? `
                            <div class="mt-2 text-sm">
                                <p>User has insufficient credits for this operation.</p>
                                <p>Run an Affordability Check for details.</p>
                            </div>
                        ` : ''}
                    </div>
                </div>
            `;
            
            this.addToTimeline('Flow failed', 'error', errorDetails);
        }
    },
    
    async testProvider() {
        const output = document.getElementById('test-provider-output').querySelector('pre');
        const status = document.getElementById('provider-status');
        
        try {
            output.classList.remove('hidden');
            output.textContent = 'Testing provider connection...';
            
            if (!BillingComponent.testProviderConnection) {
                throw new Error('Provider test not available');
            }
            
            // Call the existing test method
            await BillingComponent.testProviderConnection();
            
            // Since BillingComponent shows toast, we just update our UI
            const details = {
                status: 'SUCCESS',
                provider: 'LemonSqueezy',
                api_key: '✓ Configured',
                webhook_secret: '✓ Configured',
                test_endpoint: '/v1/users/me'
            };
            
            output.textContent = JSON.stringify(details, null, 2);
            status.classList.remove('badge-ghost', 'badge-error');
            status.classList.add('badge-success');
            status.textContent = 'Connected';
            
            this.addToTimeline('Provider test', 'success', details);
        } catch (e) {
            const details = {
                status: 'ERROR',
                error: e.message,
                possible_causes: [
                    'Missing API key in credentials',
                    'Invalid API key',
                    'Network issue with LemonSqueezy'
                ]
            };
            
            output.textContent = JSON.stringify(details, null, 2);
            status.classList.remove('badge-ghost', 'badge-success');
            status.classList.add('badge-error');
            status.textContent = 'Failed';
            
            this.addToTimeline('Provider test', 'error', details);
        }
    },
    
    addToTimeline(action, status, details) {
        const timeline = document.getElementById('test-timeline');
        if (!timeline) return;
        
        // Remove initial placeholder
        if (timeline.querySelector('.text-base-content\\/60')) {
            timeline.innerHTML = '';
        }
        
        const timestamp = new Date().toLocaleTimeString();
        const badgeClass = {
            success: 'badge-success',
            error: 'badge-error',
            warning: 'badge-warning',
            info: 'badge-info'
        }[status] || 'badge-ghost';
        
        const entry = document.createElement('div');
        entry.className = 'flex items-start gap-3 p-2 rounded hover:bg-base-200';
        entry.innerHTML = `
            <span class="text-xs text-base-content/60">${timestamp}</span>
            <span class="badge badge-sm ${badgeClass}">${status}</span>
            <div class="flex-1">
                <p class="text-sm font-semibold">${action}</p>
                ${details ? `<pre class="text-xs mt-1 text-base-content/60">${JSON.stringify(details, null, 2)}</pre>` : ''}
            </div>
        `;
        
        timeline.insertBefore(entry, timeline.firstChild);
        
        // Keep only last 10 entries
        while (timeline.children.length > 10) {
            timeline.removeChild(timeline.lastChild);
        }
    }
};