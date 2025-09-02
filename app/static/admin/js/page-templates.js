window.pageTemplates = {
            overview: () => `
                <div class="mb-6">
                    <h1 class="text-3xl font-bold">Dashboard Overview</h1>
                    <p class="text-base-content/60">System status and key metrics</p>
                </div>
                
                                    <!-- Quick Setup -->
                    <div class="alert alert-warning mb-6" id="setup-alert" style="display: none;">
                        <i class="fas fa-exclamation-triangle"></i>
                        <div>
                            <h3 class="font-bold">Setup Required</h3>
                            <p>Configure your Supabase credentials and admin key to load data</p>
                            <p class="text-sm mt-1">You need to run the setup wizard or configure credentials below</p>
                        </div>
                        <div class="flex gap-2">
                            <button class="btn btn-sm btn-primary" onclick="showQuickSetup()">Quick Setup</button>
                            <a href="/core/v1/setup/wizard" class="btn btn-sm btn-secondary" target="_blank">Setup Wizard</a>
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
                                <button class="btn btn-sm btn-primary" onclick="addFixedCostRow()">
                                    <i class="fas fa-plus"></i> Add Fixed Cost
                                </button>
                                <button class="btn btn-sm btn-success" onclick="saveFixedCosts()">
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
                    <p class="text-base-content/60">Configure flow ID mappings and node names</p>
                </div>
                
                <!-- Tabs for future expansion -->
                <div class="tabs tabs-boxed mb-6">
                    <a href="#" class="tab tab-active" data-tab="mappings">Current Mappings</a>
                    <a href="#" class="tab" data-tab="import">Import/Export</a>
                    <a href="#" class="tab" data-tab="validation">Validation</a>
                </div>
                
                <div id="tab-mappings" class="tab-content active">
                    <div class="card bg-base-100 shadow-xl">
                        <div class="card-body">
                            <h2 class="card-title">Flow Configuration</h2>
                            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                                <div class="form-control">
                                    <label class="label">App ID</label>
                                    <input type="text" class="input input-bordered" id="flow_app_id" value="default" />
                                </div>
                                <div class="form-control">
                                    <label class="label">Flow Key</label>
                                    <input type="text" class="input input-bordered" id="flow_key" placeholder="e.g., news_writer" />
                                </div>
                                <div class="form-control">
                                    <label class="label">Flow ID</label>
                                    <input type="text" class="input input-bordered" id="flow_id" placeholder="94b0..." />
                                </div>
                                <div class="form-control">
                                    <label class="label">Node Names (comma-separated)</label>
                                    <input type="text" class="input input-bordered" id="node_names" placeholder="node1,node2" />
                                </div>
                            </div>
                            <div class="card-actions justify-end mt-4">
                                <button class="btn btn-primary" onclick="upsertFlowConfig()">Save Flow Config</button>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div id="tab-import" class="tab-content">
                    <div class="card bg-base-100 shadow-xl">
                        <div class="card-body">
                            <p class="text-center text-base-content/60">Import/Export functionality coming soon...</p>
                        </div>
                    </div>
                </div>
                
                <div id="tab-validation" class="tab-content">
                    <div class="card bg-base-100 shadow-xl">
                        <div class="card-body">
                            <p class="text-center text-base-content/60">Flow validation coming soon...</p>
                        </div>
                    </div>
                </div>
            `,
            
            // Configuration - Security
            'config-security': () => `
                <div class="mb-6">
                    <h1 class="text-3xl font-bold">Security Settings</h1>
                    <p class="text-base-content/60">Manage credentials and security settings</p>
                </div>
                
                <!-- Tabs for future expansion -->
                <div class="tabs tabs-boxed mb-6">
                    <a href="#" class="tab tab-active" data-tab="credentials">Credentials</a>
                    <a href="#" class="tab" data-tab="access">Access Control</a>
                    <a href="#" class="tab" data-tab="audit">Audit Log</a>
                </div>
                
                <div id="tab-credentials" class="tab-content active">
                    <div class="card bg-base-100 shadow-xl">
                        <div class="card-body">
                            <h2 class="card-title">Credential Management</h2>
                            <div class="alert alert-warning mb-4">
                                <i class="fas fa-exclamation-triangle"></i>
                                <span>Handle credentials with care. They are encrypted before storage.</span>
                            </div>
                            <div class="flex gap-2">
                                <button class="btn btn-secondary" onclick="rotateCredential('api_key')">
                                    <i class="fas fa-key"></i> Rotate API Key
                                </button>
                                <button class="btn btn-secondary" onclick="rotateCredential('webhook_secret')">
                                    <i class="fas fa-lock"></i> Rotate Webhook Secret
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div id="tab-access" class="tab-content">
                    <div class="card bg-base-100 shadow-xl">
                        <div class="card-body">
                            <p class="text-center text-base-content/60">Access control settings coming soon...</p>
                        </div>
                    </div>
                </div>
                
                <div id="tab-audit" class="tab-content">
                    <div class="card bg-base-100 shadow-xl">
                        <div class="card-body">
                            <p class="text-center text-base-content/60">Security audit log coming soon...</p>
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
                            
                            <!-- Timeline -->
                            <div class="divider"></div>
                            <div>
                                <h3 class="font-semibold mb-3">Test Timeline</h3>
                                <div id="test-timeline" class="space-y-2">
                                    <p class="text-sm text-base-content/60">No tests executed yet</p>
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
                </div>
            `
        };