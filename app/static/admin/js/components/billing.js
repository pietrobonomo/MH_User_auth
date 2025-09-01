/**
 * Componente Billing & Plans
 */
const BillingComponent = {
    /**
     * Carica dati piani
     */
    async loadPlansData() {
        try {
            // Prima prova a caricare dalla configurazione billing
            let plans = [];
            try {
                const billingConfig = await API.get('/core/v1/admin/billing/config');
                if (billingConfig.config && billingConfig.config.plans) {
                    plans = billingConfig.config.plans;
                }
            } catch (configError) {
                console.log('No billing config found, trying plans endpoint');
            }
            
            // Se non ci sono piani nella config, prova l'endpoint plans
            if (plans.length === 0) {
                try {
                    const plansResp = await API.get('/core/v1/billing/plans');
                    plans = plansResp.plans || plansResp || [];
                } catch (plansError) {
                    console.log('No plans found from plans endpoint');
                }
            }
            
            const tbody = document.getElementById('plans-table');
            if (tbody) {
                tbody.innerHTML = '';
                if (plans.length === 0) {
                    // Aggiungi alcuni piani di default
                    const defaultPlans = [
                        { id: 'starter', name: 'Starter', type: 'subscription', price_usd: 9.99, credits_per_month: 1000 },
                        { id: 'pro', name: 'Professional', type: 'subscription', price_usd: 29.99, credits_per_month: 5000 },
                        { id: 'enterprise', name: 'Enterprise', type: 'subscription', price_usd: 99.99, credits_per_month: 20000 }
                    ];
                    defaultPlans.forEach(plan => this.addPlanTableRow(plan));
                    Utils.showToast('Loaded default plans - click Save to persist', 'info');
                } else {
                    plans.forEach(plan => this.addPlanTableRow(plan));
                }
            }
        } catch (error) {
            console.error('Failed to load plans data:', error);
            Utils.showToast('Failed to load plans', 'error');
        }
    },
    
    /**
     * Aggiungi riga piano
     */
    addPlanTableRow(plan) {
        const tbody = document.getElementById('plans-table');
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td><input type="text" class="input input-sm input-bordered" value="${plan.id || ''}" /></td>
            <td><input type="text" class="input input-sm input-bordered" value="${plan.name || ''}" /></td>
            <td>
                <select class="select select-sm select-bordered">
                    <option value="subscription" ${plan.type === 'subscription' ? 'selected' : ''}>Subscription</option>
                    <option value="one_time" ${plan.type === 'one_time' ? 'selected' : ''}>One Time</option>
                </select>
            </td>
            <td><input type="number" class="input input-sm input-bordered" value="${plan.price_usd || ''}" step="0.01" /></td>
            <td><input type="number" class="input input-sm input-bordered" value="${plan.credits || plan.credits_per_month || ''}" /></td>
            <td><button class="btn btn-sm btn-primary" onclick="BillingComponent.saveSinglePlan(this)">Save</button></td>
            <td><button class="btn btn-sm btn-error" onclick="this.closest('tr').remove()">Remove</button></td>
        `;
        tbody.appendChild(tr);
    },
    
    /**
     * Salva singolo piano
     */
    async saveSinglePlan(button) {
        const row = button.closest('tr');
        const inputs = row.querySelectorAll('input, select');
        const plan = {
            id: inputs[0].value.trim(),
            name: inputs[1].value.trim(),
            type: inputs[2].value,
            price_usd: parseFloat(inputs[3].value) || 0,
            credits_per_month: parseInt(inputs[4].value) || 0
        };
        
        // Validazione
        if (!plan.id) {
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
            const existingIndex = config.plans.findIndex(p => p.id === plan.id);
            if (existingIndex >= 0) {
                config.plans[existingIndex] = plan;
            } else {
                config.plans.push(plan);
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
            
            Utils.showToast(`Plan "${plan.name}" saved successfully`, 'success');
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
            
            // Carica mapping varianti
            const plansResp = await API.get('/core/v1/billing/plans');
            const plans = plansResp.plans || plansResp || [];
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
            const variantMap = {};
            document.querySelectorAll('#variant-map-table tr').forEach(tr => {
                const planId = tr.querySelector('[data-field="plan_id"]').textContent.trim();
                const variant = tr.querySelector('input[data-field="variant_id"]').value.trim();
                if (planId) variantMap[planId] = variant || '';
            });
            
            const config = {
                provider: "lemonsqueezy",
                config: {
                    lemonsqueezy: {
                        store_id: document.getElementById('ls_store').value.trim(),
                        test_mode: document.getElementById('ls_test_mode').checked,
                        variant_map: variantMap
                    }
                }
            };
            
            await API.put('/core/v1/admin/billing/config', config);
            Utils.showToast('Provider configuration saved successfully!', 'success');
        } catch (error) {
            console.error('Save provider config error:', error);
            Utils.showToast('Failed to save provider configuration: ' + error.message, 'error');
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
            
            // Carica piani
            const plansResp = await API.get('/core/v1/billing/plans');
            const plans = plansResp.plans || plansResp || [];
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
