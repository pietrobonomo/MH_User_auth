/**
 * Componente Observability
 */
const ObservabilityComponent = {
    async loadAILogs() {
        try {
            const logs = await API.get('/core/v1/admin/observability/openrouter/logs?limit=20');
            const output = document.getElementById('ai-logs-output');
            output.innerHTML = `<pre class="json">${JSON.stringify(logs, null, 2)}</pre>`;
        } catch (error) {
            Utils.showToast('Failed to load AI logs', 'error');
        }
    },
    
    async loadAISnapshot() {
        try {
            const snapshot = await API.get('/core/v1/admin/observability/openrouter/snapshot');
            const container = document.getElementById('ai-snapshot-container');
            
            if (!snapshot || typeof snapshot !== 'object') {
                container.innerHTML = '<p class="text-gray-500">No snapshot data available</p>';
                return;
            }
            
            // Estrai dati dal snapshot
            const usage = snapshot.usage || {};
            const costs = snapshot.costs || {};
            const models = snapshot.models || [];
            
            container.innerHTML = `
                <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                    <div class="stat bg-base-100 rounded-lg shadow">
                        <div class="stat-title">Total Requests</div>
                        <div class="stat-value">${usage.total_requests || 0}</div>
                    </div>
                    <div class="stat bg-base-100 rounded-lg shadow">
                        <div class="stat-title">Total Cost</div>
                        <div class="stat-value">$${(costs.total_cost_usd || 0).toFixed(4)}</div>
                    </div>
                    <div class="stat bg-base-100 rounded-lg shadow">
                        <div class="stat-title">Models Used</div>
                        <div class="stat-value">${models.length}</div>
                    </div>
                </div>
                
                <h3 class="text-lg font-semibold mb-2">Model Usage</h3>
                <div class="overflow-x-auto">
                    <table class="table table-sm">
                        <thead>
                            <tr>
                                <th>Model</th>
                                <th>Requests</th>
                                <th>Tokens</th>
                                <th>Cost</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${models.map(m => `
                                <tr>
                                    <td>${m.model || 'Unknown'}</td>
                                    <td>${m.requests || 0}</td>
                                    <td>${m.total_tokens || 0}</td>
                                    <td>$${(m.cost_usd || 0).toFixed(4)}</td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>
            `;
        } catch (error) {
            Utils.showToast('Failed to load AI snapshot', 'error');
        }
    },

    async loadCreditsLedger() {
        try {
            const userId = document.getElementById('ledger_user_filter').value.trim();
            const url = userId 
                ? `/core/v1/admin/observability/credits/ledger?user_id=${userId}&limit=50`
                : '/core/v1/admin/observability/credits/ledger?limit=50';
            
            const ledger = await API.get(url);
            const output = document.getElementById('credits-ledger-output');
            output.innerHTML = `<pre class="json">${JSON.stringify(ledger, null, 2)}</pre>`;
        } catch (error) {
            Utils.showToast('Failed to load credits ledger', 'error');
        }
    },

    async previewRollout() {
        try {
            const preview = await API.post('/core/v1/admin/observability/rollout/preview');
            const output = document.getElementById('rollout-output');
            output.innerHTML = `<pre class="json">${JSON.stringify(preview, null, 2)}</pre>`;
        } catch (error) {
            Utils.showToast('Failed to preview rollout', 'error');
        }
    },

    async runRollout() {
        if (!confirm('Are you sure you want to run the rollout?')) return;
        
        try {
            const result = await API.post('/core/v1/admin/observability/rollout/run');
            Utils.showToast('Rollout completed', 'success');
            const output = document.getElementById('rollout-output');
            output.innerHTML = `<pre class="json">${JSON.stringify(result, null, 2)}</pre>`;
        } catch (error) {
            Utils.showToast('Failed to run rollout', 'error');
        }
    }
};