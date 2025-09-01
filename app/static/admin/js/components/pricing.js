/**
 * Componente Pricing & Business
 */
const PricingComponent = {
    /**
     * Carica la configurazione pricing
     */
    async loadPricingConfig() {
        try {
            const config = await API.get('/core/v1/admin/pricing/config');
            
            // Popola i campi del form
            const fields = {
                'rev_target': config.monthly_revenue_target_usd || 0,
                'usd_to_credits': config.usd_to_credits || 100,
                'margin_mult': config.target_margin_multiplier || 2,
                'min_op_cost': config.minimum_operation_cost_credits || 0.01
            };
            
            for (const [id, value] of Object.entries(fields)) {
                const element = document.getElementById(id);
                if (element) element.value = value;
            }
            
            // Carica fixed costs se presenti
            const fixedCostsTable = document.getElementById('fixed-costs-table');
            if (fixedCostsTable) {
                this.loadFixedCosts(config.fixed_monthly_costs_usd || []);
            }
            
            // Aggiorna simulator se presente
            if (document.getElementById('simulator-output')) {
                this.simulatePricing(config);
            }
            
            return config;
        } catch (error) {
            console.error('Failed to load pricing config:', error);
            Utils.showToast('Failed to load pricing configuration', 'error');
        }
    },
    
    /**
     * Salva la configurazione pricing
     */
    async savePricingConfig() {
        try {
            // Leggi config esistente
            const existing = await API.get('/core/v1/admin/pricing/config');
            
            // Raccogli dati dal form
            const updated = {
                ...existing,
                monthly_revenue_target_usd: parseFloat(document.getElementById('rev_target').value) || 1000,
                usd_to_credits: parseFloat(document.getElementById('usd_to_credits').value) || 100,
                target_margin_multiplier: parseFloat(document.getElementById('margin_mult').value) || 2,
                minimum_operation_cost_credits: parseFloat(document.getElementById('min_op_cost').value) || 0.01
            };
            
            await API.put('/core/v1/admin/pricing/config', updated);
            Utils.showToast('Pricing configuration saved successfully!', 'success');
            
            // Aggiorna simulator
            if (document.getElementById('simulator-output')) {
                this.simulatePricing(updated);
            }
        } catch (error) {
            console.error('Save pricing config error:', error);
            Utils.showToast('Failed to save configuration: ' + error.message, 'error');
        }
    },
    
    /**
     * Carica app affordability
     */
    async loadAppAffordability() {
        try {
            const appIdsResp = await API.get('/core/v1/admin/app-ids');
            const appIds = appIdsResp.app_ids || [];
            
            console.log('Found app IDs:', appIds);
            
            const tbody = document.getElementById('app-affordability-table');
            if (!tbody) return;
            
            tbody.innerHTML = '';
            
            if (appIds.length === 0) {
                tbody.innerHTML = `
                    <tr>
                        <td colspan="4" class="text-center text-base-content/60 py-8">
                            <div>
                                <i class="fas fa-info-circle text-2xl mb-2"></i>
                                <p class="font-semibold">No apps configured yet</p>
                                <p class="text-sm">Apps will appear here once you configure flow mappings</p>
                                <p class="text-sm text-info">💡 Go to Configuration → Flow Mappings to add apps</p>
                            </div>
                        </td>
                    </tr>
                `;
                return;
            }
            
            // Carica configurazione per ogni app
            const config = await API.get('/core/v1/admin/pricing/config');
            
            for (const appId of appIds) {
                let minCredits = 0;
                if (config.flow_costs_usd && typeof config.flow_costs_usd === 'object' && appId in config.flow_costs_usd) {
                    minCredits = parseFloat(config.flow_costs_usd[appId]) || 0;
                }
                
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td><span class="font-mono">${appId}</span></td>
                    <td>
                        <input type="number" class="input input-sm input-bordered" 
                               data-app="${appId}" value="${minCredits}" 
                               step="0.01" placeholder="0" />
                    </td>
                    <td>
                        <span class="badge ${minCredits > 0 ? 'badge-success' : 'badge-warning'}">
                            ${minCredits > 0 ? 'Protected' : 'No Check'}
                        </span>
                    </td>
                    <td>
                        <button class="btn btn-xs btn-ghost" onclick="PricingComponent.testAppAffordability('${appId}')">
                            <i class="fas fa-test-tube"></i> Test
                        </button>
                    </td>
                `;
                tbody.appendChild(tr);
            }
            
            Utils.showToast(`Loaded ${appIds.length} app configurations`, 'info');
        } catch (error) {
            console.error('Failed to load app affordability:', error);
            Utils.showToast('Failed to load app affordability: ' + error.message, 'error');
        }
    },
    
    /**
     * Salva app affordability
     */
    async saveAppAffordability() {
        try {
            const inputs = document.querySelectorAll('#app-affordability-table input[data-app]');
            const existingConfig = await API.get('/core/v1/admin/pricing/config');
            const flowMap = { ...(existingConfig.flow_costs_usd || {}) };
            
            inputs.forEach(input => {
                const appId = input.dataset.app;
                const minCredits = parseFloat(input.value) || 0;
                flowMap[appId] = minCredits;
            });
            
            const updatedConfig = { 
                ...existingConfig, 
                flow_costs_usd: flowMap, 
                minimum_affordability_per_app: {} 
            };
            
            await API.put('/core/v1/admin/pricing/config', updatedConfig);
            
            // Aggiorna badge
            inputs.forEach(input => {
                const minCredits = parseFloat(input.value) || 0;
                const row = input.closest('tr');
                const badge = row?.querySelector('.badge');
                if (badge) {
                    badge.className = `badge ${minCredits > 0 ? 'badge-success' : 'badge-warning'}`;
                    badge.textContent = minCredits > 0 ? 'Protected' : 'No Check';
                }
            });
            
            Utils.showToast(`Saved affordability settings for ${inputs.length} apps`, 'success');
        } catch (error) {
            console.error('Save app affordability error:', error);
            Utils.showToast('Failed to save affordability settings: ' + error.message, 'error');
        }
    },
    
    /**
     * Test app affordability
     */
    async testAppAffordability(appId) {
        try {
            const config = await API.get('/core/v1/admin/pricing/config');
            const minCredits = (config.flow_costs_usd && typeof config.flow_costs_usd === 'object')
              ? (parseFloat(config.flow_costs_usd[appId]) || 0)
              : 0;
            Utils.showToast(`App "${appId}" requires minimum ${minCredits} credits for execution`, 'info');
        } catch (error) {
            Utils.showToast(`Failed to test app "${appId}": ${error.message}`, 'error');
        }
    },
    
    /**
     * Simula pricing
     */
    simulatePricing(config) {
        // Calcola fixed costs
        let fixed = 0;
        const fixedTable = document.getElementById('fixed-costs-table');
        if (fixedTable) {
            fixedTable.querySelectorAll('tr').forEach(row => {
                const inputs = row.querySelectorAll('input');
                if (inputs.length >= 2) {
                    const cost = parseFloat(inputs[1].value) || 0;
                    fixed += cost;
                }
            });
        } else if (Array.isArray(config?.fixed_monthly_costs_usd)) {
            fixed = config.fixed_monthly_costs_usd.reduce((sum, c) => sum + (parseFloat(c.cost_usd) || 0), 0);
        }
        
        // Leggi valori correnti o usa config
        let revenue = parseFloat(document.getElementById('rev_target')?.value);
        if (Number.isNaN(revenue)) revenue = config?.monthly_revenue_target_usd || 0;
        
        let marginMult = parseFloat(document.getElementById('margin_mult')?.value);
        if (Number.isNaN(marginMult)) marginMult = config?.target_margin_multiplier || 0;
        
        let usdToCredits = parseFloat(document.getElementById('usd_to_credits')?.value);
        if (Number.isNaN(usdToCredits)) usdToCredits = config?.usd_to_credits || 0;
        
        const overheadPerc = revenue > 0 ? (fixed / revenue) : 0;
        const overheadMult = 1 + overheadPerc;
        const finalCreditMult = overheadMult * marginMult * usdToCredits;
        const usdMult = overheadMult * marginMult;
        
        const output = document.getElementById('simulator-output');
        if (output) {
            output.innerHTML = `
                <div class="stats stats-vertical lg:stats-horizontal shadow">
                    <div class="stat">
                        <div class="stat-title">Overhead Multiplier</div>
                        <div class="stat-value text-primary">${overheadMult.toFixed(2)}x</div>
                    </div>
                    <div class="stat">
                        <div class="stat-title">USD Multiplier</div>
                        <div class="stat-value text-secondary">${usdMult.toFixed(2)}x</div>
                    </div>
                    <div class="stat">
                        <div class="stat-title">Credit Multiplier</div>
                        <div class="stat-value text-accent">${finalCreditMult.toFixed(2)}x</div>
                    </div>
                </div>
            `;
        }
    },
    
    /**
     * Carica fixed costs
     */
    loadFixedCosts(costs) {
        const tbody = document.getElementById('fixed-costs-table');
        if (!tbody) return;
        
        tbody.innerHTML = '';
        
        if (costs.length === 0) {
            // Default costs
            const defaultCosts = [
                { name: "Infrastructure", cost_usd: 50 },
                { name: "Payment Processor", cost_usd: 50 },
                { name: "Business & Marketing", cost_usd: 150 },
                { name: "Support & Maintenance", cost_usd: 80 },
                { name: "Legal & Accounting", cost_usd: 50 }
            ];
            
            defaultCosts.forEach(cost => this.addFixedCostRow(cost.name, cost.cost_usd));
            Utils.showToast('Loaded default fixed costs - click Save to persist', 'info');
        } else {
            costs.forEach(cost => this.addFixedCostRow(cost.name, cost.cost_usd));
            Utils.showToast(`Loaded ${costs.length} fixed costs`, 'success');
        }
        
        this.updateOverheadPreview();
    },
    
    /**
     * Aggiungi riga fixed cost
     */
    addFixedCostRow(name = '', cost = '') {
        const tbody = document.getElementById('fixed-costs-table');
        if (!tbody) return;
        
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td><input type="text" class="input input-sm input-bordered" value="${name}" placeholder="e.g., Infrastructure" /></td>
            <td><input type="number" class="input input-sm input-bordered" value="${cost}" step="0.01" placeholder="50.00" /></td>
            <td><button class="btn btn-sm btn-error" onclick="this.closest('tr').remove(); PricingComponent.updateOverheadPreview()">Remove</button></td>
        `;
        
        // Aggiungi listener per aggiornare preview
        tr.querySelectorAll('input').forEach(input => {
            input.addEventListener('input', () => this.updateOverheadPreview());
        });
        
        tbody.appendChild(tr);
    },
    
    /**
     * Aggiorna overhead preview
     */
    updateOverheadPreview(config = null) {
        try {
            const revenueTarget = parseFloat(document.getElementById('rev_target')?.value) || 10000;
            
            let totalFixedCosts = 0;
            const tbody = document.getElementById('fixed-costs-table');
            if (tbody) {
                tbody.querySelectorAll('tr').forEach(row => {
                    const inputs = row.querySelectorAll('input');
                    if (inputs.length >= 2) {
                        const cost = parseFloat(inputs[1].value) || 0;
                        totalFixedCosts += cost;
                    }
                });
            }
            
            if (config && config.fixed_monthly_costs_usd) {
                totalFixedCosts = config.fixed_monthly_costs_usd.reduce((sum, c) => sum + (c.cost_usd || 0), 0);
            }
            
            const overheadMultiplier = revenueTarget > 0 ? (1 + (totalFixedCosts / revenueTarget)) : 1.0;
            
            const totalEl = document.getElementById('total-fixed-costs');
            if (totalEl) totalEl.textContent = Utils.formatCurrency(totalFixedCosts);
            
            const multiplierEl = document.getElementById('overhead-multiplier');
            if (multiplierEl) multiplierEl.textContent = `${overheadMultiplier.toFixed(2)}x`;
            
        } catch (error) {
            console.error('Failed to update overhead preview:', error);
        }
    },
    
    /**
     * Salva fixed costs
     */
    async saveFixedCosts() {
        try {
            const existingConfig = await API.get('/core/v1/admin/pricing/config');
            
            const fixedCosts = [];
            const tbody = document.getElementById('fixed-costs-table');
            if (tbody) {
                tbody.querySelectorAll('tr').forEach(row => {
                    const inputs = row.querySelectorAll('input');
                    if (inputs.length >= 2) {
                        const name = inputs[0].value.trim();
                        const cost = parseFloat(inputs[1].value) || 0;
                        if (name && cost > 0) {
                            fixedCosts.push({ name, cost_usd: cost });
                        }
                    }
                });
            }
            
            const updatedConfig = {
                ...existingConfig,
                fixed_monthly_costs_usd: fixedCosts
            };
            
            await API.put('/core/v1/admin/pricing/config', updatedConfig);
            Utils.showToast('Fixed costs saved successfully!', 'success');
            this.updateOverheadPreview();
        } catch (error) {
            console.error('Save fixed costs error:', error);
            Utils.showToast('Failed to save fixed costs: ' + error.message, 'error');
        }
    }
};
