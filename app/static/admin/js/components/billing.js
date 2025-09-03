/**
 * Componente Billing & Plans
 */
const BillingComponent = {
    /**
     * Carica dati piani
     */
    async loadPlansData() {
        try {
            // Carica SOLO dalla configurazione billing unificata
            let plans = [];
            const billingConfig = await API.get('/core/v1/admin/billing/config');
            plans = (billingConfig.config && billingConfig.config.plans) ? billingConfig.config.plans : [];
            
            const container = document.getElementById('plans-container');
            if (container) {
                container.innerHTML = '';
                plans.forEach(plan => this.addPlanCard(plan));
            }
        } catch (error) {
            console.error('Failed to load plans data:', error);
            Utils.showToast('Failed to load plans', 'error');
        }
    },
    
    /**
     * Aggiungi card piano con regole rollout integrate
     */
    addPlanCard(plan) {
        const container = document.getElementById('plans-container');
        if (!container) return;
        
        const rollout = plan.rollout || { enabled: false, rule: {} };
        const cardId = `plan-card-${plan.id || Date.now()}`;
        
        const card = document.createElement('div');
        card.className = 'card bg-base-100 shadow-xl mb-4';
        card.id = cardId;
        card.innerHTML = `
            <div class="card-body">
                <div class="grid grid-cols-1 md:grid-cols-6 gap-4 items-end mb-4">
                    <div>
                        <label class="label"><span class="label-text">Plan ID</span></label>
                        <input type="text" class="input input-sm input-bordered" data-field="id" value="${plan.id || ''}" placeholder="plan-id" />
                    </div>
                    <div>
                        <label class="label"><span class="label-text">Name</span></label>
                        <input type="text" class="input input-sm input-bordered" data-field="name" value="${plan.name || ''}" placeholder="Plan Name" />
                    </div>
                    <div>
                        <label class="label"><span class="label-text">Type</span></label>
                        <select class="select select-sm select-bordered" data-field="type">
                            <option value="subscription" ${plan.type === 'subscription' ? 'selected' : ''}>Subscription</option>
                            <option value="one_time" ${plan.type === 'one_time' ? 'selected' : ''}>One Time</option>
                        </select>
                    </div>
                    <div>
                        <label class="label"><span class="label-text">Price (USD)</span></label>
                        <input type="number" class="input input-sm input-bordered" data-field="price_usd" value="${plan.price_usd || ''}" step="0.01" placeholder="0.00" />
                    </div>
                    <div>
                        <label class="label"><span class="label-text">Credits</span></label>
                        <input type="number" class="input input-sm input-bordered" data-field="credits_per_month" value="${plan.credits_per_month || plan.credits || ''}" placeholder="0" />
                    </div>
                    <div class="flex gap-2">
                        <button class="btn btn-sm btn-primary" onclick="BillingComponent.savePlanFromCard('${cardId}')">Save</button>
                        <button class="btn btn-sm btn-error" onclick="BillingComponent.removePlanCard('${cardId}')">Remove</button>
                    </div>
                </div>
                
                <div class="divider">Rollout Rules</div>
                
                <div class="bg-base-200 rounded-lg p-4">
                    <div class="flex items-center justify-between mb-4">
                        <label class="label cursor-pointer flex items-center gap-3">
                            <input type="checkbox" class="toggle toggle-primary toggle-lg" data-field="rollout_enabled" ${rollout.enabled ? 'checked' : ''} onchange="BillingComponent.toggleRolloutUI('${cardId}', this.checked)" />
                            <span class="label-text text-lg font-medium">Enable Credit Rollout</span>
                        </label>
                        <div class="flex items-center gap-2">
                            <select class="select select-sm select-bordered" data-field="rollout_interval" ${!rollout.enabled ? 'disabled' : ''}>
                                <option value="daily" ${rollout.interval === 'daily' ? 'selected' : ''}>Daily</option>
                                <option value="weekly" ${rollout.interval === 'weekly' ? 'selected' : ''}>Weekly</option>
                                <option value="monthly" ${rollout.interval === 'monthly' || !rollout.interval ? 'selected' : ''}>Monthly</option>
                                <option value="yearly" ${rollout.interval === 'yearly' ? 'selected' : ''}>Yearly</option>
                            </select>
                            <div class="badge badge-ghost">
                                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-4 h-4 mr-1">
                                    <path stroke-linecap="round" stroke-linejoin="round" d="M12 6v6h4.5m4.5 0a9 9 0 11-18 0 9 9 0 0118 0z" />
                                </svg>
                                <span data-field="interval_badge">${rollout.interval || 'Monthly'}</span>
                            </div>
                        </div>
                    </div>
                    
                    <div class="rollout-config ${rollout.enabled ? '' : 'opacity-50 pointer-events-none'}" id="rollout-config-${cardId}">
                        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                            <!-- Rollout Type & Value -->
                            <div class="space-y-4">
                                <h4 class="font-semibold">Rollout Amount</h4>
                                <div class="flex gap-2">
                                    <div class="form-control flex-1">
                                        <label class="label cursor-pointer justify-start gap-2">
                                            <input type="radio" name="rollout-type-${cardId}" value="fixed" class="radio radio-primary" data-field="rollout_type_fixed" ${rollout.rule?.type === 'fixed' ? 'checked' : ''} onchange="BillingComponent.updateRolloutType('${cardId}', 'fixed')" />
                                            <span class="label-text">Fixed Credits</span>
                                        </label>
                                        <div class="input-group">
                                            <input type="number" class="input input-bordered w-full" data-field="rollout_value_fixed" value="${rollout.rule?.type === 'fixed' ? rollout.rule?.value : ''}" step="1" placeholder="100" ${rollout.rule?.type !== 'fixed' ? 'disabled' : ''} />
                                            <span class="bg-base-300 px-3 flex items-center">credits</span>
                                        </div>
                                    </div>
                                    
                                    <div class="form-control flex-1">
                                        <label class="label cursor-pointer justify-start gap-2">
                                            <input type="radio" name="rollout-type-${cardId}" value="percent" class="radio radio-primary" data-field="rollout_type_percent" ${rollout.rule?.type === 'percent' ? 'checked' : ''} onchange="BillingComponent.updateRolloutType('${cardId}', 'percent')" />
                                            <span class="label-text">Percentage</span>
                                        </label>
                                        <div class="input-group">
                                            <input type="number" class="input input-bordered w-full" data-field="rollout_value_percent" value="${rollout.rule?.type === 'percent' ? rollout.rule?.value : ''}" step="0.1" min="0" max="100" placeholder="50" ${rollout.rule?.type !== 'percent' ? 'disabled' : ''} />
                                            <span class="bg-base-300 px-3 flex items-center">%</span>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            
                            <!-- Max Carryover -->
                            <div class="space-y-4">
                                <h4 class="font-semibold">Limits</h4>
                                <div class="form-control">
                                    <label class="label">
                                        <span class="label-text">Maximum Carryover</span>
                                        <span class="label-text-alt text-info">Optional cap on accumulated credits</span>
                                    </label>
                                    <div class="input-group">
                                        <input type="number" class="input input-bordered w-full" data-field="rollout_max" value="${rollout.rule?.max_carryover || ''}" step="1" placeholder="No limit" />
                                        <span class="bg-base-300 px-3 flex items-center">credits</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        container.appendChild(card);
    },
    
    /**
     * Toggle UI rollout
     */
    toggleRolloutUI(cardId, enabled) {
        const card = document.getElementById(cardId);
        if (!card) return;
        
        const configDiv = document.getElementById(`rollout-config-${cardId}`);
        const intervalSelect = card.querySelector('[data-field="rollout_interval"]');
        
        if (configDiv) {
            if (enabled) {
                configDiv.classList.remove('opacity-50', 'pointer-events-none');
                if (intervalSelect) intervalSelect.disabled = false;
            } else {
                configDiv.classList.add('opacity-50', 'pointer-events-none');
                if (intervalSelect) intervalSelect.disabled = true;
            }
        }
    },

    /**
     * Aggiorna tipo rollout
     */
    updateRolloutType(cardId, type) {
        const card = document.getElementById(cardId);
        if (!card) return;
        
        const fixedInput = card.querySelector('[data-field="rollout_value_fixed"]');
        const percentInput = card.querySelector('[data-field="rollout_value_percent"]');
        
        if (type === 'fixed') {
            fixedInput.disabled = false;
            percentInput.disabled = true;
            percentInput.value = '';
        } else {
            fixedInput.disabled = true;
            fixedInput.value = '';
            percentInput.disabled = false;
        }
    },

    /**
     * Aggiungi nuovo piano
     */
    addNewPlan() {
        const newPlan = {
            id: '',
            name: '',
            type: 'subscription',
            price_usd: 0,
            credits_per_month: 0,
            rollout: {
                enabled: false,
                rule: {
                    type: 'fixed',
                    value: 0
                }
            }
        };
        this.addPlanCard(newPlan);
    },

    /**
     * Salva piano da card
     */
    async savePlanFromCard(cardId) {
        const card = document.getElementById(cardId);
        if (!card) return;
        
        // Raccogli tutti i dati dalla card
        const planData = {
            id: card.querySelector('[data-field="id"]').value.trim(),
            name: card.querySelector('[data-field="name"]').value.trim(),
            type: card.querySelector('[data-field="type"]').value,
            price_usd: parseFloat(card.querySelector('[data-field="price_usd"]').value) || 0,
            credits_per_month: parseInt(card.querySelector('[data-field="credits_per_month"]').value) || 0
        };
        
        // Raccogli dati rollout
        const rolloutEnabled = card.querySelector('[data-field="rollout_enabled"]').checked;
        const rolloutInterval = card.querySelector('[data-field="rollout_interval"]').value || 'monthly';
        let rolloutType = 'fixed';
        let rolloutValue = 0;
        
        // Determina tipo e valore in base ai radio button
        const fixedRadio = card.querySelector('[data-field="rollout_type_fixed"]');
        const percentRadio = card.querySelector('[data-field="rollout_type_percent"]');
        
        if (fixedRadio && fixedRadio.checked) {
            rolloutType = 'fixed';
            rolloutValue = parseFloat(card.querySelector('[data-field="rollout_value_fixed"]').value) || 0;
        } else if (percentRadio && percentRadio.checked) {
            rolloutType = 'percent';
            rolloutValue = parseFloat(card.querySelector('[data-field="rollout_value_percent"]').value) || 0;
        }
        
        const rolloutMax = parseFloat(card.querySelector('[data-field="rollout_max"]').value) || undefined;
        
        if (rolloutEnabled) {
            planData.rollout = {
                enabled: true,
                interval: rolloutInterval,
                rule: {
                    type: rolloutType,
                    value: rolloutValue,
                    ...(rolloutMax !== undefined && !isNaN(rolloutMax) ? { max_carryover: rolloutMax } : {})
                }
            };
        } else {
            planData.rollout = { enabled: false };
        }
        
        console.log('Saving plan with rollout data:', planData);
        
        // Validazione
        if (!planData.id) {
            Utils.showToast('Plan ID is required', 'error');
            return;
        }
        
        try {
            // Ottieni configurazione corrente
            const billingConfig = await API.get('/core/v1/admin/billing/config');
            const config = billingConfig.config || {};
            if (!config.plans) {
                config.plans = [];
            }
            
            // Trova o aggiungi piano
            const existingIndex = config.plans.findIndex(p => p.id === planData.id);
            if (existingIndex >= 0) {
                config.plans[existingIndex] = planData;
            } else {
                config.plans.push(planData);
            }
            
            // Salva configurazione
            await API.put('/core/v1/admin/billing/config', config);
            
            // Feedback visivo
            card.classList.add('ring-2', 'ring-success');
            setTimeout(() => {
                card.classList.remove('ring-2', 'ring-success');
            }, 2000);
            
            Utils.showToast(`Plan "${planData.name}" saved successfully`, 'success');
        } catch (error) {
            Utils.showToast(`Failed to save plan: ${error.message}`, 'error');
        }
    },

    /**
     * Rimuovi card piano
     */
    removePlanCard(cardId) {
        const card = document.getElementById(cardId);
        if (card) {
            card.remove();
        }
    },

    /**
     * Salva singolo piano (legacy per compatibilità)
     */
    async saveSinglePlan(button) {
        const row = button.closest('tr');
        const inputs = row.querySelectorAll('input, select');
        const edited = {
            id: inputs[0].value.trim(),
            name: inputs[1].value.trim(),
            type: inputs[2].value,
            price_usd: parseFloat(inputs[3].value) || 0,
            credits_per_month: parseInt(inputs[4].value) || 0
        };
        
        // Validazione
        if (!edited.id) {
            Utils.showToast('Plan ID is required', 'error');
            return;
        }
        
        try {
            // Prima ottieni la configurazione corrente
            const billingConfig = await API.get('/core/v1/admin/billing/config');
            const config = billingConfig.config || {};
            
            // Aggiorna o aggiungi il piano nella configurazione
            if (!config.plans) {
                config.plans = [];
            }
            
            // Trova e aggiorna o aggiungi il piano
            const existingIndex = config.plans.findIndex(p => p.id === edited.id);
            if (existingIndex >= 0) {
                const current = config.plans[existingIndex] || {};
                // Mantieni eventuali campi extra (rollout, bi_flags, variant_id, ecc.)
                config.plans[existingIndex] = { ...current, ...edited };
            } else {
                config.plans.push(edited);
            }
            
            // Salva la configurazione aggiornata
            await API.put('/core/v1/admin/billing/config', config);
            
            // Aggiorna il bottone per mostrare successo
            const originalText = button.textContent;
            button.textContent = '✅ Saved';
            button.classList.add('btn-success');
            setTimeout(() => {
                button.textContent = originalText;
                button.classList.remove('btn-success');
            }, 2000);
            
            Utils.showToast(`Plan "${edited.name}" saved successfully`, 'success');
        } catch (error) {
            Utils.showToast(`Failed to save plan: ${error.message}`, 'error');
        }
    },


    
    /**
     * Carica configurazione billing
     */
    async loadBillingConfig() {
        try {
            const billingConfig = await API.get('/core/v1/admin/billing/config');
            const config = billingConfig.config || {};
            const ls = config.lemonsqueezy || {};
            
            const storeInput = document.getElementById('ls_store');
            if (storeInput) storeInput.value = ls.store_id || '';
            
            const testModeInput = document.getElementById('ls_test_mode');
            if (testModeInput) testModeInput.checked = !!ls.test_mode;
            
            // Carica mapping varianti dai piani della config unificata
            const plans = (config.plans || []);
            const variantMap = (ls.variant_map || {});
            const tbody = document.getElementById('variant-map-table');
            
            if (tbody) {
                tbody.innerHTML = '';
                plans.forEach(p => {
                    const tr = document.createElement('tr');
                    tr.innerHTML = `
                        <td data-field="plan_id">${p.id || ''}</td>
                        <td>${p.name || ''}</td>
                        <td>${p.price_usd ?? ''}</td>
                        <td>${p.credits_per_month ?? p.credits ?? ''}</td>
                        <td><input type="text" class="input input-sm input-bordered" data-field="variant_id" value="${variantMap[p.id] || ''}" placeholder="e.g., 933399" /></td>
                    `;
                    tbody.appendChild(tr);
                });
            }

            // Carica impostazioni globali rollout (UI minimale, se presente nei template)
            const fallbackToggle = document.getElementById('rollout_fallback_enabled');
            if (fallbackToggle) fallbackToggle.checked = !!config.rollout_fallback_enabled;
            const defType = document.getElementById('default_rollover_type');
            const defValue = document.getElementById('default_rollover_value');
            const defMax = document.getElementById('default_rollover_max');
            if (defType && defValue) {
                const rule = config.default_rollover_rule || {};
                defType.value = rule.type || 'fixed';
                defValue.value = rule.value ?? '';
                if (defMax) defMax.value = rule.max_carryover ?? '';
            }

            // BI: mostra costo stimato (se presenti i campi nella pagina)
            const costInput = document.getElementById('signup_credits_cost');
            const newUsersInput = document.getElementById('bi_monthly_new_users');
            const line = document.getElementById('signup_credits_forecast_line');
            const out = document.getElementById('signup_credits_forecast_cost');
            if (costInput && newUsersInput && line && out) {
                const updateForecast = () => {
                    const cost = parseFloat(costInput.value) || 0;
                    const users = parseInt(newUsersInput.value) || 0;
                    const total = cost * users;
                    out.textContent = `$${total.toFixed(2)}`;
                    line.style.display = 'block';
                };
                costInput.addEventListener('input', updateForecast);
                newUsersInput.addEventListener('input', updateForecast);
                updateForecast();
            }
        } catch (error) {
            console.error('Load provider config error:', error);
            Utils.showToast('Failed to load provider configuration: ' + error.message, 'error');
        }
    },
    
    /**
     * Salva configurazione provider
     */
    async saveBillingProviderConfig() {
        try {
            // Costruisci la mappa SOLO per valori non vuoti
            const variantMap = {};
            document.querySelectorAll('#variant-map-table tr').forEach(tr => {
                const planId = tr.querySelector('[data-field="plan_id"]').textContent.trim();
                const variant = tr.querySelector('input[data-field="variant_id"]').value.trim();
                if (planId && variant) variantMap[planId] = variant;
            });

            // 1) Carica configurazione esistente per evitare overwrite
            const existing = await API.get('/core/v1/admin/billing/config');
            const base = existing.config || {};

            // 2) Applica provider e sotto-config a livello TOP-LEVEL (no nested config)
            const lsBlock = {
                ...(base.lemonsqueezy || {}),
                store_id: document.getElementById('ls_store').value.trim(),
                test_mode: document.getElementById('ls_test_mode').checked,
                ...(Object.keys(variantMap).length > 0 ? { variant_map: variantMap } : {})
            };

            const updated = {
                ...base,
                provider: 'lemonsqueezy',
                lemonsqueezy: lsBlock
            };

            // 3) Salva
            await API.put('/core/v1/admin/billing/config', updated);
            Utils.showToast('Provider configuration saved successfully!', 'success');
        } catch (error) {
            console.error('Save provider config error:', error);
            Utils.showToast('Failed to save provider configuration: ' + error.message, 'error');
        }
    },

    /**
     * Test connessione provider
     */
    async testProviderConnection() {
        try {
            const res = await API.post('/core/v1/admin/credentials/test?provider=lemonsqueezy');
            const ok = !!res?.success;
            const msg = ok ? (`Connection OK${res.user ? ' as ' + res.user : ''}`) : (`Test failed${res?.error ? ': ' + res.error : ''}`);
            Utils.showToast(msg, ok ? 'success' : 'error');
        } catch (error) {
            Utils.showToast('Failed to test connection: ' + (error.message || 'Error'), 'error');
        }
    },
    
    /**
     * Carica configurazione crediti
     */
    async loadCreditsConfig() {
        try {
            const pricingConfig = await API.get('/core/v1/admin/pricing/config');
            
            // Signup Credits
            const signupCreditsInput = document.getElementById('signup_initial_credits');
            if (signupCreditsInput) signupCreditsInput.value = pricingConfig.signup_initial_credits || 100;
            
            const signupCostInput = document.getElementById('signup_credits_cost');
            if (signupCostInput) signupCostInput.value = pricingConfig.signup_initial_credits_cost_usd || 0;
            
            // Rollout Settings
            const intervalSelect = document.getElementById('rollout_interval');
            if (intervalSelect) intervalSelect.value = pricingConfig.rollout_interval || 'monthly';
            
            const creditsInput = document.getElementById('rollout_credits');
            if (creditsInput) creditsInput.value = pricingConfig.rollout_credits_per_period || 1000;
            
            const maxInput = document.getElementById('rollout_max');
            if (maxInput) maxInput.value = pricingConfig.rollout_max_credits_rollover || 2000;
            
            const percentageInput = document.getElementById('rollout_percentage');
            if (percentageInput) percentageInput.value = pricingConfig.rollout_percentage || 100;
        } catch (error) {
            console.error('Failed to load credits config:', error);
        }
    },
    
    /**
     * Salva configurazione crediti e rollout
     */
    async saveCreditsAndRolloutConfig() {
        try {
            const existingConfig = await API.get('/core/v1/admin/pricing/config');
            
            const updatedConfig = {
                ...existingConfig,
                signup_initial_credits: parseFloat(document.getElementById('signup_initial_credits').value) || 100,
                signup_initial_credits_cost_usd: parseFloat(document.getElementById('signup_credits_cost').value) || 0,
                rollout_interval: document.getElementById('rollout_interval').value || 'monthly',
                rollout_credits_per_period: parseInt(document.getElementById('rollout_credits').value) || 1000,
                rollout_max_credits_rollover: parseInt(document.getElementById('rollout_max').value) || 2000,
                rollout_percentage: parseFloat(document.getElementById('rollout_percentage').value) || 100
            };
            
            await API.put('/core/v1/admin/pricing/config', updatedConfig);
            Utils.showToast('Credits and rollout configuration saved successfully!', 'success');

            // Salva anche le impostazioni globali di rollout se presenti (accordion globale)
            const billingConfig = await API.get('/core/v1/admin/billing/config');
            const globalCfg = billingConfig.config || {};
            const fallbackToggle = document.getElementById('rollout_fallback_enabled');
            const defType = document.getElementById('default_rollover_type');
            const defValue = document.getElementById('default_rollover_value');
            const defMax = document.getElementById('default_rollover_max');
            if (fallbackToggle || defType || defValue || defMax) {
                globalCfg.rollout_fallback_enabled = !!(fallbackToggle && fallbackToggle.checked);
                globalCfg.default_rollover_rule = {
                    type: defType ? (defType.value || 'fixed') : 'fixed',
                    value: defValue ? (parseFloat(defValue.value) || 0) : 0,
                    ...(defMax && defMax.value ? { max_carryover: parseFloat(defMax.value) || 0 } : {})
                };
                await API.put('/core/v1/admin/billing/config', globalCfg);
                Utils.showToast('Global rollout settings saved', 'success');
            }

            // BI: salvataggio stima utenti/mese e costo unitario nel pricing (solo BI)
            const costInput = document.getElementById('signup_credits_cost');
            const newUsersInput = document.getElementById('bi_monthly_new_users');
            if (costInput || newUsersInput) {
                const pricingCfg = await API.get('/core/v1/admin/pricing/config');
                const biUpdated = {
                    ...pricingCfg,
                    signup_initial_credits_cost_usd: parseFloat(costInput?.value || pricingCfg.signup_initial_credits_cost_usd || 0),
                    bi_monthly_new_users: parseInt(newUsersInput?.value || pricingCfg.bi_monthly_new_users || 0)
                };
                await API.put('/core/v1/admin/pricing/config', biUpdated);
                Utils.showToast('BI forecast saved', 'success');
            }
        } catch (error) {
            console.error('Save credits config error:', error);
            Utils.showToast('Failed to save credits configuration: ' + error.message, 'error');
        }
    },
    
    /**
     * Genera checkout
     */
    async generateCheckout() {
        try {
            const userId = document.getElementById('checkout_user').value;
            const planId = document.getElementById('checkout_plan').value;
            
            if (!userId || !planId) {
                Utils.showToast('Please select both user and plan', 'warning');
                return;
            }
            
            const url = `/core/v1/admin/billing/checkout?user_id=${userId}&plan_id=${planId}`;
            const result = await API.post(url);
            
            const output = document.getElementById('checkout-result');
            if (result.checkout?.checkout_url) {
                output.innerHTML = `
                    <div class="alert alert-success">
                        <i class="fas fa-check-circle"></i>
                        <div>
                            <h3 class="font-bold">Checkout created!</h3>
                            <p>Click below to open the checkout page</p>
                        </div>
                        <a href="${result.checkout.checkout_url}" target="_blank" class="btn btn-sm">Open Checkout</a>
                    </div>
                `;
            } else {
                output.innerHTML = `<pre class="json">${JSON.stringify(result, null, 2)}</pre>`;
            }
        } catch (error) {
            Utils.showToast('Failed to generate checkout', 'error');
        }
    },
    
    /**
     * Carica dati checkout
     */
    async loadCheckoutData() {
        try {
            // Carica utenti
            const users = await API.get('/core/v1/admin/users?limit=100');
            const userSelect = document.getElementById('checkout_user');
            if (userSelect) {
                userSelect.innerHTML = '<option value="">-- Select User --</option>';
                users.users.forEach(user => {
                    const opt = document.createElement('option');
                    opt.value = user.id;
                    opt.textContent = `${user.email} (${user.credits || 0} credits)`;
                    userSelect.appendChild(opt);
                });
            }
            
            // Carica piani dalla config unificata
            const billingConfig = await API.get('/core/v1/admin/billing/config');
            const plans = (billingConfig.config && billingConfig.config.plans) ? billingConfig.config.plans : [];
            const planSelect = document.getElementById('checkout_plan');
            if (planSelect) {
                planSelect.innerHTML = '<option value="">-- Select Plan --</option>';
                plans.forEach(plan => {
                    const opt = document.createElement('option');
                    opt.value = plan.id;
                    opt.textContent = `${plan.name} ($${plan.price_usd})`;
                    planSelect.appendChild(opt);
                });
            }
        } catch (error) {
            console.error('Failed to load checkout data:', error);
        }
    }
};
