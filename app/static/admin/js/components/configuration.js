/**
 * Componente Configuration
 */
const ConfigurationComponent = {
async loadFlowMappings() {
            try {
                const container = document.getElementById('flow-mappings-container');
                if (!container) return;
                
                // Ottieni tutte le mappings da Supabase
                const allFlows = await API.get('/core/v1/admin/flow-configs/all?app_id=*');
                const flows = allFlows?.items || [];
                
                if (flows.length === 0) {
                    container.innerHTML = '<div class="alert alert-info">Nessuna mapping trovata nel database.</div>';
                    return;
                }
                
                // Raggruppa per app_id
                const byApp = {};
                flows.forEach(f => {
                    if (!byApp[f.app_id]) byApp[f.app_id] = [];
                    byApp[f.app_id].push(f);
                });
                
                // Genera accordion per ogni app
                const html = Object.keys(byApp).sort().map(appId => {
                    const appFlows = byApp[appId];
                    return `
                        <div class="collapse collapse-arrow bg-base-100 border">
                            <input type="checkbox" />
                            <div class="collapse-title text-lg font-medium">
                                <i class="fas fa-project-diagram mr-2"></i>
                                ${appId} <span class="badge badge-ghost">${appFlows.length} flows</span>
                            </div>
                            <div class="collapse-content">
                                <div class="overflow-x-auto">
                                    <table class="table table-sm w-full">
                                        <thead>
                                            <tr>
                                                <th>Flow Key</th>
                                                <th>Flow ID</th>
                                                <th>Node Names</th>
                                                <th>Conversational</th>
                                                <th>Actions</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            ${appFlows.map(f => {
                                                const nodes = Array.isArray(f.node_names) ? f.node_names.join(',') : '';
                                                const isConv = f.is_conversational ? true : false;
                                                return `
                                                    <tr>
                                                        <td><strong>${f.flow_key}</strong></td>
                                                        <td><code class="text-xs">${f.flow_id}</code></td>
                                                        <td><span class="text-xs opacity-70">${nodes}</span></td>
                                                        <td>
                                                            ${isConv ? '<span class="badge badge-success">🔗 Yes</span>' : '<span class="badge badge-ghost">No</span>'}
                                                        </td>
                                                        <td>
                                                            <button class="btn btn-xs btn-primary mr-1" 
                                                                onclick="ConfigurationComponent.editFlowMapping('${f.app_id}','${f.flow_key}','${f.flow_id}','${nodes}',${isConv})">
                                                                Edit
                                                            </button>
                                                            <button class="btn btn-xs btn-error" 
                                                                onclick="ConfigurationComponent.deleteFlowMapping('${f.app_id}','${f.flow_key}')">
                                                                Delete
                                                            </button>
                                                        </td>
                                                    </tr>
                                                `;
                                            }).join('')}
                                        </tbody>
                                    </table>
                                </div>
                            </div>
                        </div>
                    `;
                }).join('');
                
                container.innerHTML = html;
            } catch (e) {
                console.warn('loadFlowMappings error', e);
                const container = document.getElementById('flow-mappings-container');
                if (container) container.innerHTML = `<div class="alert alert-error">Errore caricamento: ${e.message}</div>`;
            }
        },
        editFlowMapping(appId, flowKey, flowId, nodeNames, isConversational) {
            const appField = document.getElementById('new_flow_app_id');
            const fk = document.getElementById('new_flow_key');
            const fid = document.getElementById('new_flow_id');
            const nn = document.getElementById('new_node_names');
            const conv = document.getElementById('new_is_conversational');
            if (appField) appField.value = appId;
            if (fk) fk.value = flowKey;
            if (fid) fid.value = flowId;
            if (nn) nn.value = nodeNames;
            if (conv) conv.checked = isConversational || false;
        },
        async deleteFlowMapping(appId, flowKey) {
            if (!flowKey) return;
            if (!confirm(`Eliminare la mapping '${appId}/${flowKey}'?`)) return;
            try {
                await API.delete(`/core/v1/admin/flow-configs?app_id=${encodeURIComponent(appId)}&flow_key=${encodeURIComponent(flowKey)}`);
                Utils.showToast('Mapping eliminata', 'success');
                setTimeout(() => this.loadFlowMappings(), 300);
            } catch (e) {
                Utils.showToast('Eliminazione fallita: ' + (e.message||'Error'), 'error');
            }
        },
        async populateAppIds() {
            try {
                // prendi lista app_id distinte da Supabase
                const resp = await API.get('/core/v1/admin/app-ids');
                const apps = (resp.app_ids || []).sort();
                const sel = document.getElementById('flow_app_id_select');
                const hidden = document.getElementById('flow_app_id');
                if (!sel || !hidden) return;
                sel.innerHTML = apps.map(a => `<option value="${a}">${a}</option>`).join('');
                const current = hidden.value || apps[0] || 'default';
                sel.value = current;
                hidden.value = current;
                sel.onchange = () => {
                    hidden.value = sel.value;
                    ConfigurationComponent.loadFlowMappings();
                };
            } catch (e) { console.warn('populateAppIds error', e); }
        },
async addNewFlowMapping() {
            try {
                const convCheckbox = document.getElementById('new_is_conversational');
                const config = {
                    app_id: document.getElementById('new_flow_app_id').value.trim(),
                    flow_key: document.getElementById('new_flow_key').value.trim(),
                    flow_id: document.getElementById('new_flow_id').value.trim(),
                    node_names: document.getElementById('new_node_names').value.split(',').map(s => s.trim()).filter(Boolean),
                    is_conversational: convCheckbox ? convCheckbox.checked : false
                };
                
                if (!config.app_id || !config.flow_key || !config.flow_id) {
                    Utils.showToast('App ID, Flow Key e Flow ID sono obbligatori', 'error');
                    return;
                }
                
                await API.post('/core/v1/admin/flow-configs', config);
                
                Utils.showToast('Flow mapping salvata', 'success');
                
                // Clear form
                document.getElementById('new_flow_app_id').value = '';
                document.getElementById('new_flow_key').value = '';
                document.getElementById('new_flow_id').value = '';
                document.getElementById('new_node_names').value = '';
                if (convCheckbox) convCheckbox.checked = false;
                
                setTimeout(() => this.loadFlowMappings(), 300);
            } catch (error) {
                Utils.showToast('Errore salvataggio: ' + (error.message || 'Error'), 'error');
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
    },

    // Setup Wizard Integration
    async checkSetupStatus() {
        const statusEl = document.getElementById('setup-status-content');
        const formCard = document.getElementById('setup-form-card');
        
        try {
            // Timeout dopo 5 secondi
            const timeoutPromise = new Promise((_, reject) => 
                setTimeout(() => reject(new Error('Timeout - server non risponde')), 5000)
            );
            
            const response = await Promise.race([
                API.get('/core/v1/setup/status'),
                timeoutPromise
            ]);
            
            console.log('Setup status response:', response);
            
            if (response.setup_completed) {
                statusEl.innerHTML = `
                    <div class="alert alert-success">
                        <i class="fas fa-check-circle"></i>
                        <div>
                            <h3 class="font-bold">Setup Completato!</h3>
                            <div class="text-sm">
                                <p>✅ Supabase: ${response.supabase_configured ? 'Configurato' : 'Non configurato'}</p>
                                <p>✅ Admin Key: ${response.admin_key_configured ? 'Configurata' : 'Non configurata'}</p>
                                <p>✅ LemonSqueezy: ${response.credentials_encrypted ? 'Criptate e salvate' : 'Non salvate'}</p>
                                <p>${response.flowise_configured ? '✅' : '❌'} Flowise: ${response.flowise_configured ? 'Configurato' : 'Non configurato'}</p>
                            </div>
                            <div class="mt-4">
                                <button class="btn btn-warning btn-sm" id="reset-setup-btn">
                                    <i class="fas fa-redo"></i> Reset Setup
                                </button>
                            </div>
                        </div>
                    </div>
                `;
                formCard.style.display = 'none';
                
                // Aggiungi event listener al pulsante reset
                setTimeout(() => {
                    const resetBtn = document.getElementById('reset-setup-btn');
                    if (resetBtn) {
                        resetBtn.addEventListener('click', () => this.resetSetup());
                    }
                }, 100);
            } else {
                statusEl.innerHTML = `
                    <div class="alert alert-warning">
                        <i class="fas fa-exclamation-triangle"></i>
                        <div>
                            <h3 class="font-bold">Setup Richiesto</h3>
                            <p class="text-sm">Completa la configurazione iniziale per utilizzare Flow Starter.</p>
                        </div>
                    </div>
                `;
                formCard.style.display = 'block';
            }
        } catch (error) {
            console.error('Setup status check failed:', error);
            statusEl.innerHTML = `
                <div class="alert alert-error">
                    <i class="fas fa-times-circle"></i>
                    <div>
                        <h3 class="font-bold">Errore nel controllo dello status</h3>
                        <p class="text-sm">${error.message}</p>
                        <button class="btn btn-sm btn-outline mt-2" onclick="ConfigurationComponent.checkSetupStatus()">
                            <i class="fas fa-redo"></i> Riprova
                        </button>
                    </div>
                </div>
            `;
            // Mostra il form in caso di errore
            if (formCard) {
                formCard.style.display = 'block';
            }
        }
    },

    async runSetup() {
        const btn = document.getElementById('setup_btn');
        const resultEl = document.getElementById('setup-result');
        
        // Disable button and show loading
        btn.disabled = true;
        btn.innerHTML = '<span class="loading loading-spinner loading-sm"></span> Configurando...';
        
        const payload = {
            supabase_url: document.getElementById('supabase_url').value.trim(),
            supabase_service_key: document.getElementById('supabase_key').value.trim(),
            lemonsqueezy_api_key: document.getElementById('ls_api_key').value.trim(),
            lemonsqueezy_store_id: document.getElementById('ls_store_id').value.trim(),
            lemonsqueezy_webhook_secret: document.getElementById('ls_webhook_secret').value.trim(),
            flowise_base_url: document.getElementById('flowise_base_url').value.trim(),
            flowise_api_key: document.getElementById('flowise_api_key').value.trim(),
            app_name: document.getElementById('app_name').value.trim() || 'default'
        };
        
        // Validazione base
        if (!payload.supabase_url || !payload.supabase_service_key || !payload.lemonsqueezy_api_key) {
            resultEl.innerHTML = `
                <div class="alert alert-error">
                    <i class="fas fa-times-circle"></i>
                    <span>Compila almeno Supabase URL, Service Key e LemonSqueezy API Key</span>
                </div>
            `;
            btn.disabled = false;
            btn.innerHTML = '<i class="fas fa-rocket"></i> Completa Setup';
            return;
        }
        
        try {
            const response = await API.post('/core/v1/setup/complete-setup', payload);
            
            resultEl.innerHTML = `
                <div class="alert alert-success">
                    <i class="fas fa-check-circle"></i>
                    <div>
                        <h3 class="font-bold">✅ Setup completato!</h3>
                        <p><strong>Test connessione:</strong> ${response.connection_test.success ? '✅ OK' : '❌ ' + response.connection_test.error}</p>
                        
                        <div class="mt-4">
                            <h4 class="font-semibold">📝 Variabili d'ambiente generate:</h4>
                            <pre class="bg-base-300 p-3 rounded text-xs mt-2 overflow-auto max-h-48">${response.env_commands.join('\\n')}</pre>
                        </div>
                        
                        <div class="mt-4">
                            <h4 class="font-semibold">Prossimi passi:</h4>
                            <ul class="list-disc list-inside text-sm mt-2">
                                ${response.next_steps.map(step => `<li>${step}</li>`).join('')}
                            </ul>
                        </div>
                    </div>
                </div>
            `;
            
            // Refresh status after successful setup
            setTimeout(() => {
                this.checkSetupStatus();
            }, 2000);
            
        } catch (error) {
            resultEl.innerHTML = `
                <div class="alert alert-error">
                    <i class="fas fa-times-circle"></i>
                    <span>Errore: ${error.message}</span>
                </div>
            `;
        }
        
        btn.disabled = false;
        btn.innerHTML = '<i class="fas fa-rocket"></i> Completa Setup';
    },

    async resetSetup() {
        // Primo layer di sicurezza
        if (!confirm('⚠️ RESET SETUP\n\nQuesto eliminerà TUTTE le credenziali salvate (LemonSqueezy, Flowise, ecc.).\n\nSei sicuro di voler continuare?')) {
            return;
        }
        
        // Secondo layer di sicurezza - richiede conferma esplicita
        const confirmText = prompt('Per confermare, scrivi "RESET" (tutto maiuscolo):');
        if (confirmText !== 'RESET') {
            Utils.showToast('Reset annullato - testo di conferma non corretto', 'info');
            return;
        }

        try {
            const response = await API.post('/core/v1/setup/reset', {}, {
                headers: {
                    'X-Admin-Key': State.adminKey
                }
            });
            
            Utils.showToast('Setup resettato! Ricarica la pagina per rifarlo completo.', 'success');
            
            // Ricarica la pagina dopo 2 secondi
            setTimeout(() => {
                window.location.reload();
            }, 2000);
            
                    } catch (error) {
            Utils.showToast(`Errore durante reset: ${error.message}`, 'error');
        }
    },

    // === SECURITY & CREDENTIALS MANAGEMENT ===

    async loadCredentials() {
        try {
            // Carica credenziali di sistema dal .env (se disponibili)
            const systemCreds = await API.get('/core/v1/admin/system/credentials');
            if (systemCreds) {
                document.getElementById('sys_supabase_url').value = systemCreds.supabase_url || '';
                document.getElementById('sys_supabase_key').value = systemCreds.supabase_key || '';
                document.getElementById('sys_admin_key').value = systemCreds.admin_key || '';
                document.getElementById('sys_encryption_key').value = systemCreds.encryption_key || '';
            }

            // Carica credenziali provider da Supabase (solo per verifica, non i valori)
            const lsStatus = await API.get('/core/v1/admin/credentials/status?provider=lemonsqueezy');
            const flowiseStatus = await API.get('/core/v1/admin/credentials/status?provider=flowise');
            
            // Mostra status invece dei valori per sicurezza
            if (lsStatus?.configured) {
                document.getElementById('ls_api_key').placeholder = '••••••••••••••••••••';
                document.getElementById('ls_store_id').placeholder = 'Configured';
                document.getElementById('ls_webhook_secret').placeholder = '••••••••••••••••••••';
            }
            
            if (flowiseStatus?.configured) {
                document.getElementById('flowise_base_url').placeholder = 'Configured';
                document.getElementById('flowise_api_key').placeholder = '••••••••••••••••••••';
            }
        } catch (error) {
            console.error('Error loading credentials:', error);
        }
    },

    async saveSystemCredentials() {
        try {
            const payload = {
                supabase_url: document.getElementById('sys_supabase_url').value.trim(),
                supabase_key: document.getElementById('sys_supabase_key').value.trim(),
                admin_key: document.getElementById('sys_admin_key').value.trim(),
                encryption_key: document.getElementById('sys_encryption_key').value.trim()
            };

            if (!payload.supabase_url || !payload.supabase_key) {
                Utils.showToast('Supabase URL e Service Key sono obbligatori', 'error');
                return;
            }

            const response = await API.post('/core/v1/admin/system/credentials', payload, {
                headers: { 'X-Admin-Key': State.adminKey }
            });

            Utils.showToast('Credenziali di sistema salvate! Riavvia il server per applicare.', 'success');
        } catch (error) {
            Utils.showToast(`Errore salvataggio credenziali: ${error.message}`, 'error');
        }
    },

    async testSystemConnection() {
        try {
            const response = await API.get('/core/v1/admin/system/test-supabase', {
                headers: { 'X-Admin-Key': State.adminKey }
            });
            
            const message = response.success ? 
                `Connessione OK - ${response.tables || 0} tabelle trovate` : 
                `Test fallito: ${response.error}`;
            
            Utils.showToast(message, response.success ? 'success' : 'error');
        } catch (error) {
            Utils.showToast(`Errore test connessione: ${error.message}`, 'error');
        }
    },

    async saveLemonSqueezy() {
        try {
            const apiKey = document.getElementById('ls_api_key').value.trim();
            const storeId = document.getElementById('ls_store_id').value.trim();
            const webhookSecret = document.getElementById('ls_webhook_secret').value.trim();

            if (!apiKey || !storeId || !webhookSecret) {
                Utils.showToast('Tutti i campi LemonSqueezy sono obbligatori', 'error');
                return;
            }

            // Salva API Key
            await API.post('/core/v1/admin/credentials/rotate', {
                provider: 'lemonsqueezy',
                credential_key: 'api_key',
                new_value: apiKey
            }, {
                headers: { 'X-Admin-Key': State.adminKey }
            });

            // Salva Webhook Secret
            await API.post('/core/v1/admin/credentials/rotate', {
                provider: 'lemonsqueezy',
                credential_key: 'webhook_secret',
                new_value: webhookSecret
            }, {
                headers: { 'X-Admin-Key': State.adminKey }
            });

            // Salva Store ID nella billing config
            const billingConfig = await API.get('/core/v1/admin/billing/config');
            const config = billingConfig.config || {};
            config.lemonsqueezy = { ...config.lemonsqueezy, store_id: storeId };
            
            await API.put('/core/v1/admin/billing/config', { config }, {
                headers: { 'X-Admin-Key': State.adminKey }
            });

            Utils.showToast('Credenziali LemonSqueezy salvate!', 'success');
            
            // Pulisci i campi per sicurezza
            document.getElementById('ls_api_key').value = '';
            document.getElementById('ls_store_id').value = '';
            document.getElementById('ls_webhook_secret').value = '';
            
            // Ricarica per mostrare status
            this.loadCredentials();
        } catch (error) {
            Utils.showToast(`Errore salvataggio LemonSqueezy: ${error.message}`, 'error');
        }
    },

    async testLemonSqueezy() {
        try {
            const response = await API.post('/core/v1/admin/credentials/test?provider=lemonsqueezy', {}, {
                headers: { 'X-Admin-Key': State.adminKey }
            });
            
            const message = response.success ? 
                `Connessione OK${response.user ? ' - ' + response.user : ''}` : 
                `Test fallito: ${response.error}`;
            
            Utils.showToast(message, response.success ? 'success' : 'error');
        } catch (error) {
            Utils.showToast(`Errore test LemonSqueezy: ${error.message}`, 'error');
        }
    },

    async saveFlowise() {
        try {
            const baseUrl = document.getElementById('flowise_base_url').value.trim();
            const apiKey = document.getElementById('flowise_api_key').value.trim();

            if (!baseUrl || !apiKey) {
                Utils.showToast('Base URL e API Key Flowise sono obbligatori', 'error');
                return;
            }

            // Salva Base URL
            await API.post('/core/v1/admin/credentials/rotate', {
                provider: 'flowise',
                credential_key: 'base_url',
                new_value: baseUrl
            }, {
                headers: { 'X-Admin-Key': State.adminKey }
            });

            // Salva API Key
            await API.post('/core/v1/admin/credentials/rotate', {
                provider: 'flowise',
                credential_key: 'api_key',
                new_value: apiKey
            }, {
                headers: { 'X-Admin-Key': State.adminKey }
            });

            Utils.showToast('Credenziali Flowise salvate!', 'success');
            
            // Pulisci i campi per sicurezza
            document.getElementById('flowise_base_url').value = '';
            document.getElementById('flowise_api_key').value = '';
            
            // Ricarica per mostrare status
            this.loadCredentials();
        } catch (error) {
            Utils.showToast(`Errore salvataggio Flowise: ${error.message}`, 'error');
        }
    },

    async testFlowise() {
        try {
            const response = await API.post('/core/v1/admin/credentials/test?provider=flowise', {}, {
                headers: { 'X-Admin-Key': State.adminKey }
            });
            
            const message = response.success ? 
                'Connessione Flowise OK' : 
                `Test fallito: ${response.error}`;
            
            Utils.showToast(message, response.success ? 'success' : 'error');
        } catch (error) {
            Utils.showToast(`Errore test Flowise: ${error.message}`, 'error');
        }
    },

    async generateNewAdminKey() {
        if (!confirm('Generare una nuova Admin Key? Dovrai aggiornarla nel .env e riavviare il server.')) {
            return;
        }
        
        try {
            const response = await API.post('/core/v1/admin/system/generate-admin-key', {}, {
                headers: { 'X-Admin-Key': State.adminKey }
            });
            
            document.getElementById('sys_admin_key').value = response.admin_key;
            Utils.showToast('Nuova Admin Key generata! Copia nel .env e riavvia il server.', 'success');
        } catch (error) {
            Utils.showToast(`Errore generazione Admin Key: ${error.message}`, 'error');
        }
    },

    async rotateEncryptionKey() {
        if (!confirm('⚠️ ATTENZIONE: Ruotare la chiave di crittografia ri-cripterà tutti i dati. Continuare?')) {
            return;
        }
        
        try {
            const response = await API.post('/core/v1/admin/system/rotate-encryption-key', {}, {
                headers: { 'X-Admin-Key': State.adminKey }
            });
            
            document.getElementById('sys_encryption_key').value = response.encryption_key;
            Utils.showToast('Chiave di crittografia ruotata! Tutti i dati sono stati ri-criptati.', 'success');
        } catch (error) {
            Utils.showToast(`Errore rotazione chiave: ${error.message}`, 'error');
        }
    },

    async clearCredentialsCache() {
        try {
            await API.post('/core/v1/admin/credentials/clear-cache', {}, {
                headers: { 'X-Admin-Key': State.adminKey }
            });
            
            Utils.showToast('Cache credenziali pulita!', 'success');
        } catch (error) {
            Utils.showToast(`Errore pulizia cache: ${error.message}`, 'error');
        }
    },

    async exportCredentials() {
        try {
            const response = await API.get('/core/v1/admin/credentials/export', {
                headers: { 'X-Admin-Key': State.adminKey }
            });
            
            const blob = new Blob([JSON.stringify(response, null, 2)], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `credentials-backup-${new Date().toISOString().split('T')[0]}.json`;
            a.click();
            URL.revokeObjectURL(url);
            
            Utils.showToast('Backup credenziali esportato!', 'success');
        } catch (error) {
            Utils.showToast(`Errore esportazione: ${error.message}`, 'error');
        }
    },

    async fixEncryptionIssues() {
        if (!confirm('⚠️ RIPARAZIONE CREDENZIALI\n\nQuesto eliminerà le credenziali corrotte. Dovrai ri-inserirle manualmente.\n\nContinuare?')) {
            return;
        }
        
        try {
            const response = await API.post('/core/v1/admin/credentials/fix-encryption', {}, {
                headers: { 'X-Admin-Key': State.adminKey }
            });
            
            Utils.showToast(`${response.message} (${response.deleted} eliminate)`, 'success');
            
            // Ricarica credenziali per mostrare lo stato pulito
            setTimeout(() => {
                this.loadCredentials();
            }, 1000);
            } catch (error) {
            Utils.showToast(`Errore riparazione: ${error.message}`, 'error');
            }
        }
};