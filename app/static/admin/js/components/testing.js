/**
 * Componente Testing
 */
const TestingComponent = {
    _polling: null,
    _lastRunKey: 'core_test_last_exec',
    _saveLastRun(payload, res, meta) {
        try {
            const data = { ts: Date.now(), payload, res, meta };
            localStorage.setItem(this._lastRunKey, JSON.stringify(data));
        } catch (_) {}
    },
    _restoreLastRun() {
        try {
            const raw = localStorage.getItem(this._lastRunKey);
            if (!raw) return;
            const { res, payload, meta } = JSON.parse(raw);
            const el = document.getElementById('test-output');
            if (!el) return;
            el.innerHTML = `
                <div class="alert alert-info">
                    <i class="fas fa-history"></i>
                    <span>Ripristinato ultimo test</span>
                </div>
                <pre class="bg-base-200 p-2 rounded text-xs overflow-auto max-h-48 whitespace-pre-wrap break-words">${JSON.stringify({ payload, res, meta }, null, 2)}</pre>
            `;
        } catch (_) {}
    },
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
            const userOptions = (users.users || []).map(u => `<option value="${u.id}" data-email="${u.email}">${u.email} (${u.credits||0})</option>`).join('');
            const userSelect = document.getElementById('test_checkout_user');
            const affUser = document.getElementById('aff_user_select');
            const execUser = document.getElementById('exec_user_select');
            const convUser = document.getElementById('conv_user_select');
            if (userSelect) userSelect.innerHTML = userOptions;
            if (affUser) affUser.innerHTML = userOptions;
            if (convUser) convUser.innerHTML = userOptions;
            if (execUser) {
                execUser.innerHTML = userOptions;
                execUser.onchange = () => {
                    const opt = execUser.options[execUser.selectedIndex];
                    const email = opt ? opt.getAttribute('data-email') : '';
                    const emailInput = document.getElementById('exec_user_email');
                    if (emailInput) emailInput.value = email || '';
                };
                execUser.onchange();
            }

            // Plans dalla config unificata
            const billingConfig = await API.get('/core/v1/admin/billing/config');
            const plans = (billingConfig.config && billingConfig.config.plans) ? billingConfig.config.plans : [];
            const planSelect = document.getElementById('test_checkout_plan');
            if (planSelect) planSelect.innerHTML = plans.map(p => `<option value="${p.id}">${p.name} ($${p.price_usd})</option>`).join('');

            // Affordability app select
            const affApp = document.getElementById('aff_app_select');
            if (affApp && Array.isArray(apps.app_ids)) affApp.innerHTML = apps.app_ids.map(a => `<option value="${a}">${a}</option>`).join('');

            // Flow keys for selected app
            await this.loadFlowKeys();
            if (appSelect) appSelect.onchange = () => this.loadFlowKeys();
            
            // Popola dropdown conversazionali
            const convAppId = document.getElementById('conv_app_id');
            const convFlow = document.getElementById('conv_flow_key');
            if (convAppId && Array.isArray(apps.app_ids)) {
                convAppId.innerHTML = apps.app_ids.map(a => `<option value="${a}">${a}</option>`).join('');
            }
            
            // Popola flow keys per conversazionale (SOLO flow con is_conversational=true)
            const allFlows = await API.get('/core/v1/admin/flow-configs/all?app_id=*');
            if (convFlow && allFlows.items) {
                const conversationalFlows = allFlows.items.filter(f => f.is_conversational === true);
                if (conversationalFlows.length > 0) {
                    convFlow.innerHTML = conversationalFlows.map(f => `<option value="${f.flow_key}" data-app="${f.app_id}">${f.app_id}/${f.flow_key}</option>`).join('');
                } else {
                    convFlow.innerHTML = '<option value="">Nessun flow conversazionale configurato</option>';
                }
                
                // Popola app_id con solo le app che hanno flow conversazionali
                const conversationalApps = [...new Set(conversationalFlows.map(f => f.app_id))];
                if (convAppId && conversationalApps.length > 0) {
                    convAppId.innerHTML = conversationalApps.map(a => `<option value="${a}">${a}</option>`).join('');
                }
            }

            // Ripristina ultimo test se presente
            this._restoreLastRun();
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
                                    <strong>Password temporanea:</strong> 
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
                                    ${typeof res.openrouter_key_limit !== 'undefined' ? `<li><strong>Spending limit:</strong> $${res.openrouter_key_limit}</li>` : ''}
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
            }, 'Users');
        } catch (e) {
            document.getElementById('test-user-output').innerHTML = `
                <div class="alert alert-error">
                    <i class="fas fa-times-circle"></i> 
                    <span>Errore: ${e.message}</span>
                </div>
            `;
            
            this.addToTimeline('Creazione utente fallita', 'error', { error: e.message }, 'Users');
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
            this.addToTimeline('Generate checkout', 'info', { user, plan }, 'Checkout');
            const res = await API.post(`/core/v1/admin/billing/checkout?user_id=${encodeURIComponent(user)}&plan_id=${encodeURIComponent(plan)}`);
            if (res.checkout?.checkout_url) {
                document.getElementById('test-checkout-output').innerHTML = `<a class="link" href="${res.checkout.checkout_url}" target="_blank">Apri checkout</a>`;
                this.addToTimeline('Checkout URL generato', 'success', { url: res.checkout.checkout_url }, 'Checkout');
            } else {
                document.getElementById('test-checkout-output').textContent = JSON.stringify(res);
                this.addToTimeline('Checkout response', 'info', res, 'Checkout');
            }
        } catch (e) {
            document.getElementById('test-checkout-output').textContent = `ERROR: ${e.message}`;
            this.addToTimeline('Checkout error', 'error', { error: e.message }, 'Checkout');
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
        const input = document.getElementById('test-input').value.trim();
        const appId = document.getElementById('test_app_id')?.value || 'default';
        const flowKey = document.getElementById('exec_flow_key')?.value;
        const execUserSel = document.getElementById('exec_user_select');
        const userId = execUserSel?.value;
        const output = document.getElementById('test-output');

        if (!flowKey) {
            output.innerHTML = '<div class="alert alert-warning"><i class="fas fa-exclamation-triangle"></i> Seleziona un flow</div>';
            return;
        }
        if (!userId) {
            output.innerHTML = '<div class="alert alert-warning"><i class="fas fa-exclamation-triangle"></i> Seleziona un utente</div>';
            return;
        }

        try {
            const authHeaders = { ...State.getAuthHeaders(), 'X-App-Id': appId };
            
            // Prepara payload
            let userData;
            try {
                userData = input ? JSON.parse(input) : {};
            } catch (_) {
                userData = { input };
            }
            userData._as_user_id = userId;
            const payload = { flow_key: flowKey, data: userData };

            // Timeline iniziale
            const timeline = [];
            const addTimelineEvent = (event) => {
                timeline.push({ time: new Date().toISOString(), event });
                const tlEl = document.getElementById('exec-timeline');
                if (tlEl) {
                    tlEl.innerHTML = timeline.map(t => 
                        `<div class="flex gap-2">
                            <span class="opacity-60">${t.time.split('T')[1].split('.')[0]}</span>
                            <span>${t.event}</span>
                        </div>`
                    ).join('');
                }
            };

            addTimelineEvent('🚀 Inizio esecuzione flow');
            const userEmail = execUserSel.options[execUserSel.selectedIndex]?.text || 'Unknown';
            
            // Leggi saldo iniziale utente (admin)
            let balanceBefore = null;
            try {
                const prof = await API.get(`/core/v1/admin/user-credits?user_id=${encodeURIComponent(userId)}`);
                balanceBefore = typeof prof?.profile?.credits === 'number' ? prof.profile.credits : null;
                if (balanceBefore !== null) addTimelineEvent(`saldo iniziale: ${balanceBefore.toFixed(2)} cr`);
            } catch (_) {}
            
            // Mostra stato iniziale
            output.innerHTML = `
                <div class="space-y-4">
                    <!-- Timeline -->
                    <div class="bg-base-200 p-4 rounded-lg">
                        <h4 class="font-bold text-sm mb-2 flex items-center gap-2">
                            <i class="fas fa-clock"></i> Timeline Esecuzione
                        </h4>
                        <div id="exec-timeline" class="text-xs space-y-1 font-mono"></div>
                    </div>
                    
                    <!-- Loader -->
                    <div class="alert alert-info">
                        <i class="fas fa-spinner fa-spin"></i>
                        <span>Controllo affordability e esecuzione flow...</span>
                    </div>
                </div>
            `;
            
            addTimelineEvent('🔍 Controllo affordability pre-volo');
            // Esegui affordability check (admin, impersonificando l'utente)
            let affData = null; let affSec = null;
            try {
                const url = new URL(State.getBase() + '/core/v1/providers/flowise/affordability-check');
                url.searchParams.set('as_user_id', userId);
                if (flowKey) url.searchParams.set('flow_key', flowKey);
                const affStart = performance.now();
                const affResp = await fetch(url.toString(), { headers: authHeaders });
                affSec = ((performance.now() - affStart) / 1000).toFixed(2);
                if (affResp.ok) {
                    affData = await affResp.json();
                    addTimelineEvent(`${affSec}s affordability check -> ${affData.can_afford ? 'ok' : 'KO'}`);
                    const req = typeof affData.required_credits === 'number' ? affData.required_credits : (affData.minimum_required || 0);
                    addTimelineEvent(`${req.toFixed(2)} crediti richiesti -> ${(affData.available_credits || 0).toFixed(2)} disponibili`);
                } else {
                    const txt = await affResp.text();
                    addTimelineEvent(`${affSec}s affordability check -> errore ${affResp.status}`);
                    console.warn('Affordability error:', txt);
                }
            } catch (e) {
                addTimelineEvent(`affordability check errore: ${e.message}`);
            }

            // Marker per step successivi
            let lastMark = performance.now();
            addTimelineEvent('📤 Invio richiesta a Flow Executor (payload)');
            
            const start = Date.now();
            const execResp = await fetch(State.getBase() + '/core/v1/providers/flowise/execute', {
                    method: 'POST',
                headers: { 'Content-Type': 'application/json', ...authHeaders },
                body: JSON.stringify(payload)
            });
            
            const elapsed = Date.now() - start;
            const res = await execResp.json();
            addTimelineEvent(`📥 Risposta AI in ${(elapsed/1000).toFixed(2)}s`);

            if (execResp.ok) {
                addTimelineEvent('✅ Flow completato con successo');
                
                // Estrai risultato principale
                let mainResult = res.result;
                if (typeof mainResult === 'object' && mainResult.text) {
                    try {
                        const parsed = JSON.parse(mainResult.text);
                        mainResult = parsed.XPost || parsed;
                    } catch (e) {
                        // Keep as is
                    }
                }
                // Se disponibile, mostra input grezzo ricevuto da Flowise (start node)
                try {
                    if (res.result && Array.isArray(res.result.agentFlowExecutedData)) {
                        const startNode = res.result.agentFlowExecutedData.find(n => (n?.nodeLabel||'').toLowerCase() === 'start');
                        const rawInput = startNode?.data?.input;
                        if (rawInput && Object.keys(rawInput).length) {
                            this.addToTimeline('Input consegnato al flow', 'info', rawInput, 'Flow');
                        }
                    }
                } catch (_) {}

                // Visualizzazione stellare
                const affHtml = affData ? `
                        <div class="bg-base-300 p-3 rounded">
                            <h5 class="text-xs font-semibold mb-2 opacity-80">🧮 Affordability</h5>
                            <div class="space-y-1 text-sm">
                                <div class="flex justify-between"><span>Min Gate:</span><span class="font-mono">${(affData.minimum_required || 0).toFixed(2)} cr</span></div>
                                ${typeof affData.estimated_credits === 'number' ? `<div class="flex justify-between"><span>Stimati per flow:</span><span class="font-mono">${affData.estimated_credits.toFixed(2)} cr</span></div>` : ''}
                                ${typeof affData.required_credits === 'number' ? `<div class="flex justify-between font-semibold"><span>Richiesti (max):</span><span class="font-mono">${affData.required_credits.toFixed(2)} cr</span></div>` : ''}
                                <div class="flex justify-between"><span>Disponibili:</span><span class="font-mono">${(affData.available_credits || 0).toFixed(2)} cr</span></div>
                                <div class="flex justify-between font-bold"><span>Esito:</span><span class="${affData.can_afford ? 'text-success' : 'text-error'}">${affData.can_afford ? 'OK' : 'INSUFFICIENTI'}</span></div>
                                ${affSec ? `<div class="text-xs opacity-70">Tempo: ${affSec}s</div>` : ''}
                            </div>
                        </div>
                ` : '';
                const reqSummary = affData ? (typeof affData.required_credits === 'number' ? affData.required_credits : (affData.minimum_required || 0)) : null;
                const aiText = (res && res.result && typeof res.result.text === 'string') ? res.result.text : null;
                const summaryHtml = `
                        <div class="bg-base-200 p-3 rounded">
                            <h4 class="font-bold text-sm mb-2 flex items-center gap-2"><i class="fas fa-list"></i> Recap</h4>
                            <ul class="text-xs space-y-1">
                                ${affSec ? `<li><strong>${affSec}s</strong> affordability -> ${affData?.can_afford ? 'OK' : 'KO'}</li>` : ''}
                                ${affData ? `<li><strong>${(reqSummary||0).toFixed(2)} cr</strong> richiesti -> <strong>${(affData.available_credits||0).toFixed(2)} cr</strong> disponibili</li>` : ''}
                                <li><strong>${(elapsed/1000).toFixed(2)}s</strong> risposta AI</li>
                            </ul>
                        </div>`;

                output.innerHTML = `
                    <div class="space-y-4">
                        <!-- Header Success -->
                        <div class="alert alert-success">
                            <div class="flex items-center justify-between w-full">
                                <div class="flex items-center gap-2">
                                    <i class="fas fa-check-circle text-2xl"></i>
                                    <div>
                                        <h3 class="font-bold">Flow Eseguito con Successo</h3>
                                        <p class="text-sm opacity-80">Completato in ${elapsed}ms</p>
                                    </div>
                                </div>
                                <div class="text-right">
                                    <div class="text-sm font-semibold">Utente: ${userEmail}</div>
                                    <div class="text-xs opacity-80">Flow: ${flowKey}</div>
                                </div>
                            </div>
                        </div>

                        ${summaryHtml}

                        <!-- Timeline -->
                        <div class="bg-base-200 p-4 rounded-lg">
                            <h4 class="font-bold text-sm mb-2 flex items-center gap-2">
                                <i class="fas fa-clock"></i> Timeline Esecuzione
                            </h4>
                            <div id="exec-timeline" class="text-xs space-y-1 font-mono">
                                ${timeline.map(t => 
                                    `<div class="flex gap-2">
                                        <span class="opacity-60">${t.time.split('T')[1].split('.')[0]}</span>
                                        <span>${t.event}</span>
                                    </div>`
                                ).join('')}
                            </div>
                        </div>

                        <!-- 1. Payload Inviato -->
                        <div class="bg-base-200 p-4 rounded-lg">
                            <h4 class="font-bold text-sm mb-2 flex items-center gap-2">
                                <i class="fas fa-upload text-primary"></i> Payload Inviato
                            </h4>
                            <pre class="bg-base-300 p-3 rounded text-xs overflow-auto max-h-48 whitespace-pre-wrap break-words">${JSON.stringify(payload, null, 2)}</pre>
                        </div>

                        <!-- 1b. AI Output (text) -->
                        ${aiText ? `
                        <div class="bg-base-200 p-4 rounded-lg">
                            <h4 class="font-bold text-sm mb-2 flex items-center gap-2">
                                <i class="fas fa-comment-dots text-success"></i> AI Output (text)
                            </h4>
                            <pre class="bg-base-100 p-3 rounded text-sm whitespace-pre-wrap">${aiText.replace(/</g,'&lt;')}</pre>
                        </div>
                        ` : ''}

                        <!-- 2. Risultato Principale -->
                        <div class="bg-base-200 p-4 rounded-lg">
                            <h4 class="font-bold text-sm mb-2 flex items-center gap-2">
                                <i class="fas fa-magic text-success"></i> Risultato AI
                            </h4>
                            <div class="bg-white text-black p-4 rounded shadow-inner overflow-auto" style="max-height: 420px;">
                                ${typeof mainResult === 'string' ? 
                                    `<p class="whitespace-pre-wrap">${mainResult}</p>` :
                                    `<pre class="text-sm overflow-auto max-h-48 whitespace-pre-wrap break-words">${JSON.stringify(mainResult, null, 2)}</pre>`
                                }
                            </div>
                        </div>

                        <!-- 3. Pricing & Costs Breakdown -->
                        ${res.pricing ? `
                        <div class="bg-base-200 p-4 rounded-lg">
                            <h4 class="font-bold text-sm mb-3 flex items-center gap-2">
                                <i class="fas fa-calculator text-warning"></i> Breakdown Completo dei Costi
                            </h4>
                            
                            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                                ${affHtml}
                                <!-- OpenRouter Raw Cost -->
                                <div class="bg-base-300 p-3 rounded">
                                    <h5 class="text-xs font-semibold mb-2 opacity-80">🤖 Costo OpenRouter (Raw)</h5>
                                    <div class="space-y-1">
                                        <div class="flex justify-between text-sm">
                                            <span>Costo effettivo:</span>
                                            <span class="font-mono font-bold" data-pricing-cost>$${res.pricing.actual_cost_usd?.toFixed(6) || '0.000000'}</span>
                                        </div>
                                        <div class="flex justify-between text-xs opacity-70">
                                            <span>Usage prima:</span>
                                            <span class="font-mono">$${res.pricing.usage_before_usd?.toFixed(6) || 'N/A'}</span>
                                        </div>
                                        <div class="flex justify-between text-xs opacity-70">
                                            <span>Usage dopo:</span>
                                            <span class="font-mono" data-pricing-after>$${res.pricing.usage_after_usd?.toFixed(6) || 'N/A'}</span>
                                        </div>
                                        ${res.pricing.status === 'pending' ? 
                                            '<div class="text-xs text-warning mt-1" data-pricing-pending><i class="fas fa-clock"></i> Calcolo in corso...</div>' : 
                                            ''
                                        }
                                    </div>
                                </div>

                                <!-- Business Multipliers -->
                                <div class="bg-base-300 p-3 rounded">
                                    <h5 class="text-xs font-semibold mb-2 opacity-80">📊 Moltiplicatori Business</h5>
                                    <div class="space-y-1 text-sm">
                                        <div class="flex justify-between">
                                            <span>USD → Credits:</span>
                                            <span class="font-mono">${res.pricing.usd_to_credits || 100}x</span>
                                        </div>
                                        <div class="flex justify-between">
                                            <span>Overhead:</span>
                                            <span class="font-mono">${res.pricing.overhead_multiplier || 1}x</span>
                                        </div>
                                        <div class="flex justify-between">
                                            <span>Margine:</span>
                                            <span class="font-mono">${res.pricing.margin_multiplier || 1}x</span>
                                        </div>
                                        <div class="flex justify-between font-bold">
                                            <span>Totale:</span>
                                            <span class="font-mono">${res.pricing.usd_multiplier || 1}x</span>
                                        </div>
                                    </div>
                                </div>

                                <!-- Prezzo Pubblico -->
                                <div class="bg-base-300 p-3 rounded">
                                    <h5 class="text-xs font-semibold mb-2 opacity-80">💵 Prezzo Cliente</h5>
                                    <div class="space-y-1">
                                        <div class="flex justify-between text-sm">
                                            <span>Prezzo USD:</span>
                                            <span class="font-mono font-bold" data-pricing-public>$${res.pricing.public_price_usd?.toFixed(4) || '0.0000'}</span>
                                        </div>
                                        <div class="flex justify-between text-sm">
                                            <span>Crediti:</span>
                                            <span class="font-mono font-bold text-warning" data-pricing-credits>${res.pricing.credits_to_debit?.toFixed(2) || '0.00'}</span>
                                        </div>
                                        <div class="flex justify-between text-xs opacity-70">
                                            <span>Markup:</span>
                                            <span class="font-mono" data-pricing-markup>+${res.pricing.markup_percent?.toFixed(0) || '0'}%</span>
                                        </div>
                                    </div>
                                </div>

                                <!-- Saldo Utente -->
                                ${res.debit ? `
                                <div class="bg-base-300 p-3 rounded">
                                    <h5 class="text-xs font-semibold mb-2 opacity-80">👤 Saldo Utente</h5>
                                    <div class="space-y-1">
                                        <div class="flex justify-between text-sm">
                                            <span>Prima:</span>
                                            <span class="font-mono">${res.debit.balance_before?.toFixed(2) || 'N/A'}</span>
                                        </div>
                                        <div class="flex justify-between text-sm">
                                            <span>Scalati:</span>
                                            <span class="font-mono text-error">-${res.debit.amount?.toFixed(2) || '0.00'}</span>
                                        </div>
                                        <div class="flex justify-between text-sm font-bold">
                                            <span>Dopo:</span>
                                            <span class="font-mono ${res.debit.balance_after < 0 ? 'text-error' : 'text-success'}">${res.debit.balance_after?.toFixed(2) || 'N/A'}</span>
                                        </div>
                                    </div>
                                </div>
                                ` : ''}
                            </div>

                            <!-- Riepilogo Profitto -->
                            ${res.pricing.actual_cost_usd && res.pricing.public_price_usd ? `
                            <div class="mt-4 p-3 bg-success/20 border border-success/50 rounded">
                                <div class="flex items-center justify-between">
                                    <span class="text-sm font-semibold">💰 Profitto per questa chiamata:</span>
                                    <div class="text-right">
                                        <div class="font-mono font-bold">
                                            $${(res.pricing.public_price_usd - res.pricing.actual_cost_usd).toFixed(4)}
                                        </div>
                                        <div class="text-xs opacity-80">
                                            (${((res.pricing.public_price_usd / res.pricing.actual_cost_usd - 1) * 100).toFixed(0)}% margin)
                                        </div>
                                    </div>
                                </div>
                            </div>
                            ` : ''}
                        </div>
                        ` : ''}

                        <!-- 4. Raw Response (Collapsible) -->
                        <details class="bg-base-200 p-4 rounded-lg">
                            <summary class="cursor-pointer font-bold text-sm flex items-center gap-2">
                                <i class="fas fa-code"></i> Risposta Completa (JSON)
                            </summary>
                            <pre class="bg-base-300 p-3 rounded text-xs mt-3 overflow-auto max-h-96 whitespace-pre-wrap break-words">${JSON.stringify(res, null, 2)}</pre>
                        </details>
                    </div>
                `;

                // Se pricing è pending, avvia polling
                if (res.pricing?.status === 'pending' && res.pricing?.usage_before_usd !== undefined) {
                    this.startPricingPolling(res.pricing.usage_before_usd, authHeaders, userId);
                }
                // Avvia polling saldo per vedere addebito
                this.startBalancePolling(userId, balanceBefore);
                
                this.addToTimeline('Flow executed successfully', 'success', { elapsed_ms: elapsed }, 'Flow');

                // Salva ultimo test
                this._saveLastRun(payload, res, { timeline, balanceBefore, affData, elapsed_ms: elapsed });

            } else {
                addTimelineEvent('❌ Errore durante esecuzione');
                output.innerHTML = `
                    <div class="space-y-4">
                        <!-- Header Error -->
                        <div class="alert alert-error">
                            <div class="flex items-center gap-2">
                                <i class="fas fa-times-circle text-2xl"></i>
                                <div>
                                    <h3 class="font-bold">Errore Esecuzione Flow</h3>
                                    <p class="text-sm">${res.detail || 'Errore sconosciuto'}</p>
                                </div>
                            </div>
                        </div>

                        <!-- Timeline -->
                        <div class="bg-base-200 p-4 rounded-lg">
                            <h4 class="font-bold text-sm mb-2 flex items-center gap-2">
                                <i class="fas fa-clock"></i> Timeline Esecuzione
                            </h4>
                            <div class="text-xs space-y-1 font-mono">
                                ${timeline.map(t => 
                                    `<div class="flex gap-2">
                                        <span class="opacity-60">${t.time.split('T')[1].split('.')[0]}</span>
                                        <span>${t.event}</span>
                                    </div>`
                                ).join('')}
                            </div>
                        </div>

                        <!-- Error Details -->
                        <div class="bg-base-200 p-4 rounded-lg">
                            <h4 class="font-bold text-sm mb-2">Dettagli Errore</h4>
                            <pre class="bg-error/20 text-error-content p-3 rounded text-xs overflow-auto max-h-48 whitespace-pre-wrap break-words">${JSON.stringify(res, null, 2)}</pre>
                        </div>
                    </div>
                `;
                
                this.addToTimeline('Flow failed', 'error', res, 'Flow');
            }
            } catch (error) {
            output.innerHTML = `
                    <div class="alert alert-error">
                    <i class="fas fa-times-circle"></i>
                    <span>Errore di rete: ${error.message}</span>
                    </div>
                `;
            }
    },

    // Helper per polling pricing updates
    async startPricingPolling(usageBeforeUsd, authHeaders, userId) {
        let attempts = 0;
        const maxAttempts = 15;
        const interval = 2000;

        const pollTimer = setInterval(async () => {
            attempts++;
            try {
                const resp = await fetch(
                    State.getBase() + `/core/v1/providers/flowise/pricing?usage_before_usd=${encodeURIComponent(usageBeforeUsd)}&as_user_id=${encodeURIComponent(userId)}`,
                    { headers: authHeaders }
                );
                
                if (resp.ok) {
                    const pricing = await resp.json();
                    if (pricing.status === 'ready') {
                        // Aggiorna i valori nel DOM
                        const costEl = document.querySelector('[data-pricing-cost]');
                        const afterEl = document.querySelector('[data-pricing-after]');
                        const pendingEl = document.querySelector('[data-pricing-pending]');
                        const publicEl = document.querySelector('[data-pricing-public]');
                        const creditsEl = document.querySelector('[data-pricing-credits]');
                        const markupEl = document.querySelector('[data-pricing-markup]');

                        if (costEl) costEl.textContent = `$${pricing.actual_cost_usd?.toFixed(6) || '0.000000'}`;
                        if (afterEl) afterEl.textContent = `$${pricing.usage_after_usd?.toFixed(6) || 'N/A'}`;
                        if (pendingEl) pendingEl.remove();
                        // Calcoli con fallback se alcuni campi non sono presenti
                        const actualUsd = typeof pricing.actual_cost_usd === 'number' ? pricing.actual_cost_usd : 0;
                        const usdMult = typeof pricing.usd_multiplier === 'number' ? pricing.usd_multiplier : (typeof pricing.total_multiplier_percent === 'number' ? pricing.total_multiplier_percent/100 : null);
                        const publicUsd = typeof pricing.public_price_usd === 'number' ? pricing.public_price_usd : (usdMult ? actualUsd * usdMult : null);
                        const credits = typeof pricing.credits_to_debit === 'number' ? pricing.credits_to_debit : (typeof pricing.actual_cost_credits === 'number' ? pricing.actual_cost_credits : (typeof pricing.final_credit_multiplier === 'number' ? actualUsd * pricing.final_credit_multiplier : null));
                        const markup = typeof pricing.markup_percent === 'number' ? pricing.markup_percent : (usdMult ? (usdMult - 1) * 100 : null);

                        if (publicEl) publicEl.textContent = `$${(publicUsd ?? 0).toFixed(4)}`;
                        if (creditsEl) creditsEl.textContent = `${(credits ?? 0).toFixed(2)}`;
                        if (markupEl) markupEl.textContent = `+${(markup ?? 0).toFixed(0)}%`;

                        try { console.debug('pricing ready', {actualUsd, usdMult, publicUsd, credits, markup, pricing}); } catch(_) {}

                        clearInterval(pollTimer);
                    }
                }
            } catch (e) {
                console.error('Pricing poll error:', e);
            }

            if (attempts >= maxAttempts) {
                clearInterval(pollTimer);
            }
        }, interval);
    },

    // Polling saldo per mostrare addebito su async
    async startBalancePolling(userId, balanceBefore) {
        if (balanceBefore === null) return;
        let attempts = 0;
        const maxAttempts = 20;
        const interval = 2000;
        const balanceEl = document.querySelector('[data-balance-after]');
        const debitEl = document.querySelector('[data-debit-amount]');
        const timer = setInterval(async () => {
            attempts++;
            try {
                const prof = await API.get(`/core/v1/admin/user-credits?user_id=${encodeURIComponent(userId)}`);
                const after = typeof prof?.profile?.credits === 'number' ? prof.profile.credits : null;
                if (after !== null && balanceEl) balanceEl.textContent = after.toFixed(2);
                if (after !== null && debitEl && balanceBefore !== null) {
                    const delta = (balanceBefore - after);
                    if (delta > 0) debitEl.textContent = `-${delta.toFixed(2)} cr`;
                }
            } catch (_) {}
            if (attempts >= maxAttempts) clearInterval(timer);
        }, interval);
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
            
            // Call the real test endpoint directly
            const response = await API.post('/core/v1/admin/credentials/test?provider=lemonsqueezy', {}, {
                headers: { 'X-Admin-Key': State.adminKey }
            });
            
            if (response.success) {
                const details = {
                    status: 'SUCCESS',
                    provider: 'LemonSqueezy',
                    user: response.user || 'Connected',
                    test_endpoint: '/v1/users/me'
                };
                
                output.textContent = JSON.stringify(details, null, 2);
                status.classList.remove('badge-ghost', 'badge-error');
                status.classList.add('badge-success');
                status.textContent = 'Connected';
                
                // Sposta la timeline qui per evitare 'details is not defined'
                this.addToTimeline('Provider test', 'success', details, 'Provider');
            } else {
                throw new Error(response.error || 'Test failed');
            }
            
            // ... existing code ...
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
            
            this.addToTimeline('Provider test', 'error', details, 'Provider');
        }
    },
    
    addToTimeline(action, status, details, category) {
        // Timeline rimossa - funzione disabilitata
        return;
    },
    
    // === CONVERSATIONAL FLOW TESTING ===
    
    _chatSessionId: null,
    _chatMessages: [],
    
    async sendChatMessage() {
        const input = document.getElementById('chat-input');
        const flowKeySelect = document.getElementById('conv_flow_key');
        const flowKey = flowKeySelect?.value;
        
        // Estrai app_id dal flow selezionato (attributo data-app)
        const selectedOption = flowKeySelect?.options[flowKeySelect.selectedIndex];
        const appId = selectedOption?.getAttribute('data-app') || 'smart_contact_form';
        
        const userId = document.getElementById('conv_user_select')?.value;
        const chatContainer = document.getElementById('chat-messages');
        
        console.log('Chat test config:', { appId, flowKey, userId });
        
        if (!input || !input.value.trim()) {
            Utils.showToast('Scrivi un messaggio', 'warning');
            return;
        }
        
        if (!flowKey || !userId) {
            Utils.showToast('Seleziona App, Flow e User', 'error');
            return;
        }
        
        const userMessage = input.value.trim();
        input.value = '';
        
        // Aggiungi messaggio utente alla UI
        this._chatMessages.push({ role: 'user', content: userMessage });
        this._renderChat();
        
        // Aggiungi loading indicator
        const loadingDiv = document.createElement('div');
        loadingDiv.className = 'chat chat-start mb-2';
        loadingDiv.id = 'chat-loading';
        loadingDiv.innerHTML = `
            <div class="chat-bubble bg-base-300">
                <span class="loading loading-dots loading-sm"></span>
            </div>
        `;
        chatContainer.appendChild(loadingDiv);
        chatContainer.scrollTop = chatContainer.scrollHeight;
        
        try {
            const authHeaders = { ...State.getAuthHeaders(), 'X-App-Id': appId };
            const payload = {
                flow_key: flowKey,
                data: { 
                    input: userMessage,
                    _as_user_id: userId  // ✅ OBBLIGATORIO per X-Admin-Key
                }
            };
            
            // Aggiungi session_id se esiste
            if (this._chatSessionId) {
                payload.session_id = this._chatSessionId;
            }
            
            const response = await API.post('/core/v1/providers/flowise/execute', payload, { headers: authHeaders });
            
            // Rimuovi loading
            document.getElementById('chat-loading')?.remove();
            
            // Estrai risposta e session_id
            const botMessage = response.result?.text || 'No response';
            const sessionId = response.flow?.session_id;
            const isConversational = response.flow?.is_conversational;
            
            // Salva session_id se nuovo
            if (sessionId && !this._chatSessionId) {
                this._chatSessionId = sessionId;
                this._updateSessionBadge();
                Utils.showToast('Conversazione iniziata!', 'success');
            }
            
            // Aggiungi risposta bot
            this._chatMessages.push({ role: 'assistant', content: botMessage });
            this._renderChat();
            
            // Log info
            console.log('Chat response:', {
                sessionId,
                isConversational,
                messageCount: this._chatMessages.length
            });
            
        } catch (error) {
            document.getElementById('chat-loading')?.remove();
            this._chatMessages.push({ 
                role: 'error', 
                content: `Errore: ${error.message}` 
            });
            this._renderChat();
            Utils.showToast(`Errore: ${error.message}`, 'error');
        }
    },
    
    newConversation() {
        if (this._chatMessages.length > 0) {
            if (!confirm('Iniziare una nuova conversazione? La cronologia corrente sarà persa.')) {
                return;
            }
        }
        
        this._chatSessionId = null;
        this._chatMessages = [];
        this._renderChat();
        this._updateSessionBadge();
        Utils.showToast('Nuova conversazione avviata', 'info');
    },
    
    clearChat() {
        if (this._chatMessages.length === 0) return;
        
        if (confirm('Pulire la cronologia chat?')) {
            this._chatMessages = [];
            this._renderChat();
            Utils.showToast('Chat pulita', 'info');
        }
    },
    
    _renderChat() {
        const container = document.getElementById('chat-messages');
        if (!container) return;
        
        if (this._chatMessages.length === 0) {
            container.innerHTML = `
                <div class="text-center text-base-content/60 py-8">
                    <i class="fas fa-comment-dots text-4xl mb-2"></i>
                    <p>Inizia una conversazione inviando un messaggio</p>
                </div>
            `;
            return;
        }
        
        container.innerHTML = this._chatMessages.map(msg => {
            const isUser = msg.role === 'user';
            const isError = msg.role === 'error';
            const chatClass = isUser ? 'chat-end' : 'chat-start';
            const bubbleClass = isUser ? 'bg-primary text-primary-content' : 
                                isError ? 'bg-error text-error-content' : 
                                'bg-base-300';
            
            return `
                <div class="chat ${chatClass} mb-2">
                    <div class="chat-bubble ${bubbleClass}">
                        ${this._escapeHtml(msg.content)}
                    </div>
                </div>
            `;
        }).join('');
        
        // Auto-scroll
        container.scrollTop = container.scrollHeight;
    },
    
    _updateSessionBadge() {
        const badge = document.getElementById('conv-session-badge');
        if (!badge) return;
        
        if (this._chatSessionId) {
            badge.textContent = `Session: ${this._chatSessionId.substring(0, 8)}...`;
            badge.className = 'badge badge-success';
        } else {
            badge.textContent = 'No session';
            badge.className = 'badge badge-ghost';
        }
    },
    
    _escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
};