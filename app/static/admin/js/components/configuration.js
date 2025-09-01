/**
 * Componente Configuration
 */
const ConfigurationComponent = {
    async upsertFlowConfig() {
        try {
            const config = {
                app_id: document.getElementById('flow_app_id').value.trim() || 'default',
                flow_key: document.getElementById('flow_key').value.trim(),
                flow_id: document.getElementById('flow_id').value.trim(),
                node_names: document.getElementById('node_names').value.split(',').map(s => s.trim()).filter(Boolean)
            };
            
            await API.post('/core/v1/admin/flow-configs', config);
            
            Utils.showToast('Flow configuration saved', 'success');
        } catch (error) {
            Utils.showToast('Failed to save flow configuration', 'error');
        }
    },

    async rotateCredential(credentialKey) {
        const newValue = prompt(`Enter new value for ${credentialKey}:`);
        if (!newValue) return;
        
        try {
            await API.post('/core/v1/admin/credentials/rotate', {
                provider: 'lemonsqueezy',
                credential_key: credentialKey,
                new_value: newValue
            });
            
            Utils.showToast(`${credentialKey} rotated successfully`, 'success');
        } catch (error) {
            Utils.showToast('Failed to rotate credential', 'error');
        }
    },
    
    async saveScenario() {
        // Placeholder per future implementazioni
        Utils.showToast('Scenario saved', 'info');
    },
    
    async loadScenario() {
        // Placeholder per future implementazioni
        Utils.showToast('Scenario loaded', 'info');
    },
    
    async exportScenario() {
        // Placeholder per future implementazioni
        Utils.showToast('Scenario exported', 'info');
    }
};