/**
 * Users Component - Gestione utenti
 */
const UsersComponent = {
    currentUsers: [],
    selectedUser: null,

    /**
     * Carica lista utenti
     */
    async loadUsers(query = '') {
        try {
            Utils.showLoading();
            const url = query 
                ? `/core/v1/admin/users?q=${encodeURIComponent(query)}&limit=100`
                : '/core/v1/admin/users?limit=100';
            const data = await API.get(url);
            this.currentUsers = data.users || [];
            this.renderUsersList();
        } catch (error) {
            console.error('Failed to load users:', error);
            Utils.showToast('Errore caricamento utenti: ' + error.message, 'error');
        } finally {
            Utils.showLoading(false);
        }
    },

    /**
     * Renderizza lista utenti
     */
    renderUsersList() {
        const container = document.getElementById('users-list-container');
        if (!container) return;

        if (this.currentUsers.length === 0) {
            container.innerHTML = `
                <div class="text-center py-8 text-base-content/60">
                    <i class="fas fa-users text-4xl mb-4"></i>
                    <p>Nessun utente trovato</p>
                </div>
            `;
            return;
        }

        const html = `
            <div class="overflow-x-auto">
                <table class="table table-zebra w-full">
                    <thead>
                        <tr>
                            <th>Email</th>
                            <th>Crediti</th>
                            <th>Data Registrazione</th>
                            <th>Azioni</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${this.currentUsers.map(user => `
                            <tr>
                                <td>
                                    <div class="flex items-center gap-2">
                                        <i class="fas fa-user-circle text-2xl text-primary"></i>
                                        <span class="font-medium">${Utils.escapeHtml(user.email || 'N/A')}</span>
                                    </div>
                                </td>
                                <td>
                                    <span class="badge badge-lg ${user.credits > 0 ? 'badge-success' : 'badge-ghost'}">
                                        ${Utils.formatNumber(user.credits || 0)} credits
                                    </span>
                                </td>
                                <td>
                                    ${user.created_at ? new Date(user.created_at).toLocaleDateString('it-IT') : 'N/A'}
                                </td>
                                <td>
                                    <div class="flex gap-2">
                                        <button class="btn btn-sm btn-primary" onclick="UsersComponent.showUserDetail('${user.id}')">
                                            <i class="fas fa-eye"></i>
                                            Dettagli
                                        </button>
                                        <button class="btn btn-sm btn-error" onclick="UsersComponent.confirmDeleteUser('${user.id}', '${Utils.escapeHtml(user.email)}')">
                                            <i class="fas fa-trash"></i>
                                        </button>
                                    </div>
                                </td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
            <div class="mt-4 text-sm text-base-content/60">
                Totale: ${this.currentUsers.length} utenti
            </div>
        `;

        container.innerHTML = html;
    },

    /**
     * Mostra dettaglio utente
     */
    async showUserDetail(userId) {
        try {
            Utils.showLoading();
            const data = await API.get(`/core/v1/admin/users/${userId}`);
            this.selectedUser = data;
            this.renderUserDetailModal(data);
        } catch (error) {
            console.error('Failed to load user details:', error);
            Utils.showToast('Errore caricamento dettagli utente: ' + error.message, 'error');
        } finally {
            Utils.showLoading(false);
        }
    },

    /**
     * Renderizza modal dettaglio utente
     */
    renderUserDetailModal(data) {
        const user = data.user;
        const subscription = data.subscription;
        const history = data.credits_history || [];
        const openrouterKeys = data.openrouter_keys || [];

        const modal = document.createElement('div');
        modal.className = 'modal modal-open';
        modal.id = 'user-detail-modal';
        modal.innerHTML = `
            <div class="modal-box max-w-4xl">
                <h3 class="font-bold text-2xl mb-4">
                    <i class="fas fa-user-circle text-primary"></i>
                    ${Utils.escapeHtml(user.email || 'N/A')}
                </h3>
                
                <!-- Tabs -->
                <div class="tabs tabs-boxed mb-4">
                    <a class="tab tab-active" data-user-tab="info" onclick="UsersComponent.switchUserTab('info')">
                        <i class="fas fa-info-circle mr-2"></i>
                        Info
                    </a>
                    <a class="tab" data-user-tab="credits" onclick="UsersComponent.switchUserTab('credits')">
                        <i class="fas fa-coins mr-2"></i>
                        Crediti
                    </a>
                    <a class="tab" data-user-tab="history" onclick="UsersComponent.switchUserTab('history')">
                        <i class="fas fa-history mr-2"></i>
                        Storico (${history.length})
                    </a>
                    <a class="tab" data-user-tab="advanced" onclick="UsersComponent.switchUserTab('advanced')">
                        <i class="fas fa-cog mr-2"></i>
                        Avanzate
                    </a>
                </div>

                <!-- Tab Content: Info -->
                <div id="user-tab-info" class="user-tab-content active">
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div class="card bg-base-200">
                            <div class="card-body">
                                <h4 class="font-bold mb-2">Informazioni Base</h4>
                                <div class="space-y-2 text-sm">
                                    <div><strong>ID:</strong> <code class="text-xs">${user.id}</code></div>
                                    <div>
                                        <strong>Email:</strong> ${Utils.escapeHtml(user.email || 'N/A')}
                                        ${user.email_confirmed_at ? `
                                            <span class="badge badge-success badge-sm ml-2">
                                                <i class="fas fa-check-circle"></i> Confermata
                                            </span>
                                        ` : `
                                            <span class="badge badge-warning badge-sm ml-2">
                                                <i class="fas fa-exclamation-circle"></i> Non confermata
                                            </span>
                                        `}
                                    </div>
                                    ${!user.email_confirmed_at ? `
                                    <div>
                                        <button class="btn btn-sm btn-warning" onclick="UsersComponent.confirmUserEmail('${user.id}', '${Utils.escapeHtml(user.email || '')}')">
                                            <i class="fas fa-envelope-check"></i>
                                            Conferma Email
                                        </button>
                                    </div>
                                    ` : ''}
                                    <div><strong>Nome:</strong> ${Utils.escapeHtml(user.full_name || user.first_name || 'N/A')}</div>
                                    <div><strong>Registrato:</strong> ${user.created_at ? new Date(user.created_at).toLocaleString('it-IT') : 'N/A'}</div>
                                    ${user.email_confirmed_at ? `<div><strong>Email confermata:</strong> ${new Date(user.email_confirmed_at).toLocaleString('it-IT')}</div>` : ''}
                                </div>
                            </div>
                        </div>

                        <div class="card bg-base-200">
                            <div class="card-body">
                                <h4 class="font-bold mb-2">Crediti</h4>
                                <div class="text-3xl font-bold text-success">
                                    ${Utils.formatNumber(user.credits || 0)}
                                </div>
                                <p class="text-sm text-base-content/60">crediti disponibili</p>
                                <button class="btn btn-sm btn-primary mt-2" onclick="UsersComponent.showModifyCreditsForm()">
                                    <i class="fas fa-edit"></i>
                                    Modifica Crediti
                                </button>
                            </div>
                        </div>

                        ${subscription ? `
                        <div class="card bg-base-200 md:col-span-2">
                            <div class="card-body">
                                <h4 class="font-bold mb-2">
                                    <i class="fas fa-crown text-warning"></i>
                                    Subscription Attiva
                                </h4>
                                <div class="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                                    <div>
                                        <strong>Plan ID:</strong>
                                        <div>${subscription.plan_id || 'N/A'}</div>
                                    </div>
                                    <div>
                                        <strong>Status:</strong>
                                        <div><span class="badge badge-success">${subscription.status}</span></div>
                                    </div>
                                    <div>
                                        <strong>Crediti/Mese:</strong>
                                        <div>${Utils.formatNumber(subscription.credits_per_month || 0)}</div>
                                    </div>
                                    <div>
                                        <strong>Iniziata:</strong>
                                        <div>${subscription.created_at ? new Date(subscription.created_at).toLocaleDateString('it-IT') : 'N/A'}</div>
                                    </div>
                                </div>
                            </div>
                        </div>
                        ` : `
                        <div class="card bg-base-200 md:col-span-2">
                            <div class="card-body text-center text-base-content/60">
                                <i class="fas fa-info-circle text-2xl mb-2"></i>
                                <p>Nessuna subscription attiva</p>
                            </div>
                        </div>
                        `}
                    </div>
                </div>

                <!-- Tab Content: Credits -->
                <div id="user-tab-credits" class="user-tab-content" style="display: none;">
                    <div id="modify-credits-form-container">
                        <!-- Form modifica crediti verrà inserito qui -->
                    </div>
                </div>

                <!-- Tab Content: History -->
                <div id="user-tab-history" class="user-tab-content" style="display: none;">
                    ${history.length > 0 ? `
                    <div class="overflow-x-auto max-h-96">
                        <table class="table table-sm table-zebra">
                            <thead>
                                <tr>
                                    <th>Data</th>
                                    <th>Tipo</th>
                                    <th>Importo</th>
                                    <th>Motivo</th>
                                    <th>Balance</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${history.map(tx => `
                                    <tr>
                                        <td class="text-xs">${new Date(tx.created_at).toLocaleString('it-IT')}</td>
                                        <td>
                                            <span class="badge badge-sm ${tx.operation_type === 'credit' ? 'badge-success' : 'badge-error'}">
                                                ${tx.operation_type === 'credit' ? '+' : '-'}
                                            </span>
                                        </td>
                                        <td class="font-mono">${Utils.formatNumber(Math.abs(tx.amount || 0))}</td>
                                        <td class="text-xs">${Utils.escapeHtml(tx.reason || 'N/A')}</td>
                                        <td class="font-mono">${Utils.formatNumber(tx.balance_after || 0)}</td>
                                    </tr>
                                `).join('')}
                            </tbody>
                        </table>
                    </div>
                    <button class="btn btn-sm btn-ghost mt-4" onclick="UsersComponent.loadFullHistory('${user.id}')">
                        <i class="fas fa-download"></i>
                        Carica Storico Completo
                    </button>
                    ` : `
                    <div class="text-center py-8 text-base-content/60">
                        <i class="fas fa-history text-4xl mb-4"></i>
                        <p>Nessuna transazione</p>
                    </div>
                    `}
                </div>

                <!-- Tab Content: Advanced -->
                <div id="user-tab-advanced" class="user-tab-content" style="display: none;">
                    <div class="space-y-4">
                        ${openrouterKeys.length > 0 ? `
                        <div class="card bg-base-200">
                            <div class="card-body">
                                <h4 class="font-bold mb-2">
                                    <i class="fas fa-key text-info"></i>
                                    Chiavi OpenRouter (${openrouterKeys.length})
                                </h4>
                                <div class="space-y-2">
                                    ${openrouterKeys.map(key => `
                                        <div class="flex items-center justify-between p-2 bg-base-100 rounded">
                                            <div class="text-sm">
                                                <div><strong>${Utils.escapeHtml(key.key_name || 'N/A')}</strong></div>
                                                <div class="text-xs text-base-content/60">Limit: $${key.limit_usd || 0}</div>
                                            </div>
                                            <span class="badge ${key.is_active ? 'badge-success' : 'badge-ghost'}">
                                                ${key.is_active ? 'Attiva' : 'Inattiva'}
                                            </span>
                                        </div>
                                    `).join('')}
                                </div>
                            </div>
                        </div>
                        ` : ''}
                        
                        <div class="card bg-error/10 border-2 border-error">
                            <div class="card-body">
                                <h4 class="font-bold text-error mb-2">
                                    <i class="fas fa-exclamation-triangle"></i>
                                    Zona Pericolosa
                                </h4>
                                <p class="text-sm mb-4">Queste azioni sono irreversibili.</p>
                                <button class="btn btn-error" onclick="UsersComponent.confirmDeleteUser('${user.id}', '${Utils.escapeHtml(user.email)}')">
                                    <i class="fas fa-trash"></i>
                                    Elimina Utente
                                </button>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="modal-action">
                    <button class="btn" onclick="UsersComponent.closeUserDetailModal()">Chiudi</button>
                </div>
            </div>
            <div class="modal-backdrop" onclick="UsersComponent.closeUserDetailModal()"></div>
        `;
        
        document.body.appendChild(modal);
    },

    /**
     * Switch tra tab nel modal dettaglio
     */
    switchUserTab(tabName) {
        // Update tab buttons
        document.querySelectorAll('[data-user-tab]').forEach(tab => {
            tab.classList.remove('tab-active');
            if (tab.dataset.userTab === tabName) {
                tab.classList.add('tab-active');
            }
        });

        // Show/hide tab contents
        document.querySelectorAll('.user-tab-content').forEach(content => {
            content.style.display = 'none';
        });
        const activeContent = document.getElementById(`user-tab-${tabName}`);
        if (activeContent) {
            activeContent.style.display = 'block';
        }

        // Se tab credits, mostra form
        if (tabName === 'credits' && this.selectedUser) {
            this.showModifyCreditsForm();
        }
    },

    /**
     * Mostra form modifica crediti
     */
    showModifyCreditsForm() {
        const container = document.getElementById('modify-credits-form-container');
        if (!container) return;

        const user = this.selectedUser?.user;
        if (!user) return;

        container.innerHTML = `
            <div class="card bg-base-200">
                <div class="card-body">
                    <h4 class="font-bold mb-4">Modifica Crediti</h4>
                    <div class="alert alert-info mb-4">
                        <i class="fas fa-info-circle"></i>
                        <span>Balance corrente: <strong>${Utils.formatNumber(user.credits || 0)} crediti</strong></span>
                    </div>
                    
                    <form id="modify-credits-form" class="space-y-4">
                        <div class="form-control">
                            <label class="label">
                                <span class="label-text">Operazione</span>
                            </label>
                            <select class="select select-bordered" id="credit-operation" required>
                                <option value="credit">Accredita (+)</option>
                                <option value="debit">Addebita (-)</option>
                            </select>
                        </div>

                        <div class="form-control">
                            <label class="label">
                                <span class="label-text">Importo</span>
                            </label>
                            <input type="number" class="input input-bordered" id="credit-amount" 
                                   min="0.01" step="0.01" placeholder="es. 100" required />
                        </div>

                        <div class="form-control">
                            <label class="label">
                                <span class="label-text">Motivo</span>
                            </label>
                            <input type="text" class="input input-bordered" id="credit-reason" 
                                   placeholder="es. Rimborso supporto" required />
                        </div>

                        <div class="flex gap-2">
                            <button type="submit" class="btn btn-primary">
                                <i class="fas fa-check"></i>
                                Applica
                            </button>
                            <button type="button" class="btn btn-ghost" onclick="UsersComponent.switchUserTab('info')">
                                Annulla
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        `;

        // Bind form submit
        document.getElementById('modify-credits-form').addEventListener('submit', async (e) => {
            e.preventDefault();
            await this.modifyUserCredits(user.id);
        });
    },

    /**
     * Modifica crediti utente
     */
    async modifyUserCredits(userId) {
        const operation = document.getElementById('credit-operation').value;
        const amount = parseFloat(document.getElementById('credit-amount').value);
        const reason = document.getElementById('credit-reason').value.trim();

        if (!amount || amount <= 0 || !reason) {
            Utils.showToast('Compila tutti i campi correttamente', 'error');
            return;
        }

        try {
            Utils.showLoading();
            const result = await API.post(`/core/v1/admin/users/${userId}/credits`, {
                operation,
                amount,
                reason
            });

            Utils.showToast(
                `Crediti ${operation === 'credit' ? 'accreditati' : 'addebitati'} con successo!`,
                'success'
            );

            // Ricarica dettagli utente
            await this.showUserDetail(userId);
            this.switchUserTab('info');

            // Ricarica lista utenti
            await this.loadUsers();
        } catch (error) {
            console.error('Failed to modify credits:', error);
            Utils.showToast('Errore modifica crediti: ' + error.message, 'error');
        } finally {
            Utils.showLoading(false);
        }
    },

    /**
     * Carica storico completo
     */
    async loadFullHistory(userId) {
        try {
            Utils.showLoading();
            const data = await API.get(`/core/v1/admin/users/${userId}/credits/history?limit=500`);
            
            // Crea modal con storico completo
            const modal = document.createElement('div');
            modal.className = 'modal modal-open';
            modal.id = 'full-history-modal';
            modal.innerHTML = `
                <div class="modal-box max-w-4xl">
                    <h3 class="font-bold text-xl mb-4">Storico Completo Crediti</h3>
                    <div class="mb-4">
                        <div class="stats shadow">
                            <div class="stat">
                                <div class="stat-title">Balance Corrente</div>
                                <div class="stat-value text-success">${Utils.formatNumber(data.current_balance)}</div>
                            </div>
                            <div class="stat">
                                <div class="stat-title">Transazioni</div>
                                <div class="stat-value">${data.transactions.length}</div>
                            </div>
                        </div>
                    </div>
                    <div class="overflow-x-auto max-h-96">
                        <table class="table table-sm table-zebra">
                            <thead>
                                <tr>
                                    <th>Data</th>
                                    <th>Tipo</th>
                                    <th>Importo</th>
                                    <th>Motivo</th>
                                    <th>Balance Dopo</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${data.transactions.map(tx => `
                                    <tr>
                                        <td class="text-xs">${new Date(tx.created_at).toLocaleString('it-IT')}</td>
                                        <td>
                                            <span class="badge badge-sm ${tx.operation_type === 'credit' ? 'badge-success' : 'badge-error'}">
                                                ${tx.operation_type}
                                            </span>
                                        </td>
                                        <td class="font-mono ${tx.operation_type === 'credit' ? 'text-success' : 'text-error'}">
                                            ${tx.operation_type === 'credit' ? '+' : '-'}${Utils.formatNumber(Math.abs(tx.amount || 0))}
                                        </td>
                                        <td class="text-xs">${Utils.escapeHtml(tx.reason || 'N/A')}</td>
                                        <td class="font-mono">${Utils.formatNumber(tx.balance_after || 0)}</td>
                                    </tr>
                                `).join('')}
                            </tbody>
                        </table>
                    </div>
                    <div class="modal-action">
                        <button class="btn" onclick="document.getElementById('full-history-modal').remove()">Chiudi</button>
                    </div>
                </div>
                <div class="modal-backdrop" onclick="document.getElementById('full-history-modal').remove()"></div>
            `;
            document.body.appendChild(modal);
        } catch (error) {
            console.error('Failed to load full history:', error);
            Utils.showToast('Errore caricamento storico: ' + error.message, 'error');
        } finally {
            Utils.showLoading(false);
        }
    },

    /**
     * Conferma eliminazione utente
     */
    confirmDeleteUser(userId, email) {
        const modal = document.createElement('div');
        modal.className = 'modal modal-open';
        modal.id = 'confirm-delete-modal';
        modal.innerHTML = `
            <div class="modal-box">
                <h3 class="font-bold text-xl mb-4 text-error">
                    <i class="fas fa-exclamation-triangle"></i>
                    Conferma Eliminazione
                </h3>
                <div class="alert alert-error mb-4">
                    <i class="fas fa-exclamation-circle"></i>
                    <span>Questa azione è <strong>irreversibile</strong>!</span>
                </div>
                <p class="mb-4">
                    Stai per eliminare l'utente:<br>
                    <strong class="text-lg">${Utils.escapeHtml(email)}</strong>
                </p>
                <p class="text-sm text-base-content/60 mb-4">
                    Verranno eliminati tutti i dati associati: profilo, transazioni, subscription, chiavi OpenRouter.
                </p>
                <div class="form-control mb-4">
                    <label class="label">
                        <span class="label-text">Digita <strong>ELIMINA</strong> per confermare:</span>
                    </label>
                    <input type="text" class="input input-bordered" id="delete-confirm-input" placeholder="ELIMINA" />
                </div>
                <div class="modal-action">
                    <button class="btn" onclick="document.getElementById('confirm-delete-modal').remove()">Annulla</button>
                    <button class="btn btn-error" onclick="UsersComponent.deleteUser('${userId}')">
                        <i class="fas fa-trash"></i>
                        Elimina Definitivamente
                    </button>
                </div>
            </div>
            <div class="modal-backdrop" onclick="document.getElementById('confirm-delete-modal').remove()"></div>
        `;
        document.body.appendChild(modal);
    },

    /**
     * Elimina utente
     */
    async deleteUser(userId) {
        const confirmInput = document.getElementById('delete-confirm-input');
        if (confirmInput && confirmInput.value !== 'ELIMINA') {
            Utils.showToast('Digita ELIMINA per confermare', 'error');
            return;
        }

        try {
            Utils.showLoading();
            await API.delete(`/core/v1/admin/users/${userId}`);
            
            Utils.showToast('Utente eliminato con successo', 'success');
            
            // Chiudi tutti i modal
            document.getElementById('confirm-delete-modal')?.remove();
            document.getElementById('user-detail-modal')?.remove();
            
            // Ricarica lista
            await this.loadUsers();
        } catch (error) {
            console.error('Failed to delete user:', error);
            Utils.showToast('Errore eliminazione utente: ' + error.message, 'error');
        } finally {
            Utils.showLoading(false);
        }
    },

    /**
     * Chiudi modal dettaglio utente
     */
    closeUserDetailModal() {
        document.getElementById('user-detail-modal')?.remove();
        this.selectedUser = null;
    },

    /**
     * Mostra form creazione utente
     */
    showCreateUserForm() {
        const modal = document.createElement('div');
        modal.className = 'modal modal-open';
        modal.id = 'create-user-modal';
        modal.innerHTML = `
            <div class="modal-box max-w-2xl">
                <h3 class="font-bold text-xl mb-4">
                    <i class="fas fa-user-plus text-primary"></i>
                    Crea Nuovo Utente
                </h3>
                
                <form id="create-user-form" class="space-y-4">
                    <div class="form-control">
                        <label class="label">
                            <span class="label-text">Email *</span>
                        </label>
                        <input type="email" class="input input-bordered" id="new-user-email" 
                               placeholder="user@example.com" required />
                    </div>

                    <div class="form-control">
                        <label class="label">
                            <span class="label-text">Password</span>
                            <span class="label-text-alt">Lascia vuoto per generare automaticamente</span>
                        </label>
                        <input type="password" class="input input-bordered" id="new-user-password" 
                               placeholder="••••••••" />
                    </div>

                    <div class="form-control">
                        <label class="label">
                            <span class="label-text">Nome Completo</span>
                        </label>
                        <input type="text" class="input input-bordered" id="new-user-fullname" 
                               placeholder="Mario Rossi" />
                    </div>

                    <div class="alert alert-info">
                        <i class="fas fa-info-circle"></i>
                        <div>
                            <p class="text-sm">L'utente riceverà:</p>
                            <ul class="text-xs list-disc list-inside">
                                <li>Crediti iniziali secondo la configurazione pricing</li>
                                <li>Provisioning automatico chiave OpenRouter</li>
                                <li>Email di benvenuto (se configurata)</li>
                            </ul>
                        </div>
                    </div>

                    <div class="modal-action">
                        <button type="button" class="btn" onclick="document.getElementById('create-user-modal').remove()">
                            Annulla
                        </button>
                        <button type="submit" class="btn btn-primary">
                            <i class="fas fa-user-plus"></i>
                            Crea Utente
                        </button>
                    </div>
                </form>
            </div>
            <div class="modal-backdrop" onclick="document.getElementById('create-user-modal').remove()"></div>
        `;
        
        document.body.appendChild(modal);

        // Bind form submit
        document.getElementById('create-user-form').addEventListener('submit', async (e) => {
            e.preventDefault();
            await this.createUser();
        });
    },

    /**
     * Crea nuovo utente
     */
    async createUser() {
        const email = document.getElementById('new-user-email').value.trim();
        const password = document.getElementById('new-user-password').value.trim();
        const fullName = document.getElementById('new-user-fullname').value.trim();

        if (!email) {
            Utils.showToast('Email obbligatoria', 'error');
            return;
        }

        const payload = { email };
        if (password) payload.password = password;
        if (fullName) payload.full_name = fullName;

        try {
            Utils.showLoading();
            const result = await API.post('/core/v1/admin/users', payload);
            
            Utils.showToast('Utente creato con successo!', 'success');
            
            // Mostra credenziali generate
            if (result.password) {
                alert(`Utente creato!\n\nEmail: ${result.email}\nPassword: ${result.password}\n\n⚠️ Salva queste credenziali, non verranno più mostrate!`);
            }
            
            // Chiudi modal
            document.getElementById('create-user-modal')?.remove();
            
            // Ricarica lista
            await this.loadUsers();
        } catch (error) {
            console.error('Failed to create user:', error);
            Utils.showToast('Errore creazione utente: ' + error.message, 'error');
        } finally {
            Utils.showLoading(false);
        }
    },

    /**
     * Conferma email utente
     */
    async confirmUserEmail(userId, email) {
        if (!confirm(`Confermare l'email per ${email}?`)) {
            return;
        }

        try {
            Utils.showLoading();
            const result = await API.post('/core/v1/auth/confirm-email', {
                user_id: userId
            });
            
            Utils.showToast('Email confermata con successo!', 'success');
            
            // Ricarica dettagli utente per aggiornare UI
            await this.showUserDetail(userId);
        } catch (error) {
            console.error('Failed to confirm email:', error);
            Utils.showToast('Errore conferma email: ' + error.message, 'error');
        } finally {
            Utils.showLoading(false);
        }
    },
};

// Esponi globalmente
window.UsersComponent = UsersComponent;











