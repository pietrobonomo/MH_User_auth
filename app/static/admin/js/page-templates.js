window.pageTemplates = {
            overview: () => `
                <div class="mb-6">
                    <h1 class="text-3xl font-bold">Dashboard Overview</h1>
                    <p class="text-base-content/60">System status and key metrics</p>
                </div>
                
                                    <!-- Admin Key Info -->
                    <div class="alert alert-info mb-6" id="admin-key-info" style="display: none;">
                        <i class="fas fa-info-circle"></i>
                        <div>
                            <h3 class="font-bold">Configura Admin Key</h3>
                            <p>Per usare la dashboard, configura la tua Admin Key nel browser</p>
                            <p class="text-sm mt-1">L'Admin Key è salvata in localStorage e serve per autenticare le chiamate API</p>
                        </div>
                        <div class="flex gap-2">
                            <button class="btn btn-sm btn-primary" onclick="showQuickSetup()">Configura Admin Key</button>
                        </div>
                    </div>
                
                <!-- Metrics Grid -->
                <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
                    <div class="metric-card card bg-base-100 shadow-xl">
                        <div class="card-body">
                            <h2 class="card-title text-sm">Total Users</h2>
                            <p class="text-3xl font-bold" id="metric-users">-</p>
                        </div>
                    </div>
                    <div class="metric-card card bg-base-100 shadow-xl">
                        <div class="card-body">
                            <h2 class="card-title text-sm">Active Credits</h2>
                            <p class="text-3xl font-bold" id="metric-credits">-</p>
                        </div>
                    </div>
                    <div class="metric-card card bg-base-100 shadow-xl">
                        <div class="card-body">
                            <h2 class="card-title text-sm">Revenue Target</h2>
                            <p class="text-3xl font-bold" id="metric-revenue">-</p>
                        </div>
                    </div>
                    <div class="metric-card card bg-base-100 shadow-xl">
                        <div class="card-body">
                            <h2 class="card-title text-sm">System Health</h2>
                            <p class="text-3xl font-bold text-success">OK</p>
                        </div>
                    </div>
                </div>
                
                <!-- Quick Actions -->
                <div class="card bg-base-100 shadow-xl">
                    <div class="card-body">
                        <h2 class="card-title">Quick Actions</h2>
                        <div class="flex flex-wrap gap-2">
                            <button class="btn btn-primary" onclick="navigate('billing', 'operations')">
                                <i class="fas fa-shopping-cart"></i> Create Checkout
                            </button>
                            <button class="btn btn-secondary" onclick="navigate('observability', 'rollouts')">
                                <i class="fas fa-sync"></i> Run Rollout
                            </button>
                            <button class="btn btn-accent" onclick="navigate('testing')">
                                <i class="fas fa-play"></i> Test Flow
                            </button>
                        </div>
                    </div>
                </div>
            `,
            
            // Business & Pricing - Revenue Configuration
            'business-config': () => `
                <div class="mb-6">
                    <h1 class="text-3xl font-bold">Revenue Configuration</h1>
                    <p class="text-base-content/60">Configure revenue targets and pricing multipliers</p>
                </div>
                
                <!-- Tabs for future expansion -->
                <div class="tabs tabs-boxed mb-6">
                    <a href="#" class="tab tab-active" data-tab="basic">Basic Settings</a>
                    <a href="#" class="tab" data-tab="fixed-costs">Fixed Costs</a>
                    <a href="#" class="tab" data-tab="history">History</a>
                </div>
                
                <!-- Tab Contents -->
                <div id="tab-basic" class="tab-content active">
                    <div class="card bg-base-100 shadow-xl">
                        <div class="card-body">
                            <h2 class="card-title">Revenue Settings</h2>
                            <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                                <div class="form-control">
                                    <label class="label">Monthly Revenue Target (USD)</label>
                                    <input type="number" class="input input-bordered" id="rev_target" />
                                </div>
                                <div class="form-control">
                                    <label class="label">USD → Credits</label>
                                    <input type="number" class="input input-bordered" id="usd_to_credits" />
                                </div>
                                <div class="form-control">
                                    <label class="label">Target Margin Multiplier</label>
                                    <input type="number" class="input input-bordered" id="margin_mult" />
                                </div>
                                <div class="form-control">
                                    <label class="label">Min Operation Cost (credits)</label>
                                    <input type="number" class="input input-bordered" id="min_op_cost" />
                                </div>
                                <div class="form-control">
                                    <label class="label">Initial Credits at Signup</label>
                                    <input type="number" class="input input-bordered" id="signup_initial_credits" placeholder="100" />
                                </div>
                                <div class="form-control">
                                    <label class="label">Signup Credits Cost (USD) [BI]</label>
                                    <input type="number" class="input input-bordered" id="signup_credits_cost" step="0.01" placeholder="0.00" />
                                </div>
                                <div class="form-control">
                                    <label class="label">Monthly new users (BI)</label>
                                    <input type="number" class="input input-bordered" id="bi_monthly_new_users" step="1" placeholder="0" />
                                </div>
                            </div>
                            <div class="mt-2 text-sm text-base-content/70" id="signup_credits_forecast_line" style="display:none;">
                                Estimated monthly signup credits cost: <span id="signup_credits_forecast_cost" class="font-semibold">$0.00</span>
                            </div>
                            <div class="card-actions justify-end mt-4">
                                <button class="btn btn-primary" onclick="PricingComponent.savePricingConfig()">Save Configuration</button>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div id="tab-fixed-costs" class="tab-content">
                    <div class="card bg-base-100 shadow-xl">
                        <div class="card-body">
                            <h2 class="card-title">Fixed Monthly Costs (Overhead)</h2>
                            <div class="alert alert-info mb-4">
                                <i class="fas fa-info-circle"></i>
                                <div>
                                    <p class="font-semibold">Overhead Calculation</p>
                                    <p class="text-sm">These fixed costs are used to calculate the overhead multiplier: (total_fixed_costs / monthly_revenue_target)</p>
                                </div>
                            </div>
                            <table class="table w-full">
                                <thead>
                                    <tr>
                                        <th>Cost Category</th>
                                        <th>Monthly Cost (USD)</th>
                                        <th>Actions</th>
                                    </tr>
                                </thead>
                                <tbody id="fixed-costs-table">
                                    <!-- Dynamic content -->
                                </tbody>
                            </table>
                            <div class="flex gap-2 mt-4">
                                <button class="btn btn-sm btn-primary" onclick="PricingComponent.addFixedCostRow()">
                                    <i class="fas fa-plus"></i> Add Fixed Cost
                                </button>
                                <button class="btn btn-sm btn-success" onclick="PricingComponent.saveFixedCosts()">
                                    <i class="fas fa-save"></i> Save Changes
                                </button>
                            </div>
                            
                            <!-- Overhead Preview -->
                            <div class="divider">Overhead Preview</div>
                            <div id="overhead-preview" class="stats shadow">
                                <div class="stat">
                                    <div class="stat-title">Total Fixed Costs</div>
                                    <div class="stat-value text-primary" id="total-fixed-costs">$0</div>
                                </div>
                                <div class="stat">
                                    <div class="stat-title">Overhead Multiplier</div>
                                    <div class="stat-value text-secondary" id="overhead-multiplier">1.0x</div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div id="tab-history" class="tab-content">
                    <div class="card bg-base-100 shadow-xl">
                        <div class="card-body">
                            <p class="text-center text-base-content/60">Configuration history coming soon...</p>
                        </div>
                    </div>
                </div>
            `,
            
            // Business & Pricing - App Affordability
            'business-costs': () => `
                <div class="mb-6">
                    <h1 class="text-3xl font-bold">App Affordability</h1>
                    <p class="text-base-content/60">Configure minimum credits required per app before flow execution</p>
                </div>
                
                <!-- Tabs for future expansion -->
                <div class="tabs tabs-boxed mb-6">
                    <a href="#" class="tab tab-active" data-tab="current">Current Apps</a>
                    <a href="#" class="tab" data-tab="analytics">Usage Analytics</a>
                    <a href="#" class="tab" data-tab="policies">Policies</a>
                </div>
                
                <div id="tab-current" class="tab-content active">
                    <div class="card bg-base-100 shadow-xl">
                        <div class="card-body">
                            <h2 class="card-title">Minimum Affordability per App</h2>
                            <p class="text-xs text-base-content/60">Saved in pricing config under <code>flow_costs_usd[appId]</code>.</p>
                            <div class="alert alert-info mb-4">
                                <i class="fas fa-info-circle"></i>
                                <div>
                                    <p class="font-semibold">Affordability Check</p>
                                    <p class="text-sm">Before executing ANY flow in an app, the system checks if the user has at least this many credits</p>
                                </div>
                            </div>
                            <table class="table w-full">
                                <thead>
                                    <tr>
                                        <th>App ID</th>
                                        <th>Min Credits Required</th>
                                        <th>Status</th>
                                        <th>Actions</th>
                                    </tr>
                                </thead>
                                <tbody id="app-affordability-table">
                                    <!-- Dynamic content -->
                                </tbody>
                            </table>
                            <div class="flex gap-2 mt-4">
                                <button class="btn btn-sm btn-primary" onclick="PricingComponent.loadAppAffordability()">
                                    <i class="fas fa-refresh"></i> Refresh Apps
                                </button>
                                <button class="btn btn-sm btn-success" onclick="PricingComponent.saveAppAffordability()">
                                    <i class="fas fa-save"></i> Save All Changes
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div id="tab-analytics" class="tab-content">
                    <div class="card bg-base-100 shadow-xl">
                        <div class="card-body">
                            <p class="text-center text-base-content/60">Affordability analytics coming soon...</p>
                        </div>
                    </div>
                </div>
                
                <div id="tab-policies" class="tab-content">
                    <div class="card bg-base-100 shadow-xl">
                        <div class="card-body">
                            <p class="text-center text-base-content/60">Affordability policies coming soon...</p>
                        </div>
                    </div>
                </div>
            `,
            
            // Business & Pricing - Simulator
            'business-simulator': () => `
                <div class="mb-6">
                    <h1 class="text-3xl font-bold">Pricing Simulator</h1>
                    <p class="text-base-content/60">Simulate pricing scenarios and multipliers</p>
                </div>
                
                <!-- Tabs for future expansion -->
                <div class="tabs tabs-boxed mb-6">
                    <a href="#" class="tab tab-active" data-tab="quick">Quick Simulation</a>
                    <a href="#" class="tab" data-tab="detailed">Detailed Analysis</a>
                    <a href="#" class="tab" data-tab="compare">Compare</a>
                </div>
                
                <div id="tab-quick" class="tab-content active">
                    <div class="card bg-base-100 shadow-xl">
                        <div class="card-body">
                            <h2 class="card-title">Current Pricing Multipliers</h2>
                            <div id="simulator-output">
                                <!-- Dynamic simulator content -->
                            </div>
                        </div>
                    </div>
                </div>
                
                <div id="tab-detailed" class="tab-content">
                    <div class="card bg-base-100 shadow-xl">
                        <div class="card-body">
                            <p class="text-center text-base-content/60">Detailed analysis coming soon...</p>
                        </div>
                    </div>
                </div>
                
                <div id="tab-compare" class="tab-content">
                    <div class="card bg-base-100 shadow-xl">
                        <div class="card-body">
                            <p class="text-center text-base-content/60">Scenario comparison coming soon...</p>
                        </div>
                    </div>
                </div>
            `,
            
            // Business & Pricing - Scenarios
            'business-scenarios': () => `
                <div class="mb-6">
                    <h1 class="text-3xl font-bold">Scenario Manager</h1>
                    <p class="text-base-content/60">Save and load different pricing scenarios</p>
                </div>
                
                <!-- Tabs for future expansion -->
                <div class="tabs tabs-boxed mb-6">
                    <a href="#" class="tab tab-active" data-tab="manage">Manage Scenarios</a>
                    <a href="#" class="tab" data-tab="templates">Templates</a>
                    <a href="#" class="tab" data-tab="share">Share</a>
                </div>
                
                <div id="tab-manage" class="tab-content active">
                    <div class="card bg-base-100 shadow-xl">
                        <div class="card-body">
                            <h2 class="card-title">Current Scenario</h2>
                            <div class="form-control">
                                <label class="label">Scenario Name</label>
                                <input type="text" class="input input-bordered" id="scenario_name" placeholder="e.g., growth-q4" />
                            </div>
                            <div class="flex gap-2 mt-4">
                                <button class="btn btn-primary" onclick="saveScenario()">Save Scenario</button>
                                <button class="btn btn-secondary" onclick="loadScenario()">Load Scenario</button>
                                <button class="btn btn-accent" onclick="exportScenario()">Export</button>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div id="tab-templates" class="tab-content">
                    <div class="card bg-base-100 shadow-xl">
                        <div class="card-body">
                            <p class="text-center text-base-content/60">Scenario templates coming soon...</p>
                        </div>
                    </div>
                </div>
                
                <div id="tab-share" class="tab-content">
                    <div class="card bg-base-100 shadow-xl">
                        <div class="card-body">
                            <p class="text-center text-base-content/60">Scenario sharing coming soon...</p>
                        </div>
                    </div>
                </div>
            `,
            
            // Billing & Plans - Payment Provider
            'billing-provider': () => `
                <div class="mb-6">
                    <h1 class="text-3xl font-bold">Payment Provider</h1>
                    <p class="text-base-content/60">Configure payment processing settings</p>
                </div>
                
                <!-- Tabs for future expansion -->
                <div class="tabs tabs-boxed mb-6">
                    <a href="#" class="tab tab-active" data-tab="config">Configuration</a>
                    <a href="#" class="tab" data-tab="webhooks">Webhooks</a>
                    <a href="#" class="tab" data-tab="logs">Logs</a>
                </div>
                
                <div id="tab-config" class="tab-content active">
                    <div class="card bg-base-100 shadow-xl">
                        <div class="card-body">
                            <h2 class="card-title">Provider Settings</h2>
                            <div class="alert alert-info mb-4">
                                <i class="fas fa-info-circle"></i>
                                <span>Currently configured for LemonSqueezy</span>
                            </div>
                            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                                <div class="form-control">
                                    <label class="label">Store ID</label>
                                    <input type="text" class="input input-bordered" id="ls_store" />
                                </div>
                                <div class="form-control">
                                    <label class="label">
                                        <span>Test Mode</span>
                                        <input type="checkbox" class="checkbox" id="ls_test_mode" />
                                    </label>
                                </div>
                            </div>

                            <div class="divider">Plan → Provider Mapping</div>
                            <div class="overflow-x-auto">
                                <table class="table w-full">
                                    <thead>
                                        <tr>
                                            <th>Plan ID</th>
                                            <th>Name</th>
                                            <th>Price (USD)</th>
                                            <th>Credits/Month</th>
                                            <th>Provider Variant ID</th>
                                        </tr>
                                    </thead>
                                    <tbody id="variant-map-table">
                                        <!-- Dynamic content -->
                                    </tbody>
                                </table>
                            </div>
                            <div class="card-actions justify-end mt-4">
                                <button class="btn btn-secondary" onclick="BillingComponent.testProviderConnection && BillingComponent.testProviderConnection()">Test Connection</button>
                                <button class="btn btn-primary" onclick="BillingComponent.saveBillingProviderConfig()">Save Configuration</button>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div id="tab-webhooks" class="tab-content">
                    <div class="card bg-base-100 shadow-xl">
                        <div class="card-body">
                            <p class="text-center text-base-content/60">Webhook monitoring coming soon...</p>
                        </div>
                    </div>
                </div>
                
                <div id="tab-logs" class="tab-content">
                    <div class="card bg-base-100 shadow-xl">
                        <div class="card-body">
                            <p class="text-center text-base-content/60">Provider logs coming soon...</p>
                        </div>
                    </div>
                </div>
            `,
            
            // Billing & Plans - Subscription Plans
            'billing-plans': () => `
                <div class="mb-6">
                    <h1 class="text-3xl font-bold">Subscription Plans</h1>
                    <p class="text-base-content/60">Manage subscription tiers and pricing</p>
                </div>
                
                <!-- Tabs for future expansion -->
                <div class="tabs tabs-boxed mb-6">
                    <a href="#" class="tab tab-active" data-tab="plans">Plans</a>
                    <a href="#" class="tab" data-tab="discounts">Discounts</a>
                    <a href="#" class="tab" data-tab="analytics">Analytics</a>
                </div>
                
                <div id="tab-plans" class="tab-content active">
                    <div id="plans-container">
                        <!-- Dynamic plan cards will be added here -->
                    </div>
                    <button class="btn btn-primary mt-4" onclick="BillingComponent.addNewPlan()">
                        <i class="fas fa-plus"></i> Add New Plan
                            </button>
                </div>
                
                <div id="tab-discounts" class="tab-content">
                    <div class="card bg-base-100 shadow-xl">
                        <div class="card-body">
                            <p class="text-center text-base-content/60">Discount management coming soon...</p>
                        </div>
                    </div>
                </div>
                
                <div id="tab-analytics" class="tab-content">
                    <div class="card bg-base-100 shadow-xl">
                        <div class="card-body">
                            <p class="text-center text-base-content/60">Plan analytics coming soon...</p>
                        </div>
                    </div>
                </div>
            `,
            
            // billing-credits rimosso: ora vive come tab in 'business-config'
            
            // Billing & Plans - Checkout
            'billing-checkout': () => `
                <div class="mb-6">
                    <h1 class="text-3xl font-bold">Checkout Generator</h1>
                    <p class="text-base-content/60">Create checkout sessions for users</p>
                </div>
                
                <!-- Tabs for future expansion -->
                <div class="tabs tabs-boxed mb-6">
                    <a href="#" class="tab tab-active" data-tab="create">Create Checkout</a>
                    <a href="#" class="tab" data-tab="history">History</a>
                    <a href="#" class="tab" data-tab="templates">Templates</a>
                </div>
                
                <div id="tab-create" class="tab-content active">
                    <div class="card bg-base-100 shadow-xl">
                        <div class="card-body">
                            <h2 class="card-title">Generate New Checkout</h2>
                            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                                <div class="form-control">
                                    <label class="label">Select User</label>
                                    <select class="select select-bordered" id="checkout_user">
                                        <option value="">-- Select User --</option>
                                    </select>
                                </div>
                                <div class="form-control">
                                    <label class="label">Select Plan</label>
                                    <select class="select select-bordered" id="checkout_plan">
                                        <option value="">-- Select Plan --</option>
                                    </select>
                                </div>
                            </div>
                            <button class="btn btn-primary mt-4" onclick="BillingComponent.generateCheckout()">
                                <i class="fas fa-shopping-cart"></i> Generate Checkout
                            </button>
                            <div id="checkout-result" class="mt-4">
                                <!-- Checkout result -->
                            </div>
                        </div>
                    </div>
                </div>
                
                <div id="tab-history" class="tab-content">
                    <div class="card bg-base-100 shadow-xl">
                        <div class="card-body">
                            <p class="text-center text-base-content/60">Checkout history coming soon...</p>
                        </div>
                    </div>
                </div>
                
                <div id="tab-templates" class="tab-content">
                    <div class="card bg-base-100 shadow-xl">
                        <div class="card-body">
                            <p class="text-center text-base-content/60">Checkout templates coming soon...</p>
                        </div>
                    </div>
                </div>
            `,
            
            // Observability - AI Usage
            'observe-ai': () => `
                <div class="mb-6">
                    <h1 class="text-3xl font-bold">AI Usage Analytics</h1>
                    <p class="text-base-content/60">Monitor AI provider usage and costs</p>
                </div>
                
                <!-- Tabs for future expansion -->
                <div class="tabs tabs-boxed mb-6">
                    <a href="#" class="tab tab-active" data-tab="logs">Recent Logs</a>
                    <a href="#" class="tab" data-tab="analytics">Analytics</a>
                    <a href="#" class="tab" data-tab="costs">Cost Breakdown</a>
                </div>
                
                <div id="tab-logs" class="tab-content active">
                    <div class="card bg-base-100 shadow-xl">
                        <div class="card-body">
                            <h2 class="card-title">Recent AI Usage Logs</h2>
                            <div class="flex gap-2 mb-4">
                                <button class="btn btn-sm btn-primary" onclick="loadAILogs()">Load Logs</button>
                                <button class="btn btn-sm btn-secondary" onclick="loadAISnapshot()">Snapshot</button>
                            </div>
                            <div id="ai-logs-output">
                                <!-- Dynamic content -->
                            </div>
                        </div>
                    </div>
                </div>
                
                <div id="tab-analytics" class="tab-content">
                    <div class="card bg-base-100 shadow-xl">
                        <div class="card-body">
                            <p class="text-center text-base-content/60">AI usage analytics coming soon...</p>
                        </div>
                    </div>
                </div>
                
                <div id="tab-costs" class="tab-content">
                    <div class="card bg-base-100 shadow-xl">
                        <div class="card-body">
                            <p class="text-center text-base-content/60">Cost breakdown analysis coming soon...</p>
                        </div>
                    </div>
                </div>
            `,
            
            // Observability - Credits Ledger
            'observe-credits': () => `
                <div class="mb-6">
                    <h1 class="text-3xl font-bold">Credits Ledger</h1>
                    <p class="text-base-content/60">Track credit transactions and balance history</p>
                </div>
                
                <!-- Tabs for future expansion -->
                <div class="tabs tabs-boxed mb-6">
                    <a href="#" class="tab tab-active" data-tab="ledger">Transactions</a>
                    <a href="#" class="tab" data-tab="balance">Balance History</a>
                    <a href="#" class="tab" data-tab="reports">Reports</a>
                </div>
                
                <div id="tab-ledger" class="tab-content active">
                    <div class="card bg-base-100 shadow-xl">
                        <div class="card-body">
                            <h2 class="card-title">Credit Transactions</h2>
                            <div class="form-control mb-4">
                                <label class="label">Filter by User ID</label>
                                <input type="text" class="input input-bordered" id="ledger_user_filter" placeholder="Optional" />
                            </div>
                            <button class="btn btn-primary" onclick="loadCreditsLedger()">Load Ledger</button>
                            <div id="credits-ledger-output" class="mt-4">
                                <!-- Dynamic content -->
                            </div>
                        </div>
                    </div>
                </div>
                
                <div id="tab-balance" class="tab-content">
                    <div class="card bg-base-100 shadow-xl">
                        <div class="card-body">
                            <p class="text-center text-base-content/60">Balance history visualization coming soon...</p>
                        </div>
                    </div>
                </div>
                
                <div id="tab-reports" class="tab-content">
                    <div class="card bg-base-100 shadow-xl">
                        <div class="card-body">
                            <p class="text-center text-base-content/60">Credit reports coming soon...</p>
                        </div>
                    </div>
                </div>
            `,
            
            // Observability - Rollout Manager
            'observe-rollouts': () => `
                <div class="mb-6">
                    <h1 class="text-3xl font-bold">Rollout Manager</h1>
                    <p class="text-base-content/60">Manage and monitor credit rollouts</p>
                </div>
                
                <!-- Tabs for future expansion -->
                <div class="tabs tabs-boxed mb-6">
                    <a href="#" class="tab tab-active" data-tab="execute">Execute</a>
                    <a href="#" class="tab" data-tab="history">History</a>
                    <a href="#" class="tab" data-tab="automation">Automation</a>
                </div>
                
                <div id="tab-execute" class="tab-content active">
                    <div class="card bg-base-100 shadow-xl">
                        <div class="card-body">
                            <h2 class="card-title">Rollout Operations</h2>
                            <div class="flex gap-2 mb-4">
                                <button class="btn btn-primary" onclick="previewRollout()">Preview</button>
                                <button class="btn btn-warning" onclick="runRollout()">Run Rollout</button>
                            </div>
                            <div id="rollout-output">
                                <!-- Dynamic content -->
                            </div>
                        </div>
                    </div>
                </div>
                
                <div id="tab-history" class="tab-content">
                    <div class="card bg-base-100 shadow-xl">
                        <div class="card-body">
                            <p class="text-center text-base-content/60">Rollout history coming soon...</p>
                        </div>
                    </div>
                </div>
                
                <div id="tab-automation" class="tab-content">
                    <div class="card bg-base-100 shadow-xl">
                        <div class="card-body">
                            <p class="text-center text-base-content/60">Rollout automation settings coming soon...</p>
                        </div>
                    </div>
                </div>
            `,
            
            // Configuration - Flow Mappings
            'config-flows': () => `
                <div class="mb-6">
                    <h1 class="text-3xl font-bold">Flow Mappings</h1>
                    <p class="text-base-content/60">Gestione mapping flow_key → flow_id per app</p>
                </div>
                
                <!-- Flow Mappings by App -->
                <div id="flow-mappings-container" class="space-y-6">
                    <div class="loading loading-spinner loading-lg mx-auto"></div>
                    <p class="text-center">Caricamento mappings...</p>
                </div>
                
                <!-- Add New Mapping -->
                <div class="card bg-base-100 shadow-xl mt-6">
                    <div class="card-body">
                        <h2 class="card-title">Add New Flow Mapping</h2>
                        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div class="form-control">
                                <label class="label">App ID</label>
                                <input type="text" class="input input-bordered" id="new_flow_app_id" placeholder="my_app" />
                            </div>
                            <div class="form-control">
                                <label class="label">Flow Key</label>
                                <input type="text" class="input input-bordered" id="new_flow_key" placeholder="content_generator" />
                            </div>
                            <div class="form-control">
                                <label class="label">Flow ID (from Flowise)</label>
                                <input type="text" class="input input-bordered" id="new_flow_id" placeholder="b52ba55e-fc16-404f..." />
                            </div>
                            <div class="form-control">
                                <label class="label">Node Names (comma-separated)</label>
                                <input type="text" class="input input-bordered" id="new_node_names" placeholder="agentAgentflow_0,llmAgentflow_1" />
                            </div>
                            <div class="form-control">
                                <label class="label cursor-pointer justify-start gap-4">
                                    <input type="checkbox" class="checkbox checkbox-primary" id="new_is_conversational" />
                                    <span class="label-text">
                                        <i class="fas fa-comments text-primary mr-2"></i>
                                        <strong>Conversational Mode</strong> - Mantiene il contesto tra chiamate usando session_id
                                    </span>
                                </label>
                            </div>
                        </div>
                        <div class="card-actions justify-end mt-4">
                            <button class="btn btn-primary" onclick="ConfigurationComponent.addNewFlowMapping()">Add Flow Mapping</button>
                        </div>
                    </div>
                </div>
            `,
            
            // Configuration - Security
            'config-security': () => `
                <div class="mb-6">
                    <h1 class="text-3xl font-bold">Security & Credentials</h1>
                    <p class="text-base-content/60">Manage system credentials and security settings</p>
                </div>
                
                <!-- Tabs for future expansion -->
                <div class="tabs tabs-boxed mb-6">
                    <a href="#" class="tab tab-active" data-tab="credentials">Credentials</a>
                    <a href="#" class="tab" data-tab="rotation">Key Rotation</a>
                    <a href="#" class="tab" data-tab="audit">Audit Log</a>
                </div>
                
                <div id="tab-credentials" class="tab-content active">
                    <!-- System Credentials -->
                    <div class="card bg-base-100 shadow-xl mb-6">
                        <div class="card-body">
                            <h2 class="card-title">
                                <i class="fas fa-server text-primary"></i>
                                System Credentials
                            </h2>
                            <div class="alert alert-info mb-4">
                                <i class="fas fa-info-circle"></i>
                                <span>These credentials are required for core system functionality</span>
                            </div>
                            
                            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                                <div class="form-control">
                                    <label class="label">
                                        <span class="label-text">Supabase URL</span>
                                    </label>
                                    <input type="text" class="input input-bordered" id="sys_supabase_url" placeholder="https://xxx.supabase.co" />
                                </div>
                                <div class="form-control">
                                    <label class="label">
                                        <span class="label-text">Supabase Service Key</span>
                                    </label>
                                    <input type="password" class="input input-bordered" id="sys_supabase_key" placeholder="eyJhbGciOi..." />
                                </div>
                                <div class="form-control">
                                    <label class="label">
                                        <span class="label-text">Admin Key</span>
                                    </label>
                                    <input type="password" class="input input-bordered" id="sys_admin_key" placeholder="Generated admin key" />
                                </div>
                                <div class="form-control">
                                    <label class="label">
                                        <span class="label-text">Encryption Key</span>
                                    </label>
                                    <input type="password" class="input input-bordered" id="sys_encryption_key" placeholder="Fernet encryption key" />
                                </div>
                            </div>
                            
                            <div class="card-actions justify-end mt-4">
                                <button class="btn btn-secondary" onclick="ConfigurationComponent.testSystemConnection()">Test Supabase</button>
                                <button class="btn btn-primary" onclick="ConfigurationComponent.saveSystemCredentials()">Save System Credentials</button>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Provider Credentials -->
                    <div class="card bg-base-100 shadow-xl mb-6">
                        <div class="card-body">
                            <h2 class="card-title">
                                <i class="fas fa-plug text-warning"></i>
                                Provider Credentials
                            </h2>
                            <div class="alert alert-warning mb-4">
                                <i class="fas fa-shield-alt"></i>
                                <span>These credentials are encrypted and stored in Supabase</span>
                            </div>
                            
                            <!-- LemonSqueezy -->
                            <div class="collapse collapse-arrow bg-base-200 mb-2">
                                <input type="checkbox" />
                                <div class="collapse-title font-medium">
                                    <i class="fas fa-lemon text-yellow-500"></i>
                                    LemonSqueezy Configuration
                                </div>
                                <div class="collapse-content">
                                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
                                        <div class="form-control">
                                            <label class="label">
                                                <span class="label-text">API Key</span>
                                            </label>
                                            <input type="password" class="input input-bordered" id="ls_api_key" placeholder="Your LemonSqueezy API key" />
                                        </div>
                                        <div class="form-control">
                                            <label class="label">
                                                <span class="label-text">Store ID</span>
                                            </label>
                                            <input type="text" class="input input-bordered" id="ls_store_id" placeholder="12345" />
                                        </div>
                                        <div class="form-control md:col-span-2">
                                            <label class="label">
                                                <span class="label-text">Webhook Secret</span>
                                            </label>
                                            <input type="password" class="input input-bordered" id="ls_webhook_secret" placeholder="Webhook signing secret" />
                                        </div>
                                    </div>
                                    <div class="flex gap-2 mt-4">
                                        <button class="btn btn-secondary btn-sm" onclick="ConfigurationComponent.testLemonSqueezy()">Test Connection</button>
                                        <button class="btn btn-primary btn-sm" onclick="ConfigurationComponent.saveLemonSqueezy()">Save LemonSqueezy</button>
                                    </div>
                                </div>
                            </div>
                            
                            <!-- Flowise -->
                            <div class="collapse collapse-arrow bg-base-200">
                                <input type="checkbox" />
                                <div class="collapse-title font-medium">
                                    <i class="fas fa-robot text-blue-500"></i>
                                    Flowise/AI Configuration
                                </div>
                                <div class="collapse-content">
                                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
                                        <div class="form-control">
                                            <label class="label">
                                                <span class="label-text">Base URL</span>
                                            </label>
                                            <input type="text" class="input input-bordered" id="flowise_base_url" placeholder="https://your-flowise.com/api/v1/prediction" />
                                        </div>
                                        <div class="form-control">
                                            <label class="label">
                                                <span class="label-text">API Key</span>
                                            </label>
                                            <input type="password" class="input input-bordered" id="flowise_api_key" placeholder="Your Flowise API key" />
                                        </div>
                                    </div>
                                    <div class="flex gap-2 mt-4">
                                        <button class="btn btn-secondary btn-sm" onclick="ConfigurationComponent.testFlowise()">Test Connection</button>
                                        <button class="btn btn-primary btn-sm" onclick="ConfigurationComponent.saveFlowise()">Save Flowise</button>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div id="tab-rotation" class="tab-content">
                    <div class="card bg-base-100 shadow-xl">
                        <div class="card-body">
                            <h2 class="card-title">Key Rotation & Management</h2>
                            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                                <div class="card bg-base-200">
                                    <div class="card-body">
                                        <h3 class="card-title text-sm">Generate New Admin Key</h3>
                                        <p class="text-xs text-base-content/60">Generate a new secure admin key</p>
                                        <button class="btn btn-warning btn-sm mt-2" onclick="ConfigurationComponent.generateNewAdminKey()">Generate</button>
                                    </div>
                                </div>
                                <div class="card bg-base-200">
                                    <div class="card-body">
                                        <h3 class="card-title text-sm">Rotate Encryption Key</h3>
                                        <p class="text-xs text-base-content/60">Generate new encryption key (re-encrypts all data)</p>
                                        <button class="btn btn-error btn-sm mt-2" onclick="ConfigurationComponent.rotateEncryptionKey()">Rotate</button>
                                    </div>
                                </div>
                                <div class="card bg-base-200">
                                    <div class="card-body">
                                        <h3 class="card-title text-sm">Clear Credentials Cache</h3>
                                        <p class="text-xs text-base-content/60">Clear local credential cache</p>
                                        <button class="btn btn-ghost btn-sm mt-2" onclick="ConfigurationComponent.clearCredentialsCache()">Clear Cache</button>
                                    </div>
                                </div>
                                <div class="card bg-base-200">
                                    <div class="card-body">
                                        <h3 class="card-title text-sm">Fix Encryption Issues</h3>
                                        <p class="text-xs text-base-content/60">Repair corrupted encrypted credentials</p>
                                        <button class="btn btn-warning btn-sm mt-2" onclick="ConfigurationComponent.fixEncryptionIssues()">Fix Encryption</button>
                                    </div>
                                </div>
                                <div class="card bg-base-200">
                                    <div class="card-body">
                                        <h3 class="card-title text-sm">Export Credentials</h3>
                                        <p class="text-xs text-base-content/60">Export for backup (encrypted)</p>
                                        <button class="btn btn-info btn-sm mt-2" onclick="ConfigurationComponent.exportCredentials()">Export</button>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div id="tab-audit" class="tab-content">
                    <div class="card bg-base-100 shadow-xl">
                        <div class="card-body">
                            <h2 class="card-title">Security Audit Log</h2>
                            <div class="overflow-x-auto">
                                <table class="table w-full">
                                    <thead>
                                        <tr>
                                            <th>Timestamp</th>
                                            <th>Action</th>
                                            <th>Provider</th>
                                            <th>Status</th>
                                        </tr>
                                    </thead>
                                    <tbody id="audit-log-table">
                                        <tr>
                                            <td colspan="4" class="text-center text-base-content/60">No audit logs available</td>
                                        </tr>
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </div>
                </div>
            `,
            
            // Configuration - Initial Setup
            'config-setup': () => `
                <div class="mb-6">
                    <h1 class="text-3xl font-bold">Initial Setup</h1>
                    <p class="text-base-content/60">One-time configuration and setup guides</p>
                </div>
                
                <!-- Tabs for future expansion -->
                <div class="tabs tabs-boxed mb-6">
                    <a href="#" class="tab tab-active" data-tab="wizard">Setup Wizard</a>
                    <a href="#" class="tab" data-tab="guides">Guides</a>
                    <a href="#" class="tab" data-tab="healthcheck">Health Check</a>
                </div>
                
                <div id="tab-wizard" class="tab-content active">
                    <div class="card bg-base-100 shadow-xl">
                        <div class="card-body">
                            <h2 class="card-title">Setup Wizard</h2>
                            <div class="alert alert-info mb-4">
                                <i class="fas fa-info-circle"></i>
                                <div>
                                    <h3 class="font-bold">One-time Setup</h3>
                                    <p>Run the setup wizard only during initial installation</p>
                                </div>
                            </div>
                            <a href="/core/v1/setup/wizard" class="btn btn-primary" target="_blank">
                                <i class="fas fa-magic"></i> Open Setup Wizard
                            </a>
                        </div>
                    </div>
                </div>
                
                <div id="tab-guides" class="tab-content">
                    <div class="card bg-base-100 shadow-xl">
                        <div class="card-body">
                            <h2 class="card-title">Setup Guides</h2>
                            
                            <div class="collapse collapse-arrow bg-base-200">
                                <input type="checkbox" />
                                <div class="collapse-title font-medium">
                                    Supabase Configuration
                                </div>
                                <div class="collapse-content">
                                    <ol class="list-decimal list-inside space-y-2">
                                        <li>Go to your Supabase dashboard</li>
                                        <li>Navigate to Settings → API</li>
                                        <li>Copy the Project URL</li>
                                        <li>Copy the Service Role Key (secret)</li>
                                        <li>Paste these values in the setup wizard</li>
                                    </ol>
                                </div>
                            </div>
                            
                            <div class="collapse collapse-arrow bg-base-200 mt-2">
                                <input type="checkbox" />
                                <div class="collapse-title font-medium">
                                    LemonSqueezy Configuration
                                </div>
                                <div class="collapse-content">
                                    <ol class="list-decimal list-inside space-y-2">
                                        <li>Log into your LemonSqueezy account</li>
                                        <li>Go to Settings → API</li>
                                        <li>Generate a new API key</li>
                                        <li>Copy your Store ID from the dashboard</li>
                                        <li>Set up a webhook endpoint: <code>/core/v1/billing/webhook</code></li>
                                        <li>Copy the webhook signing secret</li>
                                    </ol>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div id="tab-healthcheck" class="tab-content">
                    <div class="card bg-base-100 shadow-xl">
                        <div class="card-body">
                            <p class="text-center text-base-content/60">System health check coming soon...</p>
                        </div>
                    </div>
                </div>
            `,
            
            testing: () => `
                <div class="mb-6">
                    <h1 class="text-3xl font-bold">Testing Suite</h1>
                    <p class="text-base-content/60">Verifica completa di servizi, integrazioni e flussi operativi</p>
                </div>
                
                <!-- Alert per ambiente locale -->
                <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    <div class="alert alert-info lg:col-span-2">
                        <i class="fas fa-info-circle"></i>
                        <div>
                            <h3 class="font-bold">Ambiente di sviluppo locale</h3>
                            <p>I webhook reali non possono raggiungere localhost. Opzioni:</p>
                            <ul class="list-disc list-inside mt-2">
                                <li>Usa "Simulate webhook" per test locali</li>
                                <li>Configura ngrok: <code class="text-xs bg-base-300 px-1 rounded">ngrok http 5050</code></li>
                                <li>Imposta l'URL pubblico di ngrok come webhook nel provider</li>
                            </ul>
                        </div>
                    </div>
                    <!-- Test Infrastructure -->
                <div class="card bg-base-100 shadow-xl">
                    <div class="card-body">
                            <h2 class="card-title">
                                <i class="fas fa-database text-primary"></i>
                                Infrastructure Tests
                            </h2>
                            
                            <!-- Supabase -->
                            <div class="mb-4">
                                <div class="flex justify-between items-center mb-2">
                                    <h3 class="font-semibold">Supabase Connection</h3>
                                    <span id="supabase-status" class="badge badge-ghost">Not tested</span>
                                </div>
                                <button class="btn btn-sm btn-primary w-full" onclick="TestingComponent.testSupabase()">
                                    <i class="fas fa-play"></i> Test Connection
                                </button>
                                <div id="test-supabase-output" class="mt-2">
                                    <pre class="bg-base-200 p-2 rounded text-xs hidden"></pre>
                                </div>
                            </div>
                            
                            <!-- Payment Provider -->
                            <div class="divider my-2"></div>
                            <div>
                                <div class="flex justify-between items-center mb-2">
                                    <h3 class="font-semibold">Payment Provider</h3>
                                    <span id="provider-status" class="badge badge-ghost">Not tested</span>
                                </div>
                                <button class="btn btn-sm btn-primary w-full" onclick="TestingComponent.testProvider()">
                                    <i class="fas fa-play"></i> Test LemonSqueezy
                                </button>
                                <div id="test-provider-output" class="mt-2">
                                    <pre class="bg-base-200 p-2 rounded text-xs hidden"></pre>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- User Management -->
                    <div class="card bg-base-100 shadow-xl">
                        <div class="card-body">
                            <h2 class="card-title">
                                <i class="fas fa-users text-success"></i>
                                User Management
                            </h2>
                            
                            <!-- Create User -->
                            <div class="mb-4">
                                <h3 class="font-semibold mb-2">Create Test User</h3>
                            <div class="form-control">
                                    <label class="label">
                                        <span class="label-text">Email address</span>
                                    </label>
                                    <input type="email" class="input input-bordered" id="test_user_email" placeholder="test@example.com" />
                            </div>
                                <button class="btn btn-sm btn-success w-full mt-3" onclick="TestingComponent.createUser()">
                                    <i class="fas fa-user-plus"></i> Create User
                                </button>
                                <div id="test-user-output" class="mt-2">
                                    <div class="hidden" id="user-result"></div>
                                </div>
                            </div>
                            
                            <!-- Affordability Check -->
                            <div class="divider my-2"></div>
                            <div>
                                <h3 class="font-semibold mb-2">Affordability Check</h3>
                                <div class="grid grid-cols-2 gap-2 mb-3">
                            <div class="form-control">
                                        <label class="label">
                                            <span class="label-text text-xs">User</span>
                                        </label>
                                        <select class="select select-bordered select-sm" id="aff_user_select"></select>
                            </div>
                                    <div class="form-control">
                                        <label class="label">
                                            <span class="label-text text-xs">App</span>
                                        </label>
                                        <select class="select select-bordered select-sm" id="aff_app_select"></select>
                        </div>
                        </div>
                                <button class="btn btn-sm btn-primary w-full" onclick="TestingComponent.affordabilityCheck()">
                                    <i class="fas fa-check-circle"></i> Check Affordability
                                </button>
                                <div id="aff-output" class="mt-2"></div>
                            </div>
                        </div>
                    </div>

                    <!-- Payment & Credits -->
                    <div class="card bg-base-100 shadow-xl lg:col-span-2">
                        <div class="card-body">
                            <h2 class="card-title">
                                <i class="fas fa-credit-card text-warning"></i>
                                Payment & Credits Testing
                            </h2>
                            
                            <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
                                <!-- Checkout Generation -->
                                <div>
                                    <h3 class="font-semibold mb-3">1. Generate Checkout</h3>
                                    <div class="grid grid-cols-2 gap-2 mb-3">
                                        <div class="form-control">
                            <label class="label">
                                                <span class="label-text text-xs">User</span>
                            </label>
                                            <select class="select select-bordered select-sm" id="test_checkout_user"></select>
                        </div>
                                        <div class="form-control">
                                            <label class="label">
                                                <span class="label-text text-xs">Plan</span>
                                            </label>
                                            <select class="select select-bordered select-sm" id="test_checkout_plan"></select>
                                        </div>
                                    </div>
                                    <button class="btn btn-primary w-full" onclick="TestingComponent.generateCheckout()">
                                        <i class="fas fa-shopping-cart"></i> Generate Checkout Link
                                    </button>
                                    <div id="test-checkout-output" class="mt-3"></div>
                                </div>
                                
                                <!-- Credit Monitoring -->
                                <div>
                                    <h3 class="font-semibold mb-3">2. Monitor Credits</h3>
                                    <div class="form-control mb-3">
                                        <label class="label">
                                            <span class="label-text text-xs">Expected credit increment</span>
                                        </label>
                                        <input type="number" class="input input-bordered input-sm" id="test_expected_increment" placeholder="5000" />
                                    </div>
                                    <div class="grid grid-cols-3 gap-2">
                                        <button class="btn btn-sm" onclick="TestingComponent.checkBalance()">
                                            <i class="fas fa-sync"></i> Check
                                        </button>
                                        <button class="btn btn-sm btn-primary" onclick="TestingComponent.startPollingBalance()">
                                            <i class="fas fa-play"></i> Poll
                                        </button>
                                        <button class="btn btn-sm btn-warning" onclick="TestingComponent.simulateWebhook()">
                                            <i class="fas fa-bolt"></i> Simulate
                                        </button>
                                    </div>
                                    <div id="test-balance-output" class="mt-3">
                                        <div class="stats shadow w-full hidden" id="balance-stats">
                                            <div class="stat">
                                                <div class="stat-title">Current Balance</div>
                                                <div class="stat-value text-primary" id="current-balance">-</div>
                                                <div class="stat-desc" id="balance-delta">No changes</div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            

                        </div>
                    </div>

                    <!-- Flow Execution -->
                    <div class="card bg-base-100 shadow-xl lg:col-span-2">
                        <div class="card-body">
                            <h2 class="card-title">
                                <i class="fas fa-rocket text-secondary"></i>
                                Flow Execution Test
                            </h2>
                            
                            <div class="grid grid-cols-1 md:grid-cols-3 gap-3 mb-4">
                                <div class="form-control">
                                    <label class="label">
                                        <span class="label-text">App ID</span>
                                    </label>
                                    <select class="select select-bordered" id="test_app_id"></select>
                                </div>
                                <div class="form-control">
                                    <label class="label">
                                        <span class="label-text">Flow Key</span>
                                    </label>
                                    <select class="select select-bordered" id="exec_flow_key"></select>
                                </div>
                                <div class="form-control">
                                    <label class="label">
                                        <span class="label-text">User</span>
                                    </label>
                                    <select class="select select-bordered" id="exec_user_select"></select>
                                </div>
                            </div>


                            
                            <div class="form-control mb-4">
                                <label class="label">
                                    <span class="label-text">Input JSON</span>
                                </label>
                                <textarea class="textarea textarea-bordered h-24 font-mono text-sm" id="test-input" placeholder='{"prompt":"Test prompt","context":"Testing flow execution"}'></textarea>
                            </div>
                            
                            <button class="btn btn-primary btn-lg w-full" onclick="TestingComponent.executeFlow()">
                            <i class="fas fa-play"></i> Execute Flow
                        </button>
                            
                            <div id="test-output" class="mt-4"></div>
                        </div>
                    </div>

                    <!-- Conversational Flow Test -->
                    <div class="card bg-base-100 shadow-xl lg:col-span-2">
                        <div class="card-body">
                            <div class="flex justify-between items-center mb-4">
                                <h2 class="card-title">
                                    <i class="fas fa-comments text-info"></i>
                                    Conversational Flow Test
                                </h2>
                                <div class="badge badge-info" id="conv-session-badge">No session</div>
                            </div>
                            
                            <div class="alert alert-info mb-4">
                                <i class="fas fa-info-circle"></i>
                                <span>Test flow conversazionali che mantengono il contesto tra messaggi</span>
                            </div>
                            
                            <div class="grid grid-cols-1 md:grid-cols-3 gap-3 mb-4">
                                <div class="form-control">
                                    <label class="label">
                                        <span class="label-text">App ID</span>
                                    </label>
                                    <select class="select select-bordered select-sm" id="conv_app_id"></select>
                                </div>
                                <div class="form-control">
                                    <label class="label">
                                        <span class="label-text">Flow Key</span>
                                    </label>
                                    <select class="select select-bordered select-sm" id="conv_flow_key"></select>
                                </div>
                                <div class="form-control">
                                    <label class="label">
                                        <span class="label-text">User</span>
                                    </label>
                                    <select class="select select-bordered select-sm" id="conv_user_select"></select>
                                </div>
                            </div>
                            
                            <!-- Chat Container -->
                            <div class="bg-base-200 rounded-lg p-4 mb-4 h-96 overflow-y-auto" id="chat-messages">
                                <div class="text-center text-base-content/60 py-8">
                                    <i class="fas fa-comment-dots text-4xl mb-2"></i>
                                    <p>Inizia una conversazione inviando un messaggio</p>
                                </div>
                            </div>
                            
                            <!-- Input -->
                            <div class="flex gap-2 mb-4">
                                <input 
                                    type="text" 
                                    class="input input-bordered flex-1" 
                                    id="chat-input" 
                                    placeholder="Scrivi un messaggio..."
                                    onkeypress="if(event.key==='Enter') TestingComponent.sendChatMessage()"
                                />
                                <button class="btn btn-primary" onclick="TestingComponent.sendChatMessage()">
                                    <i class="fas fa-paper-plane"></i>
                                </button>
                            </div>
                            
                            <!-- Actions -->
                            <div class="flex gap-2">
                                <button class="btn btn-warning btn-sm" onclick="TestingComponent.newConversation()">
                                    <i class="fas fa-plus"></i> Nuova Conversazione
                                </button>
                                <button class="btn btn-ghost btn-sm" onclick="TestingComponent.clearChat()">
                                    <i class="fas fa-trash"></i> Pulisci Chat
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            `
        };

        // Configuration - Initial Setup
        window.pageTemplates['config-setup'] = () => {
            return `
                <div class="space-y-6">
                    <div class="flex items-center gap-3">
                        <i class="fas fa-rocket text-2xl text-primary"></i>
                        <div>
                            <h1 class="text-3xl font-bold">Initial Setup</h1>
                            <p class="text-base-content/60">Configurazione sicura per il primo avvio</p>
                        </div>
                    </div>

                    <!-- Status Check -->
                    <div class="card bg-base-100 shadow-xl">
                        <div class="card-body">
                            <h2 class="card-title">
                                <i class="fas fa-info-circle text-info"></i>
                                Setup Status
                            </h2>
                            <div id="setup-status-content">
                                <div class="flex items-center gap-2">
                                    <span class="loading loading-spinner loading-sm"></span>
                                    <span>Checking setup status...</span>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Setup Form -->
                    <div class="card bg-base-100 shadow-xl" id="setup-form-card">
                        <div class="card-body">
                            <h2 class="card-title">
                                <i class="fas fa-cog text-warning"></i>
                                Configuration
                            </h2>
                            
                            <div class="alert alert-warning">
                                <i class="fas fa-shield-alt"></i>
                                <span><strong>Sicurezza:</strong> Le chiavi API saranno criptate e salvate su Supabase. Non verranno mai mostrate in plain text nei log.</span>
                            </div>

                            <!-- Step 1: Supabase -->
                            <div class="form-control">
                                <label class="label">
                                    <span class="label-text font-semibold">
                                        <span class="badge badge-primary badge-sm mr-2">1</span>
                                        Supabase Connection
                                    </span>
                                </label>
                                
                                <div class="grid grid-cols-1 gap-4">
                                    <div class="form-control">
                                        <label class="label">
                                            <span class="label-text">Supabase URL</span>
                                        </label>
                                        <input type="text" class="input input-bordered" id="supabase_url" placeholder="https://xxx.supabase.co" />
                                    </div>
                                    
                                    <div class="form-control">
                                        <label class="label">
                                            <span class="label-text">Supabase Service Key</span>
                                        </label>
                                        <input type="password" class="input input-bordered" id="supabase_key" placeholder="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." />
                                    </div>
                                </div>
                            </div>

                            <div class="divider"></div>

                            <!-- Step 2: LemonSqueezy -->
                            <div class="form-control">
                                <label class="label">
                                    <span class="label-text font-semibold">
                                        <span class="badge badge-primary badge-sm mr-2">2</span>
                                        LemonSqueezy Integration
                                    </span>
                                </label>
                                
                                <div class="grid grid-cols-1 gap-4">
                                    <div class="form-control">
                                        <label class="label">
                                            <span class="label-text">LemonSqueezy API Key</span>
                                        </label>
                                        <input type="password" class="input input-bordered" id="ls_api_key" placeholder="eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9..." />
                                    </div>
                                    
                                    <div class="form-control">
                                        <label class="label">
                                            <span class="label-text">Store ID</span>
                                        </label>
                                        <input type="text" class="input input-bordered" id="ls_store_id" placeholder="199395" />
                                    </div>
                                    
                                    <div class="form-control">
                                        <label class="label">
                                            <span class="label-text">Webhook Secret</span>
                                        </label>
                                        <input type="password" class="input input-bordered" id="ls_webhook_secret" placeholder="a93effd09a763d6c164aa61d2ccac4a4" />
                                    </div>
                                </div>
                            </div>

                            <div class="divider"></div>

                            <!-- Step 3: Flowise/AI Integration -->
                            <div class="form-control">
                                <label class="label">
                                    <span class="label-text font-semibold">
                                        <span class="badge badge-primary badge-sm mr-2">3</span>
                                        Flowise/AI Integration
                                    </span>
                                </label>
                                
                                <div class="grid grid-cols-1 gap-4">
                                    <div class="form-control">
                                        <label class="label">
                                            <span class="label-text">Flowise Base URL</span>
                                        </label>
                                        <input type="text" class="input input-bordered" id="flowise_base_url" placeholder="https://your-flowise.com/api/v1/prediction" />
                                        <label class="label">
                                            <span class="label-text-alt">URL del tuo server Flowise per eseguire i flow AI</span>
                                        </label>
                                    </div>
                                    
                                    <div class="form-control">
                                        <label class="label">
                                            <span class="label-text">Flowise API Key</span>
                                        </label>
                                        <input type="password" class="input input-bordered" id="flowise_api_key" placeholder="your-flowise-api-key" />
                                        <label class="label">
                                            <span class="label-text-alt">Chiave API per autenticarsi con Flowise</span>
                                        </label>
                                    </div>
                                </div>
                            </div>

                            <div class="divider"></div>

                            <!-- Step 4: Project Settings -->
                            <div class="form-control">
                                <label class="label">
                                    <span class="label-text font-semibold">
                                        <span class="badge badge-primary badge-sm mr-2">4</span>
                                        Project Settings
                                    </span>
                                </label>
                                
                                <div class="form-control">
                                    <label class="label">
                                        <span class="label-text">App/Project Name</span>
                                    </label>
                                    <input type="text" class="input input-bordered" id="app_name" value="default" placeholder="nome-progetto" />
                                </div>
                            </div>

                            <!-- Actions -->
                            <div class="card-actions justify-end mt-6">
                                <button class="btn btn-primary btn-lg" onclick="ConfigurationComponent.runSetup()" id="setup_btn">
                                    <i class="fas fa-rocket"></i>
                                    Completa Setup
                                </button>
                            </div>
                            
                            <div id="setup-result" class="mt-4"></div>
                        </div>
                    </div>
                </div>
            `
        };

        // Guides - Developer Documentation
        window.pageTemplates['guides'] = () => {
            return `
                <div class="space-y-6">
                    <div class="flex items-center gap-3">
                        <i class="fas fa-book text-2xl text-primary"></i>
                        <div>
                            <h1 class="text-3xl font-bold">Developer Guides</h1>
                            <p class="text-base-content/60">Documentazione completa degli endpoint e guida allo sviluppo</p>
                        </div>
                    </div>

                    <!-- Navigation Tabs -->
                    <div class="tabs tabs-boxed mb-6">
                        <a href="#" class="tab tab-active" data-tab="api-reference">API Reference</a>
                        <a href="#" class="tab" data-tab="auth">Auth</a>
                        <a href="#" class="tab" data-tab="development-guide">Development Guide</a>
                        <a href="#" class="tab" data-tab="architecture">Architecture</a>
                        <a href="#" class="tab" data-tab="examples">Examples</a>
                    </div>

                    <!-- API Reference Tab -->
                    <div id="tab-api-reference" class="tab-content active">
                        <div class="grid grid-cols-1 gap-6">
                            
                            <!-- Essential Endpoints -->
                            <div class="card bg-base-100 shadow-xl">
                                <div class="card-body">
                                    <h2 class="card-title text-primary">
                                        <i class="fas fa-rocket"></i>
                                        Endpoint Essenziali (per la tua app)
                                    </h2>
                                    
                                    <div class="alert alert-info mb-4">
                                        <i class="fas fa-info-circle"></i>
                                        <div>
                                            <p><strong>Endpoint per App Client</strong></p>
                                            <p class="text-sm mt-1">Questi endpoint sono pensati per essere chiamati dalle tue applicazioni frontend/client. Tutti richiedono autenticazione utente.</p>
                                        </div>
                                    </div>
                                    
                                    <div class="space-y-4">
                                        <!-- THE Main Endpoint -->
                                        <div class="collapse collapse-arrow bg-gradient-to-r from-primary/10 to-secondary/10 border border-primary/20">
                                            <input type="checkbox" />
                                            <div class="collapse-title font-medium">
                                                <span class="badge badge-primary badge-lg mr-2">⭐ POST</span>
                                                /core/v1/providers/flowise/execute
                                                <span class="badge badge-success badge-sm ml-2">MAIN ENDPOINT</span>
                                            </div>
                                            <div class="collapse-content">
                                                <div class="space-y-2">
                                                    <p><strong>🎯 L'endpoint che fa tutto:</strong> Esegue AI, gestisce crediti, pricing automatico</p>
                                                    <p><strong>Headers:</strong></p>
                                                    <pre class="bg-base-300 p-2 rounded text-sm">Authorization: Bearer &lt;user_token&gt;
Content-Type: application/json</pre>
                                                    <div class="alert alert-info mt-2">
                                                        <i class="fas fa-info-circle"></i>
                                                        <div class="text-sm">
                                                            <p><strong>App ID:</strong> Opzionale per single-tenant, richiesto per multi-tenant</p>
                                                            <ul class="list-disc list-inside mt-1">
                                                                <li><strong>Single-tenant:</strong> Flow Starter usa <code>CORE_APP_ID</code> dall'ambiente</li>
                                                                <li><strong>Multi-tenant:</strong> Aggiungi <code>X-App-Id: my-app</code> header</li>
                                                            </ul>
                                                        </div>
                                                    </div>
                                                    <p><strong>Body (semplicissimo):</strong></p>
                                                    <pre class="bg-base-300 p-2 rounded text-sm">{
  "flow_key": "content_generator",
  "data": {
    "prompt": "Scrivi un post LinkedIn su AI marketing"
  }
}</pre>
                                                    <p><strong>Risposta (tutto quello che ti serve):</strong></p>
                                                    <pre class="bg-base-300 p-2 rounded text-sm">{
  "result": {
    "text": "🚀 L'AI sta rivoluzionando il marketing...",
    "metadata": {...}
  }
  // Flow Starter gestisce pricing/crediti automaticamente
}</pre>
                                                    <p><strong>Errore crediti (402):</strong></p>
                                                    <pre class="bg-base-300 p-2 rounded text-sm">{
  "error_type": "insufficient_credits",
  "shortage": 2.5,
  "minimum_required": 5.0
}
// → Redirect utente a /pricing</pre>
                                                </div>
                                            </div>
                                        </div>

                                        <!-- Credits Balance -->
                                        <div class="collapse collapse-arrow bg-base-200">
                                            <input type="checkbox" />
                                            <div class="collapse-title font-medium">
                                                <span class="badge badge-success badge-sm mr-2">GET</span>
                                                /core/v1/credits/balance
                                                <span class="badge badge-ghost badge-sm ml-2">opzionale</span>
                                            </div>
                                            <div class="collapse-content">
                                                <div class="space-y-2">
                                                    <p><strong>Quando usarlo:</strong> Per mostrare saldo crediti nell'UI</p>
                                                    <p><strong>Headers:</strong></p>
                                                    <pre class="bg-base-300 p-2 rounded text-sm">Authorization: Bearer &lt;user_token&gt;</pre>
                                                    <p><strong>Risposta:</strong></p>
                                                    <pre class="bg-base-300 p-2 rounded text-sm">{ "credits": 1500.50 }</pre>
                                                </div>
                                            </div>
                                        </div>

                                        <!-- Checkout -->
                                        <div class="collapse collapse-arrow bg-base-200">
                                            <input type="checkbox" />
                                            <div class="collapse-title font-medium">
                                                <span class="badge badge-info badge-sm mr-2">POST</span>
                                                /core/v1/billing/checkout
                                                <span class="badge badge-ghost badge-sm ml-2">quando servono crediti</span>
                                            </div>
                                            <div class="collapse-content">
                                                <div class="space-y-2">
                                                    <p><strong>Quando usarlo:</strong> Per acquistare crediti quando finiscono</p>
                                                    <p><strong>Headers:</strong></p>
                                                    <pre class="bg-base-300 p-2 rounded text-sm">Authorization: Bearer &lt;user_token&gt;
Content-Type: application/json</pre>
                                                    <p><strong>Body:</strong></p>
                                                    <pre class="bg-base-300 p-2 rounded text-sm">{
  "credits": 5000,
  "amount_usd": 19.0
}</pre>
                                                    <p><strong>Risposta:</strong></p>
                                                    <pre class="bg-base-300 p-2 rounded text-sm">{
  "checkout_url": "https://lemonsqueezy.com/checkout/..."
}
// → Redirect utente a checkout_url</pre>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <!-- Advanced/Debug Endpoints -->
                            <div class="card bg-base-100 shadow-xl">
                                <div class="card-body">
                                    <h2 class="card-title text-secondary">
                                        <i class="fas fa-tools"></i>
                                        Endpoint Avanzati (debug/testing)
                                    </h2>
                                    
                                    <div class="alert alert-warning mb-4">
                                        <i class="fas fa-exclamation-triangle"></i>
                                        <span>Questi endpoint sono per debug, testing o casi speciali. Normalmente non li userai.</span>
                                    </div>
                                    
                                    <div class="space-y-4">
                                        <!-- OpenRouter Chat -->
                                        <div class="collapse collapse-arrow bg-base-200">
                                            <input type="checkbox" />
                                            <div class="collapse-title font-medium">
                                                <span class="badge badge-info badge-sm mr-2">POST</span>
                                                /core/v1/providers/openrouter/chat
                                            </div>
                                            <div class="collapse-content">
                                                <div class="space-y-2">
                                                    <p><strong>Descrizione:</strong> Esegue chat completion via OpenRouter con addebito automatico crediti</p>
                                                    <p><strong>Headers:</strong></p>
                                                    <pre class="bg-base-300 p-2 rounded text-sm">Authorization: Bearer &lt;supabase_token&gt;
Content-Type: application/json
Idempotency-Key: &lt;optional_unique_key&gt;</pre>
                                                    <p><strong>Body:</strong></p>
                                                    <pre class="bg-base-300 p-2 rounded text-sm">{
  "model": "openrouter/gpt-4o-mini",
  "messages": [
    {"role": "user", "content": "Ciao, come stai?"}
  ],
  "options": {
    "temperature": 0.7,
    "max_tokens": 1000
  }
}</pre>
                                                    <p><strong>Risposta:</strong></p>
                                                    <pre class="bg-base-300 p-2 rounded text-sm">{
  "response": {
    "choices": [{
      "message": {
        "role": "assistant",
        "content": "Ciao! Sto bene, grazie..."
      }
    }]
  },
  "usage": {
    "input_tokens": 15,
    "output_tokens": 25,
    "cost_credits": 2.5
  },
  "transaction_id": "txn_abc123"
}</pre>
                                                </div>
                                            </div>
                                        </div>

                                        <!-- Flowise Execute -->
                                        <div class="collapse collapse-arrow bg-base-200">
                                            <input type="checkbox" />
                                            <div class="collapse-title font-medium">
                                                <span class="badge badge-info badge-sm mr-2">POST</span>
                                                /core/v1/providers/flowise/execute
                                            </div>
                                            <div class="collapse-content">
                                                <div class="space-y-2">
                                                    <p><strong>Descrizione:</strong> Esegue workflow AI complessi via Flowise con controllo affordability e addebito reale</p>
                                                    <p><strong>Headers:</strong></p>
                                                    <pre class="bg-base-300 p-2 rounded text-sm">Authorization: Bearer &lt;supabase_token&gt;
X-App-Id: &lt;app_identifier&gt;
Content-Type: application/json
Idempotency-Key: &lt;optional_unique_key&gt;</pre>
                                                    <p><strong>Body con flow_key (consigliato):</strong></p>
                                                    <pre class="bg-base-300 p-2 rounded text-sm">{
  "flow_key": "content_generator",
  "data": {
    "prompt": "Scrivi un post LinkedIn su AI",
    "tone": "professional",
    "length": "medium"
  }
}</pre>
                                                    <p><strong>Body con flow_id diretto:</strong></p>
                                                    <pre class="bg-base-300 p-2 rounded text-sm">{
  "flow_id": "abc-123-def-456",
  "node_names": ["chatOpenRouter_0"],
  "data": {
    "question": "Genera contenuto marketing"
  }
}</pre>
                                                    <p><strong>Risposta successo:</strong></p>
                                                    <pre class="bg-base-300 p-2 rounded text-sm">{
  "result": {
    "text": "Contenuto generato...",
    "metadata": {...}
  },
  "pricing": {
    "actual_cost_usd": 0.0025,
    "actual_cost_credits": 0.25,
    "markup_percent": 150.0,
    "public_price_usd": 0.00625
  },
  "flow": {
    "flow_id": "abc-123-def-456",
    "flow_key": "content_generator"
  }
}</pre>
                                                    <p><strong>Errore crediti insufficienti (HTTP 402):</strong></p>
                                                    <pre class="bg-base-300 p-2 rounded text-sm">{
  "error_type": "insufficient_credits",
  "can_afford": false,
  "minimum_required": 1.0,
  "available_credits": 0.5,
  "shortage": 0.5,
  "flow_key": "content_generator",
  "app_id": "my-app"
}</pre>
                                                </div>
                                            </div>
                                        </div>

                                        <!-- Flowise Affordability Check -->
                                        <div class="collapse collapse-arrow bg-base-200">
                                            <input type="checkbox" />
                                            <div class="collapse-title font-medium">
                                                <span class="badge badge-success badge-sm mr-2">GET</span>
                                                /core/v1/providers/flowise/affordability-check
                                            </div>
                                            <div class="collapse-content">
                                                <div class="space-y-2">
                                                    <p><strong>Descrizione:</strong> Verifica se l'utente può permettersi un flow senza eseguirlo</p>
                                                    <p><strong>Query Parameters:</strong></p>
                                                    <pre class="bg-base-300 p-2 rounded text-sm">?flow_key=content_generator&as_user_id=uuid (se admin)</pre>
                                                    <p><strong>Headers:</strong></p>
                                                    <pre class="bg-base-300 p-2 rounded text-sm">Authorization: Bearer &lt;token&gt; OR X-Admin-Key: &lt;admin_key&gt;
X-App-Id: &lt;app_identifier&gt;</pre>
                                                    <p><strong>Risposta:</strong></p>
                                                    <pre class="bg-base-300 p-2 rounded text-sm">{
  "app_id": "my-app",
  "minimum_required": 1.0,
  "estimated_credits": 0.25,
  "required_credits": 1.0,
  "available_credits": 5.0,
  "can_afford": true,
  "flow_key": "content_generator",
  "phase": "precheck_only"
}</pre>
                                                </div>
                                            </div>
                                        </div>

                                        <!-- Flowise Pricing -->
                                        <div class="collapse collapse-arrow bg-base-200">
                                            <input type="checkbox" />
                                            <div class="collapse-title font-medium">
                                                <span class="badge badge-success badge-sm mr-2">GET</span>
                                                /core/v1/providers/flowise/pricing
                                            </div>
                                            <div class="collapse-content">
                                                <div class="space-y-2">
                                                    <p><strong>Descrizione:</strong> Calcola il costo reale di un'esecuzione basato sul delta OpenRouter</p>
                                                    <p><strong>Query Parameters:</strong></p>
                                                    <pre class="bg-base-300 p-2 rounded text-sm">?usage_before_usd=0.1234&as_user_id=uuid (se admin)</pre>
                                                    <p><strong>Headers:</strong></p>
                                                    <pre class="bg-base-300 p-2 rounded text-sm">Authorization: Bearer &lt;token&gt; OR X-Admin-Key: &lt;admin_key&gt;</pre>
                                                    <p><strong>Risposta:</strong></p>
                                                    <pre class="bg-base-300 p-2 rounded text-sm">{
  "status": "ready",
  "actual_cost_usd": 0.0025,
  "actual_cost_credits": 0.25,
  "usage_before_usd": 0.1234,
  "usage_after_usd": 0.1259,
  "final_credit_multiplier": 100.0,
  "usd_multiplier": 2.5,
  "markup_percent": 150.0,
  "public_price_usd": 0.00625
}</pre>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <!-- Admin Endpoints -->
                            <div class="card bg-base-100 shadow-xl">
                                <div class="card-body">
                                    <h2 class="card-title text-warning">
                                        <i class="fas fa-shield-alt"></i>
                                        Admin Endpoints
                                    </h2>
                                    <div class="alert alert-warning mb-4">
                                        <i class="fas fa-exclamation-triangle"></i>
                                        <span>Questi endpoint richiedono <code>X-Admin-Key</code> o token admin</span>
                                    </div>
                                    
                                    <div class="space-y-4">
                                        <!-- Flow Configs -->
                                        <div class="collapse collapse-arrow bg-base-200">
                                            <input type="checkbox" />
                                            <div class="collapse-title font-medium">
                                                <span class="badge badge-success badge-sm mr-2">GET</span>
                                                /core/v1/admin/flow-configs
                                            </div>
                                            <div class="collapse-content">
                                                <div class="space-y-2">
                                                    <p><strong>Descrizione:</strong> Ottiene configurazione flow per app_id e flow_key</p>
                                                    <p><strong>Query Parameters:</strong></p>
                                                    <pre class="bg-base-300 p-2 rounded text-sm">?app_id=my-app&flow_key=content_generator</pre>
                                                    <p><strong>Headers:</strong></p>
                                                    <pre class="bg-base-300 p-2 rounded text-sm">X-Admin-Key: &lt;admin_key&gt;</pre>
                                                    <p><strong>Risposta:</strong></p>
                                                    <pre class="bg-base-300 p-2 rounded text-sm">{
  "found": true,
  "config": {
    "app_id": "my-app",
    "flow_key": "content_generator",
    "flow_id": "abc-123-def-456",
    "node_names": ["chatOpenRouter_0"]
  }
}</pre>
                                                </div>
                                            </div>
                                        </div>

                                        <!-- Create Flow Config -->
                                        <div class="collapse collapse-arrow bg-base-200">
                                            <input type="checkbox" />
                                            <div class="collapse-title font-medium">
                                                <span class="badge badge-info badge-sm mr-2">POST</span>
                                                /core/v1/admin/flow-configs
                                            </div>
                                            <div class="collapse-content">
                                                <div class="space-y-2">
                                                    <p><strong>Descrizione:</strong> Crea o aggiorna configurazione flow</p>
                                                    <p><strong>Headers:</strong></p>
                                                    <pre class="bg-base-300 p-2 rounded text-sm">X-Admin-Key: &lt;admin_key&gt;
Content-Type: application/json</pre>
                                                    <p><strong>Body:</strong></p>
                                                    <pre class="bg-base-300 p-2 rounded text-sm">{
  "app_id": "my-app",
  "flow_key": "content_generator",
  "flow_id": "abc-123-def-456",
  "node_names": ["chatOpenRouter_0"]
}</pre>
                                                    <p><strong>Risposta:</strong></p>
                                                    <pre class="bg-base-300 p-2 rounded text-sm">{
  "status": "ok",
  "config": { ... }
}</pre>
                                                </div>
                                            </div>
                                        </div>

                                        <!-- User Creation -->
                                        <div class="collapse collapse-arrow bg-base-200">
                                            <input type="checkbox" />
                                            <div class="collapse-title font-medium">
                                                <span class="badge badge-info badge-sm mr-2">POST</span>
                                                /core/v1/admin/users
                                            </div>
                                            <div class="collapse-content">
                                                <div class="space-y-2">
                                                    <p><strong>Descrizione:</strong> Crea nuovo utente con provisioning automatico OpenRouter</p>
                                                    <p><strong>Headers:</strong></p>
                                                    <pre class="bg-base-300 p-2 rounded text-sm">X-Admin-Key: &lt;admin_key&gt;
Content-Type: application/json</pre>
                                                    <p><strong>Body:</strong></p>
                                                    <pre class="bg-base-300 p-2 rounded text-sm">{
  "email": "newuser@example.com",
  "password": "SecurePass123!",
  "full_name": "Nome Cognome"
}</pre>
                                                    <p><strong>Risposta:</strong></p>
                                                    <pre class="bg-base-300 p-2 rounded text-sm">{
  "status": "success",
  "user_id": "uuid",
  "email": "newuser@example.com",
  "initial_credits": 1000.0,
  "openrouter": {
    "provisioned": true,
    "key_name": "user_abc123",
    "limit": 5.0
  }
}</pre>
                                                </div>
                                            </div>
                                        </div>

                                        <!-- Pricing Config -->
                                        <div class="collapse collapse-arrow bg-base-200">
                                            <input type="checkbox" />
                                            <div class="collapse-title font-medium">
                                                <span class="badge badge-success badge-sm mr-2">GET</span>
                                                <span class="badge badge-info badge-sm mr-2">PUT</span>
                                                /core/v1/admin/pricing/config
                                            </div>
                                            <div class="collapse-content">
                                                <div class="space-y-2">
                                                    <p><strong>Descrizione:</strong> Gestisce configurazione pricing e business logic</p>
                                                    <p><strong>Headers:</strong></p>
                                                    <pre class="bg-base-300 p-2 rounded text-sm">X-Admin-Key: &lt;admin_key&gt;
Content-Type: application/json (per PUT)</pre>
                                                    <p><strong>Query Parameters (opzionali):</strong></p>
                                                    <pre class="bg-base-300 p-2 rounded text-sm">?app_id=my-app</pre>
                                                    <p><strong>Body PUT:</strong></p>
                                                    <pre class="bg-base-300 p-2 rounded text-sm">{
  "monthly_revenue_target_usd": 10000.0,
  "fixed_monthly_costs_usd": [
    {"name": "Infrastructure", "cost_usd": 200.0},
    {"name": "Marketing", "cost_usd": 2000.0}
  ],
  "usd_to_credits": 100.0,
  "target_margin_multiplier": 2.5,
  "minimum_operation_cost_credits": 0.01,
  "flow_costs_usd": {
    "content_generator": 0.005,
    "data_analyzer": 0.015
  },
  "signup_initial_credits": 1000.0
}</pre>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <!-- Billing Endpoints -->
                            <div class="card bg-base-100 shadow-xl">
                                <div class="card-body">
                                    <h2 class="card-title text-accent">
                                        <i class="fas fa-credit-card"></i>
                                        Billing Endpoints
                                    </h2>
                                    
                                    <div class="space-y-4">
                                        <!-- Get Plans -->
                                        <div class="collapse collapse-arrow bg-base-200">
                                            <input type="checkbox" />
                                            <div class="collapse-title font-medium">
                                                <span class="badge badge-success badge-sm mr-2">GET</span>
                                                /core/v1/billing/plans
                                            </div>
                                            <div class="collapse-content">
                                                <div class="space-y-2">
                                                    <p><strong>Descrizione:</strong> Ottiene lista piani di subscription disponibili</p>
                                                    <p><strong>Risposta:</strong></p>
                                                    <pre class="bg-base-300 p-2 rounded text-sm">{
  "plans": [
    {
      "id": "starter",
      "name": "Starter Plan",
      "price_usd": 19.0,
      "credits": 5000,
      "type": "subscription",
      "popular": false
    },
    {
      "id": "pro",
      "name": "Pro Plan", 
      "price_usd": 79.0,
      "credits": 25000,
      "type": "subscription",
      "popular": true
    }
  ]
}</pre>
                                                </div>
                                            </div>
                                        </div>

                                        <!-- Create Checkout -->
                                        <div class="collapse collapse-arrow bg-base-200">
                                            <input type="checkbox" />
                                            <div class="collapse-title font-medium">
                                                <span class="badge badge-info badge-sm mr-2">POST</span>
                                                /core/v1/billing/checkout
                                            </div>
                                            <div class="collapse-content">
                                                <div class="space-y-2">
                                                    <p><strong>Descrizione:</strong> Crea sessione di checkout per acquisto crediti</p>
                                                    <p><strong>Headers:</strong></p>
                                                    <pre class="bg-base-300 p-2 rounded text-sm">Authorization: Bearer &lt;supabase_token&gt;
Content-Type: application/json</pre>
                                                    <p><strong>Body:</strong></p>
                                                    <pre class="bg-base-300 p-2 rounded text-sm">{
  "credits": 5000,
  "amount_usd": 19.0,
  "metadata": {
    "plan_id": "starter",
    "customer_email": "user@example.com"
  }
}</pre>
                                                    <p><strong>Risposta:</strong></p>
                                                    <pre class="bg-base-300 p-2 rounded text-sm">{
  "checkout_url": "https://lemonsqueezy.com/checkout/...",
  "checkout_id": "checkout_abc123"
}</pre>
                                                </div>
                                            </div>
                                        </div>

                                        <!-- Webhook -->
                                        <div class="collapse collapse-arrow bg-base-200">
                                            <input type="checkbox" />
                                            <div class="collapse-title font-medium">
                                                <span class="badge badge-info badge-sm mr-2">POST</span>
                                                /core/v1/billing/webhook
                                            </div>
                                            <div class="collapse-content">
                                                <div class="space-y-2">
                                                    <p><strong>Descrizione:</strong> Endpoint webhook per processare pagamenti completati</p>
                                                    <p><strong>Headers:</strong></p>
                                                    <pre class="bg-base-300 p-2 rounded text-sm">X-Signature: &lt;webhook_signature&gt;
Content-Type: application/json</pre>
                                                    <p><strong>Configurazione:</strong></p>
                                                    <p>Configura questo URL nel tuo provider di pagamento:</p>
                                                    <pre class="bg-base-300 p-2 rounded text-sm">https://your-domain.com/core/v1/billing/webhook</pre>
                                                    <p>Per sviluppo locale con ngrok:</p>
                                                    <pre class="bg-base-300 p-2 rounded text-sm">https://abc123.ngrok.io/core/v1/billing/webhook</pre>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <!-- Setup Endpoints -->
                            <div class="card bg-base-100 shadow-xl">
                                <div class="card-body">
                                    <h2 class="card-title text-info">
                                        <i class="fas fa-cog"></i>
                                        Setup & Configuration Endpoints
                                    </h2>
                                    
                                    <div class="space-y-4">
                                        <!-- Setup Status -->
                                        <div class="collapse collapse-arrow bg-base-200">
                                            <input type="checkbox" />
                                            <div class="collapse-title font-medium">
                                                <span class="badge badge-success badge-sm mr-2">GET</span>
                                                /core/v1/setup/status
                                            </div>
                                            <div class="collapse-content">
                                                <div class="space-y-2">
                                                    <p><strong>Descrizione:</strong> Verifica stato del setup iniziale</p>
                                                    <p><strong>Risposta:</strong></p>
                                                    <pre class="bg-base-300 p-2 rounded text-sm">{
  "setup_completed": true,
  "supabase_configured": true,
  "admin_key_configured": true,
  "credentials_encrypted": true,
  "flowise_configured": true,
  "next_action": "configure_plans"
}</pre>
                                                </div>
                                            </div>
                                        </div>

                                        <!-- Complete Setup -->
                                        <div class="collapse collapse-arrow bg-base-200">
                                            <input type="checkbox" />
                                            <div class="collapse-title font-medium">
                                                <span class="badge badge-info badge-sm mr-2">POST</span>
                                                /core/v1/setup/complete-setup
                                            </div>
                                            <div class="collapse-content">
                                                <div class="space-y-2">
                                                    <p><strong>Descrizione:</strong> Completa setup iniziale con tutte le credenziali</p>
                                                    <p><strong>Body:</strong></p>
                                                    <pre class="bg-base-300 p-2 rounded text-sm">{
  "supabase_url": "https://xxx.supabase.co",
  "supabase_service_key": "eyJhbGciOi...",
  "lemonsqueezy_api_key": "eyJ0eXAiOi...",
  "lemonsqueezy_store_id": "199395",
  "lemonsqueezy_webhook_secret": "a93effd09a...",
  "flowise_base_url": "https://flowise.com/api/v1/prediction",
  "flowise_api_key": "your-api-key",
  "app_name": "my-app"
}</pre>
                                                    <p><strong>Risposta:</strong></p>
                                                    <pre class="bg-base-300 p-2 rounded text-sm">{
  "status": "success",
  "message": "Setup completato!",
  "admin_key": "generated-admin-key",
  "encryption_key": "generated-encryption-key",
  "env_commands": [
    "SUPABASE_URL=\"https://xxx.supabase.co\"",
    "CORE_ADMIN_KEY=\"generated-admin-key\""
  ]
}</pre>
                                                </div>
                                            </div>
                                        </div>

                                        <!-- Generate Token -->
                                        <div class="collapse collapse-arrow bg-base-200">
                                            <input type="checkbox" />
                                            <div class="collapse-title font-medium">
                                                <span class="badge badge-info badge-sm mr-2">POST</span>
                                                /core/v1/admin/generate-token
                                            </div>
                                            <div class="collapse-content">
                                                <div class="space-y-2">
                                                    <p><strong>Descrizione:</strong> Genera access token Supabase per utente esistente</p>
                                                    <p><strong>Body:</strong></p>
                                                    <pre class="bg-base-300 p-2 rounded text-sm">{
  "email": "user@example.com",
  "password": "userpassword"
}</pre>
                                                    <p><strong>Risposta:</strong></p>
                                                    <pre class="bg-base-300 p-2 rounded text-sm">{
  "access_token": "eyJhbGciOi..."
}</pre>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Auth Tab -->
                    <div id="tab-auth" class="tab-content">
                        <div class="card bg-base-100 shadow-xl">
                            <div class="card-body">
                                <h2 class="card-title text-primary"><i class="fas fa-user-shield"></i> Auth (Supabase)</h2>
                                <p class="text-sm">Flow Starter espone proxy semplici per Supabase Auth, utili per gli sviluppatori di app.</p>
                                <div class="mt-4 space-y-4">
                                    <div>
<pre class="bg-base-300 p-2 rounded text-sm">POST /core/v1/auth/signup
Body: { "email": "user@example.com", "password": "Passw0rd!", "redirect_to": "https://app.com/welcome" }</pre>
                                    </div>
                                    <div>
<pre class="bg-base-300 p-2 rounded text-sm">POST /core/v1/auth/login
Body: { "email": "user@example.com", "password": "Passw0rd!" }
→ { access_token, refresh_token, expires_in, ... }</pre>
                                    </div>
                                    <div>
<pre class="bg-base-300 p-2 rounded text-sm">POST /core/v1/auth/refresh
Body: { "refresh_token": "..." }</pre>
                                    </div>
                                    <div>
<pre class="bg-base-300 p-2 rounded text-sm">POST /core/v1/auth/logout
Headers: Authorization: Bearer &lt;access_token&gt;</pre>
                                    </div>
                                    <div>
<pre class="bg-base-300 p-2 rounded text-sm">GET /core/v1/auth/user
Headers: Authorization: Bearer &lt;access_token&gt;</pre>
                                    </div>
                                    <div class="alert alert-info">
                                        <i class="fas fa-info-circle"></i>
                                        <div class="text-sm">Config richieste sul Core: <code>SUPABASE_URL</code> e <code>SUPABASE_ANON_KEY</code>. Nel client skeleton trovi gli helper: <code>loginAuth</code>, <code>signupAuth</code>, <code>logoutAuth</code>, <code>getUserAuth</code>.</div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Development Guide Tab -->
                    <div id="tab-development-guide" class="tab-content">
                        <div class="space-y-6">
                            
                            <!-- Quick Start -->
                            <div class="card bg-base-100 shadow-xl">
                                <div class="card-body">
                                    <h2 class="card-title text-primary">
                                        <i class="fas fa-rocket"></i>
                                        Quick Start (5 minuti)
                                    </h2>
                                    
                                    <div class="steps">
                                        <div class="step step-primary">
                                            <div class="step-content">
                                                <h3 class="font-bold">1. Setup Supabase</h3>
                                                <ul class="list-disc list-inside text-sm space-y-1">
                                                    <li>Crea progetto su supabase.com</li>
                                                    <li>Esegui SQL schema: <code>sql/000_full_schema.sql</code></li>
                                                    <li>Copia URL progetto e Service Key</li>
                                                </ul>
                                            </div>
                                        </div>
                                        
                                        <div class="step step-primary">
                                            <div class="step-content">
                                                <h3 class="font-bold">2. Configurazione</h3>
                                                <pre class="bg-base-300 p-2 rounded text-sm"># Copia template
cp .env.example .env

# Configura variabili principali
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=your-service-key
OPENROUTER_PROVISIONING_KEY=your-openrouter-key</pre>
                                            </div>
                                        </div>
                                        
                                        <div class="step step-primary">
                                            <div class="step-content">
                                                <h3 class="font-bold">3. Avvio</h3>
                                                <pre class="bg-base-300 p-2 rounded text-sm"># Installa dipendenze
pip install -r requirements.txt

# Avvia server
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 5050</pre>
                                            </div>
                                        </div>
                                        
                                        <div class="step step-primary">
                                            <div class="step-content">
                                                <h3 class="font-bold">4. Test</h3>
                                                <pre class="bg-base-300 p-2 rounded text-sm"># Health check
curl http://127.0.0.1:5050/health

# Dashboard admin
open http://127.0.0.1:5050/core/v1/admin-ui/dashboard</pre>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <!-- Sviluppo Applicazioni -->
                            <div class="card bg-base-100 shadow-xl">
                                <div class="card-body">
                                    <h2 class="card-title text-secondary">
                                        <i class="fas fa-code"></i>
                                        Sviluppo Applicazioni su Flow Starter
                                    </h2>
                                    
                                    <div class="space-y-4">
                                        <div class="alert alert-info">
                                            <i class="fas fa-magic"></i>
                                            <div>
                                                <h3 class="font-bold">Filosofia: Plug & Play AI</h3>
                                                <p>Flow Starter è il <strong>"Stripe per l'AI"</strong>. La tua app fa una chiamata, riceve il risultato AI. Flow Starter gestisce tutto il resto: crediti, pricing, provider, sicurezza, addebiti.</p>
                                                <p class="mt-2 font-mono text-sm">app.call(flow_key, data) → ai_result ✨</p>
                                            </div>
                                        </div>

                                        <!-- Architettura Multi-Tenant -->
                                        <div class="collapse collapse-arrow bg-base-200">
                                            <input type="checkbox" />
                                            <div class="collapse-title font-medium">
                                                <i class="fas fa-building"></i>
                                                Architettura Multi-Tenant
                                            </div>
                                            <div class="collapse-content">
                                                <div class="space-y-3">
                                                    <p><strong>Concetti chiave:</strong></p>
                                                    <ul class="list-disc list-inside space-y-1">
                                                        <li><strong>App ID:</strong> Identificato automaticamente da Flow Starter (via dominio o config)</li>
                                                        <li><strong>Flow Key:</strong> Nome semplice del workflow (es. "content_generator")</li>
                                                        <li><strong>Flow ID:</strong> ID tecnico Flowise (gestito da Flow Starter)</li>
                                                        <li><strong>Node Names:</strong> Configurazione automatica OpenRouter</li>
                                                    </ul>
                                                    
                                                    <div class="alert alert-warning mt-3">
                                                        <i class="fas fa-cog"></i>
                                                        <div>
                                                            <h4 class="font-bold text-sm">Modalità Deployment</h4>
                                                            <p class="text-xs">Flow Starter supporta due modalità:</p>
                                                            <ul class="list-disc list-inside text-xs mt-1">
                                                                <li><strong>Single-tenant:</strong> <code>CORE_APP_ID=my-app</code> nell'ambiente (più semplice)</li>
                                                                <li><strong>Multi-tenant:</strong> Header <code>X-App-Id</code> per ogni chiamata</li>
                                                            </ul>
                                                            <p class="text-xs mt-2 font-semibold">💡 Consiglio: Inizia single-tenant, migra a multi-tenant se necessario</p>
                                                        </div>
                                                    </div>
                                                    
                                                    <p><strong>Configurazione flow:</strong></p>
                                                    <pre class="bg-base-300 p-2 rounded text-sm"># Configura mapping flow_key → flow_id
POST /core/v1/admin/flow-configs
{
  "app_id": "my-saas-app",
  "flow_key": "content_generator", 
  "flow_id": "abc-123-def-456",
  "node_names": ["chatOpenRouter_0"]
}</pre>
                                                    
                                                    <p><strong>Utilizzo nel client (semplicissimo):</strong></p>
                                                    <pre class="bg-base-300 p-2 rounded text-sm"># L'app fa solo questo - Flow Starter gestisce tutto!
POST /core/v1/providers/flowise/execute
Headers: Authorization: Bearer &lt;user_token&gt;
{
  "flow_key": "content_generator",
  "data": {"prompt": "Genera post LinkedIn"}
}</pre>
                                                </div>
                                            </div>
                                        </div>

                                        <!-- Sistema Crediti -->
                                        <div class="collapse collapse-arrow bg-base-200">
                                            <input type="checkbox" />
                                            <div class="collapse-title font-medium">
                                                <i class="fas fa-coins"></i>
                                                Sistema Crediti e Pricing
                                            </div>
                                            <div class="collapse-content">
                                                <div class="space-y-3">
                                                    <p><strong>Logica di pricing:</strong></p>
                                                    <ol class="list-decimal list-inside space-y-1">
                                                        <li><strong>Pre-check affordability:</strong> Verifica crediti prima dell'esecuzione</li>
                                                        <li><strong>Esecuzione:</strong> Chiama provider AI (OpenRouter/Flowise)</li>
                                                        <li><strong>Misurazione costo reale:</strong> Delta usage OpenRouter</li>
                                                        <li><strong>Addebito finale:</strong> Crediti = costo_usd × moltiplicatori</li>
                                                    </ol>
                                                    
                                                    <p><strong>Moltiplicatori automatici:</strong></p>
                                                    <pre class="bg-base-300 p-2 rounded text-sm"># Calcolo automatico basato su business config
overhead_multiplier = 1 + (costi_fissi_mensili / revenue_target)
final_multiplier = overhead_multiplier × margin_target × usd_to_credits

# Esempio: 
# Costi fissi: $3000/mese, Revenue target: $10000/mese
# overhead_multiplier = 1 + (3000/10000) = 1.3
# final_multiplier = 1.3 × 2.5 × 100 = 325 crediti per $1 di costo AI</pre>
                                                    
                                                    <p><strong>Controllo affordability per-app:</strong></p>
                                                    <pre class="bg-base-300 p-2 rounded text-sm"># Configura soglia minima per app
PUT /core/v1/admin/pricing/config
{
  "flow_costs_usd": {
    "my-saas-app": 1.0  // Soglia minima: 1.0 crediti
  }
}</pre>
                                                </div>
                                            </div>
                                        </div>

                                        <!-- Integrazione Frontend -->
                                        <div class="collapse collapse-arrow bg-base-200">
                                            <input type="checkbox" />
                                            <div class="collapse-title font-medium">
                                                <i class="fas fa-desktop"></i>
                                                Integrazione Frontend
                                            </div>
                                            <div class="collapse-content">
                                                <div class="space-y-3">
                                                    <p><strong>Integrazione JavaScript Ultra-Semplice:</strong></p>
                                                    <pre class="bg-base-300 p-2 rounded text-sm">// config.js
const FLOW_STARTER = {
  API: 'https://your-core.com/core/v1'
};

// La UNICA funzione che ti serve
async function runAI(userToken, flowKey, data, appId = null) {
  const headers = {
    'Authorization': \`Bearer \${userToken}\`,
    'Content-Type': 'application/json'
  };
  
  // Solo per multi-tenant
  if (appId) headers['X-App-Id'] = appId;
  
  const response = await fetch(\`\${FLOW_STARTER.API}/providers/flowise/execute\`, {
    method: 'POST',
    headers,
    body: JSON.stringify({ flow_key: flowKey, data })
  });

  if (response.status === 402) {
    // Unico errore da gestire: crediti insufficienti
    throw new Error('CREDITS_NEEDED');
  }

  const result = await response.json();
  return result.result; // Solo il contenuto AI
}</pre>
                                                    
                                                    <p><strong>Esempio pratico:</strong></p>
                                                    <pre class="bg-base-300 p-2 rounded text-sm">// La tua app
async function generateContent(userToken, prompt) {
  try {
    const aiResult = await runAI(userToken, 'content_generator', {
      prompt: prompt
    });
    
    // Usa il risultato nell'UI
    return aiResult.text;
    
  } catch (error) {
    if (error.message === 'CREDITS_NEEDED') {
      // Redirect a pricing
      window.location.href = '/pricing';
    } else {
      console.error('AI Error:', error);
    }
  }
}

// Uso in React/Vue/Angular

// Single-tenant (più comune)
const content = await runAI(token, 'content_generator', {
  prompt: 'Scrivi post su AI'
});

// Multi-tenant (se necessario)
const content = await runAI(token, 'content_generator', {
  prompt: 'Scrivi post su AI'
}, 'my-app-id');

setContent(content.text); // Fatto! 🎉</pre>
                                                </div>
                                            </div>
                                        </div>

                                        <!-- Best Practices -->
                                        <div class="collapse collapse-arrow bg-base-200">
                                            <input type="checkbox" />
                                            <div class="collapse-title font-medium">
                                                <i class="fas fa-star"></i>
                                                Best Practices
                                            </div>
                                            <div class="collapse-content">
                                                <div class="space-y-3">
                                                    <div class="alert alert-success">
                                                        <i class="fas fa-thumbs-up"></i>
                                                        <div>
                                                            <h4 class="font-bold">Do's ✅</h4>
                                                            <ul class="list-disc list-inside space-y-1">
                                                                <li><strong>Usa flow_key:</strong> Più semplice di flow_id</li>
                                                                <li><strong>Gestisci solo 402:</strong> Crediti insufficienti → redirect pricing</li>
                                                                <li><strong>Mostra loading state:</strong> AI può richiedere 30-60 secondi</li>
                                                                <li><strong>Salva user token:</strong> Per chiamate successive</li>
                                                            </ul>
                                                        </div>
                                                    </div>
                                                    
                                                    <div class="alert alert-error">
                                                        <i class="fas fa-times-circle"></i>
                                                        <div>
                                                            <h4 class="font-bold">Don'ts ❌</h4>
                                                            <ul class="list-disc list-inside space-y-1">
                                                                <li><strong>Non fare affordability check:</strong> Flow Starter lo fa già</li>
                                                                <li><strong>Non gestire pricing:</strong> È automatico</li>
                                                                <li><strong>Non implementare retry:</strong> Flow Starter ha timeout intelligenti</li>
                                                                <li><strong>Non esporre API keys:</strong> Tutto server-side</li>
                                                            </ul>
                                                        </div>
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <!-- Workflow Sviluppo -->
                            <div class="card bg-base-100 shadow-xl">
                                <div class="card-body">
                                    <h2 class="card-title text-accent">
                                        <i class="fas fa-tasks"></i>
                                        Workflow di Sviluppo
                                    </h2>
                                    
                                    <div class="timeline">
                                        <div class="timeline-item">
                                            <div class="timeline-marker bg-primary text-primary-content">1</div>
                                            <div class="timeline-content">
                                                <h3 class="font-bold">Setup Iniziale</h3>
                                                <p>Configura Supabase, LemonSqueezy e Flowise tramite Setup Wizard</p>
                                                <div class="mt-2">
                                                    <a href="/core/v1/setup/wizard" class="btn btn-sm btn-primary" target="_blank">
                                                        <i class="fas fa-external-link-alt"></i> Setup Wizard
                                                    </a>
                                                </div>
                                            </div>
                                        </div>
                                        
                                        <div class="timeline-item">
                                            <div class="timeline-marker bg-secondary text-secondary-content">2</div>
                                            <div class="timeline-content">
                                                <h3 class="font-bold">Configurazione Business</h3>
                                                <p>Imposta pricing, margini e costi tramite Business Dashboard</p>
                                                <div class="mt-2">
                                                    <button class="btn btn-sm btn-secondary" onclick="navigate('business-config')">
                                                        <i class="fas fa-chart-line"></i> Business Config
                                                    </button>
                                                </div>
                                            </div>
                                        </div>
                                        
                                        <div class="timeline-item">
                                            <div class="timeline-marker bg-accent text-accent-content">3</div>
                                            <div class="timeline-content">
                                                <h3 class="font-bold">Creazione Flow</h3>
                                                <p>Crea workflow in Flowise e configura mapping flow_key → flow_id</p>
                                                <div class="mt-2">
                                                    <button class="btn btn-sm btn-accent" onclick="navigate('config-flows')">
                                                        <i class="fas fa-project-diagram"></i> Flow Mappings
                                                    </button>
                                                </div>
                                            </div>
                                        </div>
                                        
                                        <div class="timeline-item">
                                            <div class="timeline-marker bg-success text-success-content">4</div>
                                            <div class="timeline-content">
                                                <h3 class="font-bold">Test & Deploy</h3>
                                                <p>Testa i flow, verifica pricing e deploy in produzione</p>
                                                <div class="mt-2">
                                                    <button class="btn btn-sm btn-success" onclick="navigate('testing')">
                                                        <i class="fas fa-flask"></i> Testing Suite
                                                    </button>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Architecture Tab -->
                    <div id="tab-architecture" class="tab-content">
                        <div class="space-y-6">
                            
                            <!-- System Overview -->
                            <div class="card bg-base-100 shadow-xl">
                                <div class="card-body">
                                    <h2 class="card-title text-primary">
                                        <i class="fas fa-sitemap"></i>
                                        Architettura del Sistema
                                    </h2>
                                    
                                    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
                                        <!-- Components -->
                                        <div>
                                            <h3 class="font-bold mb-3">Componenti Principali</h3>
                                            <div class="space-y-2">
                                                <div class="badge badge-primary badge-lg w-full justify-start">
                                                    <i class="fas fa-server mr-2"></i>
                                                    FastAPI Core
                                                </div>
                                                <div class="badge badge-secondary badge-lg w-full justify-start">
                                                    <i class="fas fa-database mr-2"></i>
                                                    Supabase (PostgreSQL + Auth)
                                                </div>
                                                <div class="badge badge-accent badge-lg w-full justify-start">
                                                    <i class="fas fa-robot mr-2"></i>
                                                    OpenRouter (AI Models)
                                                </div>
                                                <div class="badge badge-info badge-lg w-full justify-start">
                                                    <i class="fas fa-project-diagram mr-2"></i>
                                                    Flowise (AI Workflows)
                                                </div>
                                                <div class="badge badge-warning badge-lg w-full justify-start">
                                                    <i class="fas fa-credit-card mr-2"></i>
                                                    LemonSqueezy (Payments)
                                                </div>
                                            </div>
                                        </div>
                                        
                                        <!-- Data Flow -->
                                        <div>
                                            <h3 class="font-bold mb-3">Flusso Dati</h3>
                                            <div class="space-y-3">
                                                <div class="alert alert-info">
                                                    <div class="text-sm">
                                                        <p><strong>1. Autenticazione:</strong> JWT Supabase verificato via JWKS</p>
                                                        <p><strong>2. Affordability:</strong> Pre-check crediti vs soglia app</p>
                                                        <p><strong>3. Provisioning:</strong> Chiavi OpenRouter iniettate nei nodi</p>
                                                        <p><strong>4. Esecuzione:</strong> Workflow Flowise con timeout intelligenti</p>
                                                        <p><strong>5. Misurazione:</strong> Delta usage OpenRouter</p>
                                                        <p><strong>6. Addebito:</strong> Crediti reali via RPC atomiche</p>
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <!-- Database Schema -->
                            <div class="card bg-base-100 shadow-xl">
                                <div class="card-body">
                                    <h2 class="card-title text-secondary">
                                        <i class="fas fa-database"></i>
                                        Schema Database
                                    </h2>
                                    
                                    <div class="overflow-x-auto">
                                        <table class="table table-zebra">
                                            <thead>
                                                <tr>
                                                    <th>Tabella</th>
                                                    <th>Descrizione</th>
                                                    <th>Campi Principali</th>
                                                </tr>
                                            </thead>
                                            <tbody>
                                                <tr>
                                                    <td><code>profiles</code></td>
                                                    <td>Utenti e saldo crediti</td>
                                                    <td>id, email, credits, openrouter_key_name</td>
                                                </tr>
                                                <tr>
                                                    <td><code>credit_transactions</code></td>
                                                    <td>Ledger transazioni crediti</td>
                                                    <td>user_id, amount, reason, created_at</td>
                                                </tr>
                                                <tr>
                                                    <td><code>flow_configs</code></td>
                                                    <td>Mapping flow multi-tenant</td>
                                                    <td>app_id, flow_key, flow_id, node_names</td>
                                                </tr>
                                                <tr>
                                                    <td><code>pricing_configs</code></td>
                                                    <td>Configurazioni pricing per-app</td>
                                                    <td>app_id, config (JSONB)</td>
                                                </tr>
                                                <tr>
                                                    <td><code>billing_configs</code></td>
                                                    <td>Configurazioni billing per-app</td>
                                                    <td>app_id, config (JSONB)</td>
                                                </tr>
                                                <tr>
                                                    <td><code>provider_credentials</code></td>
                                                    <td>Credenziali criptate provider</td>
                                                    <td>app_id, provider, credential_key, encrypted_value</td>
                                                </tr>
                                                <tr>
                                                    <td><code>billing_transactions</code></td>
                                                    <td>Audit transazioni pagamento</td>
                                                    <td>user_id, provider, amount_cents, status</td>
                                                </tr>
                                            </tbody>
                                        </table>
                                    </div>
                                </div>
                            </div>

                            <!-- Security Model -->
                            <div class="card bg-base-100 shadow-xl">
                                <div class="card-body">
                                    <h2 class="card-title text-error">
                                        <i class="fas fa-shield-alt"></i>
                                        Modello di Sicurezza
                                    </h2>
                                    
                                    <div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
                                        <div class="space-y-3">
                                            <h3 class="font-bold">Row Level Security (RLS)</h3>
                                            <ul class="list-disc list-inside space-y-1 text-sm">
                                                <li><strong>profiles:</strong> Utenti vedono solo i propri dati</li>
                                                <li><strong>credit_transactions:</strong> Ledger per-utente isolato</li>
                                                <li><strong>flow_configs:</strong> Solo service_role (deny_all)</li>
                                                <li><strong>pricing_configs:</strong> Solo service_role (deny_all)</li>
                                                <li><strong>provider_credentials:</strong> Solo service_role (deny_all)</li>
                                            </ul>
                                        </div>
                                        
                                        <div class="space-y-3">
                                            <h3 class="font-bold">Crittografia</h3>
                                            <ul class="list-disc list-inside space-y-1 text-sm">
                                                <li><strong>Credenziali provider:</strong> Fernet encryption</li>
                                                <li><strong>Chiavi OpenRouter:</strong> Mai esposte al client</li>
                                                <li><strong>Webhook signatures:</strong> HMAC verification</li>
                                                <li><strong>JWT tokens:</strong> Verificati via JWKS</li>
                                            </ul>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Examples Tab -->
                    <div id="tab-examples" class="tab-content">
                        <div class="space-y-6">
                            
                            <!-- Complete Integration Example -->
                            <div class="card bg-base-100 shadow-xl">
                                <div class="card-body">
                                    <h2 class="card-title text-primary">
                                        <i class="fas fa-code"></i>
                                        Esempio Integrazione Completa
                                    </h2>
                                    
                                    <div class="tabs tabs-bordered">
                                        <a class="tab tab-active" onclick="showExampleTab('react')">React/Next.js</a>
                                        <a class="tab" onclick="showExampleTab('python')">Python</a>
                                        <a class="tab" onclick="showExampleTab('curl')">cURL</a>
                                    </div>
                                    
                                    <div id="example-react" class="mt-4">
                                        <h3 class="font-bold mb-2">React Hook Super Semplice</h3>
                                        <pre class="bg-base-300 p-4 rounded text-sm overflow-x-auto">// hooks/useFlowStarter.js
import { useState } from 'react';

const API_URL = process.env.NEXT_PUBLIC_FLOW_STARTER_API + '/core/v1';

export function useFlowStarter(userToken) {
  const [loading, setLoading] = useState(false);

  const headers = {
    'Authorization': \`Bearer \${userToken}\`,
    'Content-Type': 'application/json'
  };

  const runAI = async (flowKey, inputData) => {
    setLoading(true);
    try {
      const response = await fetch(\`\${API_URL}/providers/flowise/execute\`, {
        method: 'POST',
        headers,
        body: JSON.stringify({
          flow_key: flowKey,
          data: inputData
        })
      });

      if (response.status === 402) {
        // Flow Starter ha controllato - crediti insufficienti
        const error = await response.json();
        throw new Error(\`Serve ricaricare: \${error.shortage} crediti mancanti\`);
      }

      const result = await response.json();
      return result.result; // Solo il contenuto AI
      
    } finally {
      setLoading(false);
    }
  };

  return { runAI, loading };
}

// Componente esempio
function ContentGenerator({ userToken }) {
  const { runAI, loading } = useFlowStarter(userToken);
  const [content, setContent] = useState('');

  const generateContent = async () => {
    try {
      const result = await runAI('content_generator', {
        prompt: 'Scrivi un post LinkedIn su AI'
      });
      setContent(result.text);
    } catch (error) {
      if (error.message.includes('crediti')) {
        // Redirect a pricing page
        window.location.href = '/pricing';
      } else {
        alert('Errore: ' + error.message);
      }
    }
  };

  return (
    &lt;div&gt;
      &lt;button onClick={generateContent} disabled={loading}&gt;
        {loading ? 'Generando...' : 'Genera Contenuto AI'}
      &lt;/button&gt;
      {content && &lt;div&gt;{content}&lt;/div&gt;}
    &lt;/div&gt;
  );
}</pre>
                                        
                                        <div class="alert alert-info mt-4">
                                            <i class="fas fa-magic"></i>
                                            <div>
                                                <h4 class="font-bold">La magia di Flow Starter</h4>
                                                <p class="text-sm">La tua app fa solo <code>runAI(flowKey, data)</code> e riceve il risultato. Flow Starter gestisce automaticamente: autenticazione, crediti, pricing, provider AI, retry, timeout, addebiti.</p>
                                            </div>
                                        </div>
                                    </div>
                                    
                                    <div id="example-python" class="mt-4 hidden">
                                        <h3 class="font-bold mb-2">Client Python Semplice</h3>
                                        <pre class="bg-base-300 p-4 rounded text-sm overflow-x-auto"># flow_starter_client.py
import httpx
import asyncio

class FlowStarterClient:
    def __init__(self, api_url: str, user_token: str):
        self.api_url = api_url.rstrip('/') + '/core/v1'
        self.headers = {
            'Authorization': f'Bearer {user_token}',
            'Content-Type': 'application/json'
        }
    
    async def get_credits(self) -> float:
        """Ottiene il saldo crediti dell'utente."""
        async with httpx.AsyncClient() as client:
            response = await client.get(f'{self.api_url}/credits/balance', headers=self.headers)
            response.raise_for_status()
            return response.json()['credits']
    
    async def run_ai_flow(self, flow_key: str, input_data: dict) -> dict:
        """Esegue un workflow AI. Flow Starter gestisce tutto automaticamente."""
        async with httpx.AsyncClient(timeout=300) as client:
            response = await client.post(
                f'{self.api_url}/providers/flowise/execute',
                headers=self.headers,
                json={'flow_key': flow_key, 'data': input_data}
            )
            
            if response.status_code == 402:
                # Crediti insufficienti - Flow Starter ha già controllato tutto
                error = response.json()
                raise ValueError(f"Crediti insufficienti: {error.get('shortage', 0)} mancanti")
            
            response.raise_for_status()
            return response.json()

# Esempio d'uso - È COSÌ SEMPLICE!
async def main():
    # Setup client
    client = FlowStarterClient(
        api_url='https://your-core.com',
        user_token='your-supabase-token'
    )
    
    # Controlla saldo (opzionale)
    credits = await client.get_credits()
    print(f'💰 Crediti disponibili: {credits}')
    
    # Esegui AI workflow - Flow Starter fa tutto il resto!
    try:
        result = await client.run_ai_flow(
            flow_key='content_generator',
            input_data={'prompt': 'Scrivi un post LinkedIn su AI marketing'}
        )
        
        # Usa il risultato nella tua app
        ai_content = result['result']['text']
        print(f'🤖 Contenuto generato: {ai_content}')
        
    except ValueError as e:
        # Gestisci solo crediti insufficienti
        print(f'❌ {e}')
        # Redirect utente a pagina pricing
    except Exception as e:
        # Altri errori
        print(f'❌ Errore: {e}')

if __name__ == '__main__':
    asyncio.run(main())</pre>
                                        
                                        <div class="alert alert-success mt-4">
                                            <i class="fas fa-lightbulb"></i>
                                            <div>
                                                <h4 class="font-bold">Perché è così semplice?</h4>
                                                <ul class="list-disc list-inside text-sm">
                                                    <li><strong>Flow Starter gestisce tutto:</strong> affordability, pricing, addebiti, retry</li>
                                                    <li><strong>L'app si concentra sul business:</strong> input → AI result → UI</li>
                                                    <li><strong>Errori gestiti automaticamente:</strong> solo 402 (crediti) da gestire</li>
                                                    <li><strong>Plug-and-play:</strong> 3 righe di codice per AI complessa</li>
                                                </ul>
                                            </div>
                                        </div>
                                    </div>
                                    
                                    <div id="example-curl" class="mt-4 hidden">
                                        <h3 class="font-bold mb-2">cURL Super Essenziali</h3>
                                        <pre class="bg-base-300 p-4 rounded text-sm overflow-x-auto"># Setup variabili
export API_URL="https://your-core.com/core/v1"
export USER_TOKEN="your-supabase-token"

# 🚀 LA CHIAMATA CHE CONTA - Esegui AI workflow

# Single-tenant (CORE_APP_ID nell'ambiente)
curl -X POST \\
  -H "Authorization: Bearer \$USER_TOKEN" \\
  -H "Content-Type: application/json" \\
  -d '{
    "flow_key": "content_generator",
    "data": {"prompt": "Scrivi post LinkedIn su AI"}
  }' \\
  \$API_URL/providers/flowise/execute

# Multi-tenant (aggiungi X-App-Id)
curl -X POST \\
  -H "Authorization: Bearer \$USER_TOKEN" \\
  -H "X-App-Id: my-app" \\
  -H "Content-Type: application/json" \\
  -d '{
    "flow_key": "content_generator", 
    "data": {"prompt": "Scrivi post LinkedIn su AI"}
  }' \\
  \$API_URL/providers/flowise/execute

# 💰 Controlla saldo crediti (opzionale)
curl -H "Authorization: Bearer \$USER_TOKEN" \\
     \$API_URL/credits/balance

# 🛒 Crea checkout per ricaricare crediti
curl -X POST \\
  -H "Authorization: Bearer \$USER_TOKEN" \\
  -H "Content-Type: application/json" \\
  -d '{"credits": 5000, "amount_usd": 19.0}' \\
  \$API_URL/billing/checkout

# ⚡ Test rapido con utente automatico
curl -X POST \$API_URL/examples/e2e-run
# → Risposta contiene access_token pronto per i test</pre>
                                        
                                        <div class="alert alert-success mt-4">
                                            <i class="fas fa-rocket"></i>
                                            <div>
                                                <h4 class="font-bold">Basta una chiamata!</h4>
                                                <p class="text-sm">Con Flow Starter, la tua app fa una sola chiamata per eseguire AI complessi. Tutto il resto (pricing, crediti, provider, app identification) è gestito automaticamente.</p>
                                            </div>
                                        </div>
                                        
                                        <div class="alert alert-info mt-4">
                                            <i class="fas fa-cog"></i>
                                            <div>
                                                <h4 class="font-bold">Due Modi di Usare Flow Starter</h4>
                                                <div class="grid grid-cols-1 md:grid-cols-2 gap-3 mt-2">
                                                    <div class="bg-success/10 p-2 rounded">
                                                        <h5 class="font-bold text-xs text-success">✅ SINGLE-TENANT (Consigliato)</h5>
                                                        <p class="text-xs">Un'istanza Flow Starter per la tua app</p>
                                                        <code class="text-xs">CORE_APP_ID=my-app</code>
                                                        <p class="text-xs mt-1">→ No X-App-Id necessario</p>
                                                    </div>
                                                    <div class="bg-warning/10 p-2 rounded">
                                                        <h5 class="font-bold text-xs text-warning">⚠️ MULTI-TENANT (Avanzato)</h5>
                                                        <p class="text-xs">Un Flow Starter per più app</p>
                                                        <code class="text-xs">X-App-Id: my-app</code>
                                                        <p class="text-xs mt-1">→ Header richiesto</p>
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                        
                                        <div class="collapse collapse-arrow bg-base-200 mt-4">
                                            <input type="checkbox" />
                                            <div class="collapse-title font-medium text-sm">
                                                <i class="fas fa-tools"></i>
                                                Comandi Admin (Setup/Config)
                                            </div>
                                            <div class="collapse-content">
                                                <pre class="bg-base-300 p-3 rounded text-xs">export ADMIN_KEY="your-admin-key"

# Configura flow mapping (una volta)
curl -X POST -H "X-Admin-Key: \$ADMIN_KEY" \\
     -H "Content-Type: application/json" \\
     -d '{
       "app_id": "my-app",
       "flow_key": "content_generator",
       "flow_id": "your-flowise-flow-id",
       "node_names": ["chatOpenRouter_0"]
     }' \\
     \$API_URL/admin/flow-configs

# Crea utente test
curl -X POST -H "X-Admin-Key: \$ADMIN_KEY" \\
     -H "Content-Type: application/json" \\
     -d '{"email": "test@example.com"}' \\
     \$API_URL/admin/users</pre>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <!-- Error Handling -->
                            <div class="card bg-base-100 shadow-xl">
                                <div class="card-body">
                                    <h2 class="card-title text-error">
                                        <i class="fas fa-exclamation-triangle"></i>
                                        Gestione Errori
                                    </h2>
                                    
                                    <div class="overflow-x-auto">
                                        <table class="table table-zebra">
                                            <thead>
                                                <tr>
                                                    <th>Status Code</th>
                                                    <th>Scenario</th>
                                                    <th>Risposta</th>
                                                    <th>Azione Consigliata</th>
                                                </tr>
                                            </thead>
                                            <tbody>
                                                <tr>
                                                    <td><span class="badge badge-error">401</span></td>
                                                    <td>Token mancante/invalido</td>
                                                    <td><code>{"detail": "Token mancante"}</code></td>
                                                    <td>Rigenera token o verifica autenticazione</td>
                                                </tr>
                                                <tr>
                                                    <td><span class="badge badge-warning">402</span></td>
                                                    <td>Crediti insufficienti</td>
                                                    <td><code>{"error_type": "insufficient_credits", "shortage": 0.5}</code></td>
                                                    <td>Redirect a pagina acquisto crediti</td>
                                                </tr>
                                                <tr>
                                                    <td><span class="badge badge-error">404</span></td>
                                                    <td>Flow config non trovata</td>
                                                    <td><code>{"detail": "flow_config non trovata"}</code></td>
                                                    <td>Configura flow in Admin → Flow Mappings</td>
                                                </tr>
                                                <tr>
                                                    <td><span class="badge badge-error">500</span></td>
                                                    <td>Errore provider AI</td>
                                                    <td><code>{"detail": "Errore durante l'esecuzione del flow"}</code></td>
                                                    <td>Verifica configurazione provider e log</td>
                                                </tr>
                                                <tr>
                                                    <td><span class="badge badge-error">502</span></td>
                                                    <td>Timeout/errore OpenRouter</td>
                                                    <td><code>{"detail": "Impossibile determinare il costo reale"}</code></td>
                                                    <td>Retry con backoff, verifica status OpenRouter</td>
                                                </tr>
                                            </tbody>
                                        </table>
                                    </div>
                                </div>
                            </div>

                            <!-- Testing Examples -->
                            <div class="card bg-base-100 shadow-xl">
                                <div class="card-body">
                                    <h2 class="card-title text-success">
                                        <i class="fas fa-flask"></i>
                                        Esempi di Test
                                    </h2>
                                    
                                    <div class="space-y-4">
                                        <div class="collapse collapse-arrow bg-base-200">
                                            <input type="checkbox" />
                                            <div class="collapse-title font-medium">
                                                Test E2E Completo
                                            </div>
                                            <div class="collapse-content">
                                                <pre class="bg-base-300 p-3 rounded text-sm"># 1. Crea utente test automatico
curl -X POST \$API_URL/examples/e2e-run

# Risposta contiene access_token per i test successivi
# 2. Usa il token per testare i flow
export TEST_TOKEN="token_dalla_risposta_precedente"

# 3. Test flow execution
curl -X POST -H "Authorization: Bearer \$TEST_TOKEN" \\
     -H "X-App-Id: default" \\
     -H "Content-Type: application/json" \\
     -d '{
       "flow_key": "demo_generate_intro",
       "data": {"prompt": "Test prompt"}
     }' \\
     \$API_URL/providers/flowise/execute</pre>
                                            </div>
                                        </div>
                                        
                                        <div class="collapse collapse-arrow bg-base-200">
                                            <input type="checkbox" />
                                            <div class="collapse-title font-medium">
                                                Test Webhook Locale
                                            </div>
                                            <div class="collapse-content">
                                                <pre class="bg-base-300 p-3 rounded text-sm"># Setup ngrok per webhook locali
ngrok http 5050

# Configura URL webhook in LemonSqueezy:
# https://abc123.ngrok.io/core/v1/billing/webhook

# Test simulazione webhook (ambiente dev)
curl -X POST -H "X-Admin-Key: \$ADMIN_KEY" \\
     -H "Content-Type: application/json" \\
     -d '{
       "user_id": "user-uuid",
       "credits": 5000,
       "amount_usd": 19.0,
       "event_name": "order_created"
     }' \\
     \$API_URL/admin/billing/simulate-webhook</pre>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                

            `
        };

        // Users Management
        window.pageTemplates['users'] = () => {
            return `
                <div class="mb-6">
                    <div class="flex justify-between items-center">
                        <div>
                            <h1 class="text-3xl font-bold">Gestione Utenti</h1>
                            <p class="text-base-content/60">Visualizza, modifica ed elimina utenti</p>
                        </div>
                        <button class="btn btn-primary" onclick="UsersComponent.showCreateUserForm()">
                            <i class="fas fa-user-plus"></i>
                            Nuovo Utente
                        </button>
                    </div>
                </div>

                <!-- Search & Filters -->
                <div class="card bg-base-100 shadow-xl mb-6">
                    <div class="card-body">
                        <div class="form-control">
                            <div class="input-group">
                                <input type="text" 
                                       placeholder="Cerca per email..." 
                                       class="input input-bordered w-full" 
                                       id="users-search-input"
                                       onkeyup="if(event.key === 'Enter') UsersComponent.loadUsers(this.value)" />
                                <button class="btn btn-square btn-primary" onclick="UsersComponent.loadUsers(document.getElementById('users-search-input').value)">
                                    <i class="fas fa-search"></i>
                                </button>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Users List -->
                <div class="card bg-base-100 shadow-xl">
                    <div class="card-body">
                        <h2 class="card-title mb-4">
                            <i class="fas fa-users"></i>
                            Lista Utenti
                        </h2>
                        <div id="users-list-container">
                            <div class="flex items-center justify-center py-8">
                                <span class="loading loading-spinner loading-lg"></span>
                            </div>
                        </div>
                    </div>
                </div>
            `;
        };