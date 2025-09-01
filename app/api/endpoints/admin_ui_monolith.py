"""
Admin UI endpoint con la dashboard unificata completa.
HTML incorporato direttamente dal markdown funzionante.
"""

from __future__ import annotations

from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter()


@router.get("/dashboard", response_class=HTMLResponse, include_in_schema=False)
async def dashboard() -> str:
    """Dashboard unificata con tutte le funzionalità inclusa loadAppAffordability."""
    return """
<!doctype html>
<html data-theme="corporate">
<head>
    <meta charset="utf-8"/>
    <meta name="viewport" content="width=device-width,initial-scale=1"/>
    <title>Flow Starter - Dashboard</title>
    <link href="https://cdn.jsdelivr.net/npm/daisyui@4.12.23/dist/full.min.css" rel="stylesheet" type="text/css" />
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
    <style>
        .sidebar-link { transition: all 0.2s; }
        .sidebar-link:hover { background: rgba(59, 130, 246, 0.1); }
        .sidebar-link.active { background: rgba(59, 130, 246, 0.15); border-left: 3px solid #3b82f6; }
        .content-area { min-height: calc(100vh - 4rem); }
        .tab-content { display: none; }
        .tab-content.active { display: block; }
        .metric-card { transition: transform 0.2s; }
        .metric-card:hover { transform: translateY(-2px); }
        .loading { opacity: 0.6; pointer-events: none; }
        pre.json { max-height: 500px; overflow: auto; }
        .accordion-content { max-height: 0; overflow: hidden; transition: max-height 0.3s ease-out; }
        .accordion-content.active { max-height: 500px; }
    </style>
</head>
<body>
    <div class="drawer lg:drawer-open">
        <input id="drawer-toggle" type="checkbox" class="drawer-toggle" />
        
        <!-- Main Content -->
        <div class="drawer-content flex flex-col">
            <!-- Navbar -->
            <div class="navbar bg-base-100 shadow-md lg:hidden">
                <div class="flex-none">
                    <label for="drawer-toggle" class="btn btn-square btn-ghost">
                        <i class="fas fa-bars text-xl"></i>
                    </label>
                </div>
                <div class="flex-1">
                    <span class="text-xl font-bold">Flow Starter</span>
                </div>
            </div>
            
            <!-- Content Area -->
            <div class="content-area bg-base-200 p-4 lg:p-6">
                <div id="main-content" class="max-w-7xl mx-auto">
                    <!-- Il contenuto verrà caricato dinamicamente -->
                    <div class="flex items-center justify-center h-96">
                        <span class="loading loading-spinner loading-lg"></span>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Sidebar -->
        <div class="drawer-side">
            <label for="drawer-toggle" class="drawer-overlay"></label>
            <aside class="w-64 min-h-full bg-base-100 text-base-content">
                <!-- Logo -->
                <div class="p-4 border-b">
                    <h2 class="text-2xl font-bold text-primary">Flow Starter</h2>
                    <p class="text-sm text-base-content/60">Admin Dashboard</p>
                </div>
                
                <!-- Navigation -->
                <ul class="menu p-2">
                    <!-- Overview -->
                    <li>
                        <a href="#" class="sidebar-link" data-page="overview">
                            <i class="fas fa-home w-5"></i>
                            <span>Overview</span>
                        </a>
                    </li>
                    
                    <!-- Business & Pricing -->
                    <li>
                        <details id="business-accordion">
                            <summary class="sidebar-link">
                                <i class="fas fa-chart-line w-5"></i>
                                <span>Business & Pricing</span>
                            </summary>
                            <ul class="ml-4">
                                <li><a href="#" data-page="business-config">Revenue Configuration</a></li>
                                <li><a href="#" data-page="business-costs">App Affordability</a></li>
                                <li><a href="#" data-page="business-simulator">Pricing Simulator</a></li>
                                <li><a href="#" data-page="business-scenarios">Scenarios</a></li>
                            </ul>
                        </details>
                    </li>
                    
                    <!-- Billing & Plans -->
                    <li>
                        <details id="billing-accordion">
                            <summary class="sidebar-link">
                                <i class="fas fa-credit-card w-5"></i>
                                <span>Billing & Plans</span>
                            </summary>
                            <ul class="ml-4">
                                <li><a href="#" data-page="billing-plans">Subscription Plans</a></li>
                                <li><a href="#" data-page="billing-credits">Credits & Rollout</a></li>
                                <li><a href="#" data-page="billing-checkout">Checkout</a></li>
                            </ul>
                        </details>
                    </li>
                    
                    <!-- Observability -->
                    <li>
                        <details id="observability-accordion">
                            <summary class="sidebar-link">
                                <i class="fas fa-chart-bar w-5"></i>
                                <span>Observability</span>
                            </summary>
                            <ul class="ml-4">
                                <li><a href="#" data-page="observe-ai">AI Usage</a></li>
                                <li><a href="#" data-page="observe-credits">Credits Ledger</a></li>
                                <li><a href="#" data-page="observe-rollouts">Rollout Manager</a></li>
                            </ul>
                        </details>
                    </li>
                    
                    <!-- Configuration -->
                    <li>
                        <details id="config-accordion">
                            <summary class="sidebar-link">
                                <i class="fas fa-cog w-5"></i>
                                <span>Configuration</span>
                            </summary>
                            <ul class="ml-4">
                                <li><a href="#" data-page="config-flows">Flow Mappings</a></li>
                                <li><a href="#" data-page="billing-provider">Payment Provider</a></li>
                                <li><a href="#" data-page="config-security">Security</a></li>
                                <li><a href="#" data-page="config-setup">Initial Setup</a></li>
                            </ul>
                        </details>
                    </li>
                    
                    <!-- Testing -->
                    <li>
                        <a href="#" class="sidebar-link" data-page="testing">
                            <i class="fas fa-flask w-5"></i>
                            <span>Testing</span>
                        </a>
                    </li>
                </ul>
                
                <!-- Bottom Actions -->
                <div class="p-4 mt-auto border-t">
                    <button class="btn btn-sm btn-ghost w-full" onclick="clearAllData()">
                        <i class="fas fa-trash"></i>
                        Clear Local Data
                    </button>
                </div>
            </aside>
        </div>
    </div>

    <!-- Toast Container -->
    <div class="toast toast-end toast-bottom" id="toast-container"></div>

    <script>
        // ========== State Management ==========
        const state = {
            currentPage: 'overview',
            currentTab: null,
            token: localStorage.getItem('flowstarter_bearer_token') || '',
            adminKey: localStorage.getItem('flowstarter_admin_key') || 'n3v5Gbuae27hQMR5icWXGum94QjkvMBbFQPdwTYc4hM', // Auto-load from .env
            baseUrl: localStorage.getItem('flowstarter_base_url') || window.location.origin,
            appId: localStorage.getItem('flowstarter_app_id') || 'default',
            cache: {},
            autoRefresh: null
        };

        // ========== Utility Functions ==========
        function showToast(message, type = 'info') {
            const toast = document.createElement('div');
            toast.className = `alert alert-${type}`;
            toast.innerHTML = `<span>${message}</span>`;
            document.getElementById('toast-container').appendChild(toast);
            setTimeout(() => toast.remove(), 3000);
        }

        function showLoading(show = true) {
            const content = document.getElementById('main-content');
            if (show) {
                content.classList.add('loading');
                content.innerHTML = '<div class="flex items-center justify-center h-96"><span class="loading loading-spinner loading-lg"></span></div>';
            } else {
                content.classList.remove('loading');
            }
        }

        async function apiCall(url, options = {}) {
            const headers = { 'Content-Type': 'application/json' };
            if (state.token) headers['Authorization'] = `Bearer ${state.token}`;
            if (state.adminKey) headers['X-Admin-Key'] = state.adminKey;
            
            try {
                const response = await fetch(`${state.baseUrl}${url}`, { ...options, headers: { ...headers, ...options.headers } });
                if (!response.ok) {
                    const errorText = await response.text();
                    let errorDetail = `HTTP ${response.status}`;
                    try {
                        const errorJson = JSON.parse(errorText);
                        errorDetail = errorJson.detail || errorJson.message || errorDetail;
                    } catch (e) {
                        if (errorText) errorDetail += `: ${errorText}`;
                    }
                    throw new Error(errorDetail);
                }
                return await response.json();
            } catch (error) {
                showToast(`API Error: ${error.message}`, 'error');
                throw error;
            }
        }

        function saveState() {
            localStorage.setItem('flowstarter_bearer_token', state.token);
            localStorage.setItem('flowstarter_admin_key', state.adminKey);
            localStorage.setItem('flowstarter_base_url', state.baseUrl);
            localStorage.setItem('flowstarter_app_id', state.appId);
        }

        function clearAllData() {
            if (confirm('Clear all local data and reload?')) {
                localStorage.clear();
                location.reload();
            }
        }

        // ========== Page Templates ==========
        const pageTemplates = {
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
                            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
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
                            </div>
                            <div class="card-actions justify-end mt-4">
                                <button class="btn btn-primary" onclick="savePricingConfig()">Save Configuration</button>
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
                                <button class="btn btn-sm btn-primary" onclick="loadAppAffordability()">
                                    <i class="fas fa-refresh"></i> Refresh Apps
                                </button>
                                <button class="btn btn-sm btn-success" onclick="saveAppAffordability()">
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
                                <button class="btn btn-secondary" onclick="testProviderConnection()">Test Connection</button>
                                <button class="btn btn-primary" onclick="saveBillingProviderConfig()">Save Configuration</button>
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
                    <div class="card bg-base-100 shadow-xl">
                        <div class="card-body">
                            <h2 class="card-title">Active Plans</h2>
                            <table class="table w-full">
                                <thead>
                                    <tr>
                                        <th>Plan ID</th>
                                        <th>Name</th>
                                        <th>Type</th>
                                        <th>Price</th>
                                        <th>Credits</th>
                                        <th>Discount %</th>
                                        <th>Actions</th>
                                    </tr>
                                </thead>
                                <tbody id="plans-table">
                                    <!-- Dynamic content -->
                                </tbody>
                            </table>
                            <button class="btn btn-sm btn-primary mt-4" onclick="addPlanRow()">
                                <i class="fas fa-plus"></i> Add Plan
                            </button>
                        </div>
                    </div>
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
            
            // Billing & Plans - Credits & Rollout
            'billing-credits': () => `
                <div class="mb-6">
                    <h1 class="text-3xl font-bold">Credits & Rollout</h1>
                    <p class="text-base-content/60">Configure credit allocation and rollout settings</p>
                </div>
                
                <!-- Tabs for future expansion -->
                <div class="tabs tabs-boxed mb-6">
                    <a href="#" class="tab tab-active" data-tab="rollout">Rollout Settings</a>
                    <a href="#" class="tab" data-tab="policies">Policies</a>
                    <a href="#" class="tab" data-tab="schedule">Schedule</a>
                </div>
                
                <div id="tab-rollout" class="tab-content active">
                    <div class="card bg-base-100 shadow-xl">
                        <div class="card-body">
                            <h2 class="card-title">Credit Configuration</h2>
                            
                            <!-- Signup Credits -->
                            <div class="mb-6">
                                <h3 class="text-lg font-semibold mb-3">New User Signup</h3>
                                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                                    <div class="form-control">
                                        <label class="label">
                                            <span>Initial Credits at Signup</span>
                                            <span class="label-text-alt">Free credits for new users</span>
                                        </label>
                                        <input type="number" class="input input-bordered" id="signup_initial_credits" placeholder="100" />
                                    </div>
                                    <div class="form-control">
                                        <label class="label">
                                            <span>Signup Credits Cost (USD)</span>
                                            <span class="label-text-alt">P&L cost for free credits</span>
                                        </label>
                                        <input type="number" class="input input-bordered" id="signup_credits_cost" step="0.01" placeholder="0.00" />
                                    </div>
                                </div>
                            </div>
                            
                            <div class="divider">Periodic Rollout</div>
                            
                            <!-- Rollout Settings -->
                            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                                <div class="form-control">
                                    <label class="label">Rollout Interval</label>
                                    <select class="select select-bordered" id="rollout_interval">
                                        <option value="monthly">Monthly</option>
                                        <option value="weekly">Weekly</option>
                                        <option value="custom">Custom</option>
                                    </select>
                                </div>
                                <div class="form-control">
                                    <label class="label">Credits per Period</label>
                                    <input type="number" class="input input-bordered" id="rollout_credits" />
                                </div>
                                <div class="form-control">
                                    <label class="label">Max Rollover</label>
                                    <input type="number" class="input input-bordered" id="rollout_max" />
                                </div>
                                <div class="form-control">
                                    <label class="label">Rollout Percentage</label>
                                    <input type="number" class="input input-bordered" id="rollout_percentage" value="100" />
                                </div>
                            </div>
                            <div class="card-actions justify-end mt-4">
                                <button class="btn btn-primary" onclick="saveCreditsAndRolloutConfig()">Save Configuration</button>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div id="tab-policies" class="tab-content">
                    <div class="card bg-base-100 shadow-xl">
                        <div class="card-body">
                            <p class="text-center text-base-content/60">Credit policies coming soon...</p>
                        </div>
                    </div>
                </div>
                
                <div id="tab-schedule" class="tab-content">
                    <div class="card bg-base-100 shadow-xl">
                        <div class="card-body">
                            <p class="text-center text-base-content/60">Rollout scheduler coming soon...</p>
                        </div>
                    </div>
                </div>
            `,
            
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
                            <button class="btn btn-primary mt-4" onclick="generateCheckout()">
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
                    <h1 class="text-3xl font-bold">Testing</h1>
                    <p class="text-base-content/60">Test flows and API endpoints</p>
                </div>
                
                <div class="card bg-base-100 shadow-xl">
                    <div class="card-body">
                        <h2 class="card-title">Flow Executor</h2>
                        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div class="form-control">
                                <label class="label">Flow Key</label>
                                <input type="text" class="input input-bordered" id="test_flow_key" placeholder="e.g., news_writer" />
                            </div>
                            <div class="form-control">
                                <label class="label">App ID</label>
                                <input type="text" class="input input-bordered" id="test_app_id" value="default" />
                            </div>
                        </div>
                        <div class="form-control mt-4">
                            <label class="label">Input Data (JSON)</label>
                            <textarea class="textarea textarea-bordered h-32" id="test_input" placeholder='{"prompt": "Test prompt"}'></textarea>
                        </div>
                        <div class="form-control mt-4">
                            <label class="label">
                                <span>Enable Streaming</span>
                                <input type="checkbox" class="checkbox" id="test_streaming" />
                            </label>
                        </div>
                        <button class="btn btn-primary mt-4" onclick="executeFlow()">
                            <i class="fas fa-play"></i> Execute Flow
                        </button>
                        <div id="test-output" class="mt-4">
                            <!-- Test results -->
                        </div>
                    </div>
                </div>
            `
        };

        // ========== Quick Setup Modal ==========
        function showQuickSetup() {
            const modal = document.createElement('div');
            modal.className = 'modal modal-open';
            modal.innerHTML = `
                <div class="modal-box max-w-2xl">
                    <h3 class="font-bold text-lg">Quick Setup</h3>
                    <div class="py-4">
                        <div class="alert alert-info mb-4">
                            <i class="fas fa-info-circle"></i>
                            <div>
                                <p class="font-semibold">Need credentials?</p>
                                <p class="text-sm">1. Run the setup wizard to configure Supabase first</p>
                                <p class="text-sm">2. Get your admin key from the .env file</p>
                                <p class="text-sm">3. Or use a user bearer token from Supabase Auth</p>
                            </div>
                        </div>
                        
                        <div class="form-control">
                            <label class="label">
                                <span>Bearer Token</span>
                                <span class="label-text-alt">User authentication token</span>
                            </label>
                            <input type="text" class="input input-bordered" id="quick-token" value="${state.token}" placeholder="eyJhbGciOi..." />
                        </div>
                        
                        <div class="form-control mt-2">
                            <label class="label">
                                <span>Admin Key</span>
                                <span class="label-text-alt">From CORE_ADMIN_KEY in .env</span>
                            </label>
                            <input type="text" class="input input-bordered" id="quick-admin" value="${state.adminKey}" placeholder="your-secret-admin-key" />
                        </div>
                        
                        <div class="form-control mt-2">
                            <label class="label">
                                <span>Base URL</span>
                                <span class="label-text-alt">Core API endpoint</span>
                            </label>
                            <input type="text" class="input input-bordered" id="quick-base" value="${state.baseUrl}" />
                        </div>
                        
                        <div class="form-control mt-2">
                            <label class="label">
                                <span>App ID</span>
                                <span class="label-text-alt">Default is fine for single project</span>
                            </label>
                            <input type="text" class="input input-bordered" id="quick-app" value="${state.appId}" />
                        </div>
                        
                        <div class="divider">OR</div>
                        
                        <div class="text-center">
                            <p class="mb-2">First time? Configure Supabase connection first:</p>
                            <a href="/core/v1/setup/wizard" class="btn btn-secondary" target="_blank">
                                <i class="fas fa-magic"></i> Open Setup Wizard
                            </a>
                        </div>
                    </div>
                    <div class="modal-action">
                        <button class="btn" onclick="this.closest('.modal').remove()">Cancel</button>
                        <button class="btn btn-primary" onclick="saveQuickSetup()">Save Credentials</button>
                    </div>
                </div>
            `;
            document.body.appendChild(modal);
        }

        function saveQuickSetup() {
            state.token = document.getElementById('quick-token').value.trim();
            state.adminKey = document.getElementById('quick-admin').value.trim();
            state.baseUrl = document.getElementById('quick-base').value.trim() || window.location.origin;
            state.appId = document.getElementById('quick-app').value.trim() || 'default';
            saveState();
            document.querySelector('.modal').remove();
            showToast('Configuration saved', 'success');
            
            // Hide setup alert if credentials are configured
            if (state.token || state.adminKey) {
                document.getElementById('setup-alert')?.remove();
            }
            
            // Reload current page
            loadPage(state.currentPage, state.currentTab);
        }

        // ========== Navigation ==========
        function navigate(page, tab = null) {
            state.currentPage = page;
            state.currentTab = tab;
            
            // Update active states
            document.querySelectorAll('.sidebar-link').forEach(link => {
                link.classList.remove('active');
                if (link.dataset.page === page) {
                    link.classList.add('active');
                    // Open parent accordion if in submenu
                    const details = link.closest('details');
                    if (details) details.open = true;
                }
            });
            
            loadPage(page, tab);
        }

        function loadPage(page, tab = null) {
            showLoading();
            
            setTimeout(() => {
                const template = pageTemplates[page];
                if (template) {
                    document.getElementById('main-content').innerHTML = template();
                    
                    // Auto-switch to tab if specified
                    if (tab) {
                        setTimeout(() => switchTab(tab), 100);
                    } else {
                        // Activate first tab by default
                        const firstTab = document.querySelector('.tab[data-tab]');
                        if (firstTab) {
                            switchTab(firstTab.dataset.tab);
                        }
                    }
                    
                    // Load page-specific data
                    loadPageData(page);
                }
                showLoading(false);
            }, 300);
        }

        function switchTab(tabName) {
            // Update tab states
            document.querySelectorAll('.tab').forEach(tab => {
                tab.classList.remove('tab-active');
                if (tab.dataset.tab === tabName) {
                    tab.classList.add('tab-active');
                }
            });
            
            // Show/hide tab contents
            document.querySelectorAll('.tab-content').forEach(content => {
                content.classList.remove('active');
            });
            const activeContent = document.getElementById(`tab-${tabName}`);
            if (activeContent) {
                activeContent.classList.add('active');
            }
            
            state.currentTab = tabName;
        }
        
        // Setup tab click handlers
        function setupTabHandlers() {
            document.addEventListener('click', (e) => {
                // Check if clicked element or its parent is a tab
                const tab = e.target.closest('.tab[data-tab]');
                if (tab) {
                    e.preventDefault();
                    switchTab(tab.dataset.tab);
                }
            });
        }

        // ========== Data Loading ==========
        async function loadPageData(page) {
            switch (page) {
                case 'overview':
                    await loadOverviewMetrics();
                    break;
                // Business & Pricing pages
                case 'business-config':
                    await loadPricingConfig();
                    break;
                case 'business-costs':
                    await loadAppAffordability(); // Load app affordability settings
                    break;
                case 'business-simulator':
                    await loadPricingConfig(); // Load config to run simulation
                    break;
                case 'business-scenarios':
                    // Scenarios are loaded from localStorage
                    break;
                // Billing & Plans pages
                case 'billing-provider':
                    await loadBillingConfig();
                    break;
                case 'billing-plans':
                    await loadPlansData();
                    break;
                case 'billing-credits':
                    await loadCreditsConfig();
                    break;
                case 'billing-checkout':
                    await loadCheckoutData();
                    break;
                // Observability pages
                case 'observe-ai':
                    // Data loaded on demand via buttons
                    break;
                case 'observe-credits':
                    // Data loaded on demand via buttons
                    break;
                case 'observe-rollouts':
                    // Data loaded on demand via buttons
                    break;
                // Configuration pages
                case 'config-flows':
                    // Data loaded on form submission
                    break;
                case 'config-security':
                    // No initial data needed
                    break;
                case 'config-setup':
                    // Static content, no data needed
                    break;
                // Testing
                case 'testing':
                    // Data loaded on demand
                    break;
            }
        }

        async function loadOverviewMetrics() {
            try {
                // Check if credentials are configured
                if (!state.token && !state.adminKey) {
                    document.getElementById('metric-users').textContent = '-';
                    document.getElementById('metric-credits').textContent = '-';
                    document.getElementById('metric-revenue').textContent = '-';
                    // Show setup alert
                    const setupAlert = document.getElementById('setup-alert');
                    if (setupAlert) setupAlert.style.display = 'block';
                    return;
                }
                
                // Load user count
                try {
                    const users = await apiCall('/core/v1/admin/users?limit=1');
                    // API returns {count, users} not {total}
                    const totalUsers = users.count || users.total || 0;
                    document.getElementById('metric-users').textContent = totalUsers.toString();
                    
                    // If we need total count and current response has limit, get full count
                    if (totalUsers === 1 && users.users && users.users.length === 1) {
                        const fullCount = await apiCall('/core/v1/admin/users?limit=1000');
                        document.getElementById('metric-users').textContent = (fullCount.count || 0).toString();
                    }
                } catch (e) {
                    document.getElementById('metric-users').textContent = 'N/A';
                    console.error('Failed to load users:', e);
                }
                
                // Load pricing config for revenue target
                try {
                    const pricing = await apiCall('/core/v1/admin/pricing/config');
                    const revenue = pricing.monthly_revenue_target_usd || 0;
                    document.getElementById('metric-revenue').textContent = `$${revenue.toLocaleString()}`;
                } catch (e) {
                    // If no config exists, show default value
                    if (e.message && e.message.includes('422')) {
                        document.getElementById('metric-revenue').textContent = '$0';
                        console.log('No pricing config found, using defaults');
                    } else {
                        document.getElementById('metric-revenue').textContent = 'N/A';
                        console.error('Failed to load pricing:', e);
                    }
                }
                
                // Try to get total credits from all users
                try {
                    const users = await apiCall('/core/v1/admin/users?limit=1000');
                    const totalCredits = users.users ? users.users.reduce((sum, u) => sum + (u.credits || 0), 0) : 0;
                    document.getElementById('metric-credits').textContent = totalCredits.toLocaleString();
                    
                    // Show signup credits info if configured
                    const pricing = await apiCall('/core/v1/admin/pricing/config');
                    const signupCredits = pricing.signup_initial_credits || 0;
                    if (signupCredits > 0) {
                        const estimatedCost = (users.users?.length || 0) * signupCredits;
                        document.getElementById('metric-credits').title = `Total: ${totalCredits} | Signup Credits: ${signupCredits} each | Est. Cost: ${estimatedCost} credits`;
                    }
                } catch (e) {
                    document.getElementById('metric-credits').textContent = 'N/A';
                    console.error('Failed to load credits:', e);
                }
                
                // Hide setup alert if configured
                if (state.token || state.adminKey) {
                    const setupAlert = document.getElementById('setup-alert');
                    if (setupAlert && !document.querySelector('#metric-users').textContent.includes('N/A')) {
                        setupAlert.style.display = 'none';
                    }
                }
            } catch (error) {
                console.error('Failed to load metrics:', error);
                // Show setup alert on any error
                const setupAlert = document.getElementById('setup-alert');
                if (setupAlert) setupAlert.style.display = 'block';
            }
        }

        async function loadPricingConfig() {
            try {
                const config = await apiCall('/core/v1/admin/pricing/config');
                
                // Populate form fields if they exist
                const revTarget = document.getElementById('rev_target');
                if (revTarget) revTarget.value = config.monthly_revenue_target_usd || 0;
                
                const usdToCredits = document.getElementById('usd_to_credits');
                if (usdToCredits) usdToCredits.value = config.usd_to_credits || 100;
                
                const marginMult = document.getElementById('margin_mult');
                if (marginMult) marginMult.value = config.target_margin_multiplier || 2;
                
                const minOpCost = document.getElementById('min_op_cost');
                if (minOpCost) minOpCost.value = config.minimum_operation_cost_credits || 0.01;
                
                // Load fixed costs if table exists (advanced tab)
                const fixedCostsTable = document.getElementById('fixed-costs-table');
                if (fixedCostsTable) {
                    fixedCostsTable.innerHTML = '';
                    const fixedCosts = config.fixed_monthly_costs_usd || [];
                    
                    if (fixedCosts.length === 0) {
                        // Aggiungi costi di default se non configurati
                        const defaultCosts = [
                            { name: "Infrastructure", cost_usd: 50 },
                            { name: "Payment Processor", cost_usd: 50 },
                            { name: "Business & Marketing", cost_usd: 150 },
                            { name: "Support & Maintenance", cost_usd: 80 },
                            { name: "Legal & Accounting", cost_usd: 50 }
                        ];
                        
                        defaultCosts.forEach(cost => {
                            addFixedCostRow(cost.name, cost.cost_usd);
                        });
                        
                        // Mostra messaggio che questi sono valori di default
                        showToast('Loaded default fixed costs - click Save to persist to Supabase', 'info');
                    } else {
                        fixedCosts.forEach(cost => {
                            addFixedCostRow(cost.name, cost.cost_usd);
                        });
                        showToast(`Loaded ${fixedCosts.length} fixed costs from Supabase`, 'success');
                    }
                    
                    // Update overhead preview
                    updateOverheadPreview(config);
                }
                
                // Debug: mostra la configurazione caricata
                console.log('Loaded pricing config:', config);
                
                // Run simulator if on simulator page
                if (document.getElementById('simulator-output')) {
                    simulatePricing(config);
                    // Bind live updates to inputs impacting multipliers
                    const bindIds = ['rev_target','usd_to_credits','margin_mult'];
                    bindIds.forEach(id => {
                        const el = document.getElementById(id);
                        if (el && !el._simBound) {
                            el.addEventListener('input', () => simulatePricing(config));
                            el._simBound = true;
                        }
                    });
                    // Also re-simulate when fixed costs table changes
                    const fixedTable = document.getElementById('fixed-costs-table');
                    if (fixedTable && !fixedTable._simBound) {
                        fixedTable.addEventListener('input', () => simulatePricing(config));
                        fixedTable._simBound = true;
                    }
                }
            } catch (error) {
                console.error('Failed to load pricing config:', error);
            }
        }

        async function loadBillingConfig() {
            try {
                const billingConfig = await apiCall('/core/v1/admin/billing/config');
                const config = billingConfig.config || {};
                const ls = config.lemonsqueezy || {};
                document.getElementById('ls_store').value = ls.store_id || '';
                document.getElementById('ls_test_mode').checked = ls.test_mode || false;
            } catch (error) {
                console.error('Failed to load billing config:', error);
            }
        }
        
        async function loadPlansData() {
            try {
                const plansResp = await apiCall('/core/v1/billing/plans');
                const plans = plansResp.plans || plansResp || [];
                
                // Populate plans table
                const tbody = document.getElementById('plans-table');
                if (tbody) {
                    tbody.innerHTML = '';
                    plans.forEach(plan => {
                        addPlanTableRow(plan);
                    });
                }
            } catch (error) {
                console.error('Failed to load plans data:', error);
            }
        }
        
        async function loadCreditsConfig() {
            try {
                const pricingConfig = await apiCall('/core/v1/admin/pricing/config');
                
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
        }
        
        async function loadCheckoutData() {
            try {
                // Load users for checkout
                const users = await apiCall('/core/v1/admin/users?limit=100');
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
                
                // Load plans for checkout
                const plansResp = await apiCall('/core/v1/billing/plans');
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

        // ========== Business Functions ==========
        function addFixedCostRow(name = '', cost = '') {
            const tbody = document.getElementById('fixed-costs-table');
            if (!tbody) return;
            
            // Rimuovi il messaggio informativo se presente
            const infoRow = tbody.querySelector('tr td[colspan="3"]');
            if (infoRow) {
                infoRow.closest('tr').remove();
            }
            
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td><input type="text" class="input input-sm input-bordered" value="${name}" placeholder="e.g., Infrastructure" /></td>
                <td><input type="number" class="input input-sm input-bordered" value="${cost}" step="0.01" placeholder="50.00" /></td>
                <td><button class="btn btn-sm btn-error" onclick="this.closest('tr').remove(); updateOverheadPreview()">Remove</button></td>
            `;
            
            // Add event listener to update preview on change
            tr.querySelectorAll('input').forEach(input => {
                input.addEventListener('input', updateOverheadPreview);
            });
            
            tbody.appendChild(tr);
        }
        
        function updateOverheadPreview(config = null) {
            try {
                // Calculate from current form values
                const revenueTarget = parseFloat(document.getElementById('rev_target')?.value) || 10000;
                
                // Get fixed costs from table
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
                
                // Or use config if provided
                if (config && config.fixed_monthly_costs_usd) {
                    totalFixedCosts = config.fixed_monthly_costs_usd.reduce((sum, c) => sum + (c.cost_usd || 0), 0);
                }
                
                const overheadMultiplier = revenueTarget > 0 ? (1 + (totalFixedCosts / revenueTarget)) : 1.0;
                
                // Update preview
                const totalEl = document.getElementById('total-fixed-costs');
                if (totalEl) totalEl.textContent = `$${totalFixedCosts.toLocaleString()}`;
                
                const multiplierEl = document.getElementById('overhead-multiplier');
                if (multiplierEl) multiplierEl.textContent = `${overheadMultiplier.toFixed(2)}x`;
                
            } catch (error) {
                console.error('Failed to update overhead preview:', error);
            }
        }
        
        async function saveFixedCosts() {
            try {
                // Prima carica la configurazione esistente
                const existingConfig = await apiCall('/core/v1/admin/pricing/config');
                
                // Raccogli i fixed costs dalla tabella
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
                
                // Aggiorna solo i fixed costs
                const updatedConfig = {
                    ...existingConfig,
                    fixed_monthly_costs_usd: fixedCosts
                };
                
                console.log('Saving fixed costs:', fixedCosts);
                
                const url = `/core/v1/admin/pricing/config`;
                await apiCall(url, {
                    method: 'PUT',
                    body: JSON.stringify(updatedConfig)
                });
                
                showToast('Fixed costs saved successfully!', 'success');
                updateOverheadPreview();
            } catch (error) {
                console.error('Save fixed costs error:', error);
                showToast('Failed to save fixed costs: ' + error.message, 'error');
            }
        }
        
        // ========== App Affordability Functions ==========
        async function loadAppAffordability() {
            try {
                // Carica lista app IDs
                const appIdsResp = await apiCall('/core/v1/admin/app-ids');
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
                
                // Carica configurazione DEFAULT e mostra affordability per app (usa flow_costs_usd come sorgente primaria)
                for (const appId of appIds) {
                    try {
                        const config = await apiCall(`/core/v1/admin/pricing/config`);
                        let minCredits = 0;
                        if (config.flow_costs_usd && typeof config.flow_costs_usd === 'object' && appId in config.flow_costs_usd) {
                            minCredits = parseFloat(config.flow_costs_usd[appId]) || 0;
                        } else {
                            // legacy mappa non più in uso: ignora
                            minCredits = 0;
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
                                <button class="btn btn-xs btn-ghost" onclick="testAppAffordability('${appId}')">
                                    <i class="fas fa-test-tube"></i> Test
                                </button>
                            </td>
                        `;
                        tbody.appendChild(tr);
                    } catch (e) {
                        console.error(`Failed to load config for app ${appId}:`, e);
                        const tr = document.createElement('tr');
                        tr.innerHTML = `
                            <td><span class="font-mono">${appId}</span></td>
                            <td>
                                <input type="number" class="input input-sm input-bordered" 
                                       data-app="${appId}" value="0" 
                                       step="0.01" placeholder="0" />
                            </td>
                            <td><span class="badge badge-error">Error</span></td>
                            <td>-</td>
                        `;
                        tbody.appendChild(tr);
                    }
                }
                
                showToast(`Loaded ${appIds.length} app configurations`, 'info');
            } catch (error) {
                console.error('Failed to load app affordability:', error);
                showToast('Failed to load app affordability: ' + error.message, 'error');
            }
        }
        
        async function saveAppAffordability() {
            try {
                const inputs = document.querySelectorAll('#app-affordability-table input[data-app]');
                // Unica PUT: aggiorna la mappa completa sul DEFAULT
                const existingConfig = await apiCall(`/core/v1/admin/pricing/config`);
                const flowMap = { ...(existingConfig.flow_costs_usd || {}) };
                inputs.forEach(input => {
                    const appId = input.dataset.app;
                    const minCredits = parseFloat(input.value) || 0;
                    flowMap[appId] = minCredits;
                });
                // Scrivi SOLO in flow_costs_usd e pulisci la legacy map per evitare duplicazioni
                const updatedConfig = { ...existingConfig, flow_costs_usd: flowMap, minimum_affordability_per_app: {} };
                await apiCall(`/core/v1/admin/pricing/config`, {
                    method: 'PUT',
                    body: JSON.stringify(updatedConfig)
                });
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
                showToast(`Saved affordability settings for ${inputs.length} apps`, 'success');
            } catch (error) {
                console.error('Save app affordability error:', error);
                showToast('Failed to save affordability settings: ' + error.message, 'error');
            }
        }
        
        async function testAppAffordability(appId) {
            try {
                const config = await apiCall(`/core/v1/admin/pricing/config`);
                const minCredits = (config.flow_costs_usd && typeof config.flow_costs_usd === 'object')
                  ? (parseFloat(config.flow_costs_usd[appId]) || 0)
                  : 0;
                showToast(`App "${appId}" requires minimum ${minCredits} credits for execution`, 'info');
            } catch (error) {
                showToast(`Failed to test app "${appId}": ${error.message}`, 'error');
            }
        }

        async function savePricingConfig() {
            try {
                // Leggi config esistente per preservare mappe e campi non nel form
                const existing = await apiCall('/core/v1/admin/pricing/config');

                // Raccogli flow base costs (se presente tabella)
                const flowCosts = { ...(existing.flow_costs_usd || {}) };
                const flowCostsTable = document.getElementById('flow-costs-table');
                if (flowCostsTable) {
                    flowCostsTable.querySelectorAll('tr').forEach(row => {
                        const key = row.cells[0].querySelector('input').value.trim();
                        const cost = parseFloat(row.cells[1].querySelector('input').value) || 0;
                        if (key) flowCosts[key] = cost;
                    });
                }

                const updated = {
                    ...existing,
                    monthly_revenue_target_usd: parseFloat(document.getElementById('rev_target').value) || 1000,
                    usd_to_credits: parseFloat(document.getElementById('usd_to_credits').value) || 100,
                    target_margin_multiplier: parseFloat(document.getElementById('margin_mult').value) || 2,
                    minimum_operation_cost_credits: parseFloat(document.getElementById('min_op_cost').value) || 0.01,
                    flow_costs_usd: flowCosts,
                    // Preserva fixed_monthly_costs_usd (gestiti nella tab dedicata)
                    fixed_monthly_costs_usd: existing.fixed_monthly_costs_usd || [],
                    // Preserva affordability map
                    minimum_affordability_per_app: existing.minimum_affordability_per_app || {},
                    // Rollout: se non presenti nel form, mantieni esistenti
                    rollout_interval: existing.rollout_interval ?? 'monthly',
                    rollout_credits_per_period: typeof existing.rollout_credits_per_period === 'number' ? existing.rollout_credits_per_period : 1000,
                    rollout_max_credits_rollover: typeof existing.rollout_max_credits_rollover === 'number' ? existing.rollout_max_credits_rollover : 2000,
                    rollout_proration: existing.rollout_proration ?? 'none',
                    rollout_percentage: typeof existing.rollout_percentage === 'number' ? existing.rollout_percentage : 100.0,
                    rollout_scheduler_enabled: !!existing.rollout_scheduler_enabled,
                    rollout_scheduler_time_utc: existing.rollout_scheduler_time_utc || '03:00',
                    // Sconti & business
                    plan_discounts_percent: existing.plan_discounts_percent || {},
                    signup_initial_credits: typeof existing.signup_initial_credits === 'number' ? existing.signup_initial_credits : 100,
                    signup_initial_credits_cost_usd: typeof existing.signup_initial_credits_cost_usd === 'number' ? existing.signup_initial_credits_cost_usd : 0,
                    unused_credits_recognized_as_revenue: existing.unused_credits_recognized_as_revenue !== false
                };

                console.log('Saving pricing config:', updated);

                // Salva sempre il DEFAULT
                const url = `/core/v1/admin/pricing/config`;
                await apiCall(url, {
                    method: 'PUT',
                    body: JSON.stringify(updated)
                });

                showToast('Pricing configuration saved successfully!', 'success');

                // Update simulator se visibile
                if (document.getElementById('simulator-output')) {
                    simulatePricing(updated);
                }
            } catch (error) {
                console.error('Save pricing config error:', error);
                showToast('Failed to save configuration: ' + error.message, 'error');
            }
        }

        function simulatePricing(config) {
            // Fixed costs: prefer live DOM table if present, else sum from config
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

            // Read current inputs if available, else fallback to config
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

        // ========== Billing Functions ==========
        function addPlanTableRow(plan) {
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
                <td><input type="number" class="input input-sm input-bordered" value="${plan.discount_percent || ''}" step="0.1" /></td>
                <td><button class="btn btn-sm btn-error" onclick="this.closest('tr').remove()">Remove</button></td>
            `;
            tbody.appendChild(tr);
        }

        function addPlanRow() {
            addPlanTableRow({});
        }

        async function generateCheckout() {
            try {
                const userId = document.getElementById('checkout_user').value;
                const planId = document.getElementById('checkout_plan').value;
                
                if (!userId || !planId) {
                    showToast('Please select both user and plan', 'warning');
                    return;
                }
                
                const url = `/core/v1/admin/billing/checkout?user_id=${userId}&plan_id=${planId}`;
                const result = await apiCall(url, { method: 'POST' });
                
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
                showToast('Failed to generate checkout', 'error');
            }
        }

        async function testProviderConnection() {
            try {
                const result = await apiCall('/core/v1/admin/credentials/test?provider=lemonsqueezy', {
                    method: 'POST'
                });
                showToast('Connection test: ' + (result.status || 'Success'), 'success');
            } catch (error) {
                showToast('Connection test failed: ' + error.message, 'error');
            }
        }
        
        async function saveBillingProviderConfig() {
            try {
                // Leggi piani e mappa variant dal DOM
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
                
                console.log('Saving billing provider config:', config);
                
                const url = `/core/v1/admin/billing/config`;
                await apiCall(url, {
                    method: 'PUT',
                    body: JSON.stringify(config)
                });
                
                showToast('Provider configuration saved successfully!', 'success');
            } catch (error) {
                console.error('Save provider config error:', error);
                showToast('Failed to save provider configuration: ' + error.message, 'error');
            }
        }

        async function loadBillingConfig() {
            try {
                const billingConfig = await apiCall('/core/v1/admin/billing/config');
                const config = billingConfig.config || {};
                const ls = config.lemonsqueezy || {};
                document.getElementById('ls_store').value = ls.store_id || '';
                document.getElementById('ls_test_mode').checked = !!ls.test_mode;
                // Carica piani e popola tabella mapping
                const plansResp = await apiCall('/core/v1/billing/plans');
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
                showToast('Failed to load provider configuration: ' + error.message, 'error');
            }
        }

        // ========== Observability Functions ==========
        async function loadAILogs() {
            try {
                const logs = await apiCall('/core/v1/admin/observability/openrouter/logs?limit=20');
                const output = document.getElementById('ai-logs-output');
                output.innerHTML = `<pre class="json">${JSON.stringify(logs, null, 2)}</pre>`;
            } catch (error) {
                showToast('Failed to load AI logs', 'error');
            }
        }

        async function loadCreditsLedger() {
            try {
                const userId = document.getElementById('ledger_user_filter').value.trim();
                const url = userId 
                    ? `/core/v1/admin/observability/credits/ledger?user_id=${userId}&limit=50`
                    : '/core/v1/admin/observability/credits/ledger?limit=50';
                
                const ledger = await apiCall(url);
                const output = document.getElementById('credits-ledger-output');
                output.innerHTML = `<pre class="json">${JSON.stringify(ledger, null, 2)}</pre>`;
            } catch (error) {
                showToast('Failed to load credits ledger', 'error');
            }
        }

        async function previewRollout() {
            try {
                const preview = await apiCall('/core/v1/admin/observability/rollout/preview', {
                    method: 'POST'
                });
                const output = document.getElementById('rollout-output');
                output.innerHTML = `<pre class="json">${JSON.stringify(preview, null, 2)}</pre>`;
            } catch (error) {
                showToast('Failed to preview rollout', 'error');
            }
        }

        async function runRollout() {
            if (!confirm('Are you sure you want to run the rollout?')) return;
            
            try {
                const result = await apiCall('/core/v1/admin/observability/rollout/run', {
                    method: 'POST'
                });
                showToast('Rollout completed', 'success');
                const output = document.getElementById('rollout-output');
                output.innerHTML = `<pre class="json">${JSON.stringify(result, null, 2)}</pre>`;
            } catch (error) {
                showToast('Failed to run rollout', 'error');
            }
        }

        // ========== Rollout Functions ==========
        async function saveCreditsAndRolloutConfig() {
            try {
                // Prima carica la configurazione esistente
                const existingConfig = await apiCall('/core/v1/admin/pricing/config');
                
                // Aggiorna i campi signup e rollout
                const updatedConfig = {
                    ...existingConfig,
                    // Signup Credits
                    signup_initial_credits: parseFloat(document.getElementById('signup_initial_credits').value) || 100,
                    signup_initial_credits_cost_usd: parseFloat(document.getElementById('signup_credits_cost').value) || 0,
                    // Rollout Settings
                    rollout_interval: document.getElementById('rollout_interval').value || 'monthly',
                    rollout_credits_per_period: parseInt(document.getElementById('rollout_credits').value) || 1000,
                    rollout_max_credits_rollover: parseInt(document.getElementById('rollout_max').value) || 2000,
                    rollout_percentage: parseFloat(document.getElementById('rollout_percentage').value) || 100
                };
                
                console.log('Saving credits and rollout config:', updatedConfig);
                
                const url = `/core/v1/admin/pricing/config`;
                await apiCall(url, {
                    method: 'PUT',
                    body: JSON.stringify(updatedConfig)
                });
                
                showToast('Credits and rollout configuration saved successfully!', 'success');
            } catch (error) {
                console.error('Save credits config error:', error);
                showToast('Failed to save credits configuration: ' + error.message, 'error');
            }
        }

        // ========== Configuration Functions ==========
        async function upsertFlowConfig() {
            try {
                const config = {
                    app_id: document.getElementById('flow_app_id').value.trim() || 'default',
                    flow_key: document.getElementById('flow_key').value.trim(),
                    flow_id: document.getElementById('flow_id').value.trim(),
                    node_names: document.getElementById('node_names').value.split(',').map(s => s.trim()).filter(Boolean)
                };
                
                await apiCall('/core/v1/admin/flow-configs', {
                    method: 'POST',
                    body: JSON.stringify(config)
                });
                
                showToast('Flow configuration saved', 'success');
            } catch (error) {
                showToast('Failed to save flow configuration', 'error');
            }
        }

        async function rotateCredential(credentialKey) {
            const newValue = prompt(`Enter new value for ${credentialKey}:`);
            if (!newValue) return;
            
            try {
                await apiCall('/core/v1/admin/credentials/rotate', {
                    method: 'POST',
                    body: JSON.stringify({
                        provider: 'lemonsqueezy',
                        credential_key: credentialKey,
                        new_value: newValue
                    })
                });
                
                showToast(`${credentialKey} rotated successfully`, 'success');
            } catch (error) {
                showToast('Failed to rotate credential', 'error');
            }
        }

        // ========== Testing Functions ==========
        async function executeFlow() {
            try {
                const flowKey = document.getElementById('test_flow_key').value.trim();
                const appId = document.getElementById('test_app_id').value.trim() || 'default';
                const inputData = document.getElementById('test_input').value.trim();
                const streaming = document.getElementById('test_streaming').checked;
                
                const body = {
                    flow_key: flowKey,
                    input: inputData ? JSON.parse(inputData) : {}
                };
                
                const output = document.getElementById('test-output');
                output.innerHTML = '<span class="loading loading-spinner loading-md"></span> Executing...';
                
                const url = streaming 
                    ? `/core/v1/flows/execute/stream?app_id=${appId}`
                    : `/core/v1/flows/execute?app_id=${appId}`;
                
                const result = await apiCall(url, {
                    method: 'POST',
                    body: JSON.stringify(body)
                });
                
                output.innerHTML = `<pre class="json">${JSON.stringify(result, null, 2)}</pre>`;
            } catch (error) {
                document.getElementById('test-output').innerHTML = `
                    <div class="alert alert-error">
                        <i class="fas fa-exclamation-triangle"></i>
                        <span>Execution failed: ${error.message}</span>
                    </div>
                `;
            }
        }

        // ========== Initialize ==========
        document.addEventListener('DOMContentLoaded', () => {
            // Auto-save admin key if not already saved
            if (state.adminKey && !localStorage.getItem('flowstarter_admin_key')) {
                saveState();
                console.log('Auto-saved admin key to localStorage');
            }
            
            // Debug state
            console.log('Dashboard initialized with state:', {
                hasToken: !!state.token,
                hasAdminKey: !!state.adminKey,
                baseUrl: state.baseUrl,
                appId: state.appId
            });
            
            // Set up navigation
            document.querySelectorAll('[data-page]').forEach(link => {
                link.addEventListener('click', (e) => {
                    e.preventDefault();
                    const page = link.dataset.page;
                    const tab = link.dataset.tab;
                    navigate(page, tab);
                });
            });
            
            // Set up tab handlers
            setupTabHandlers();
            
            // Load initial page
            navigate('overview');
        });
    </script>
</body>
</html>
    """


@router.get("/business-dashboard", response_class=HTMLResponse, include_in_schema=False)
async def business_dashboard() -> str:
    """Business & Pricing dashboard redirect."""
    return '<html><head><meta http-equiv="refresh" content="0;url=/core/v1/admin-ui/dashboard#business-config"></head></html>'


@router.get("/business", response_class=HTMLResponse, include_in_schema=False)
async def business_dashboard_compat() -> str:
    return await business_dashboard()


@router.get("/billing", response_class=HTMLResponse, include_in_schema=False)
async def billing_ui() -> str:
    """Billing redirect."""
    return '<html><head><meta http-equiv="refresh" content="0;url=/core/v1/admin-ui/dashboard#billing-plans"></head></html>'


@router.get("/observability", response_class=HTMLResponse, include_in_schema=False)
async def observability_ui() -> str:
    """Observability redirect."""
    return '<html><head><meta http-equiv="refresh" content="0;url=/core/v1/admin-ui/dashboard#observability-ai"></head></html>'
