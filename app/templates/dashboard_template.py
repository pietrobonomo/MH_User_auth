"""
Template della Dashboard Unificata per Flow Starter.
Struttura modulare e mantenibile per la dashboard amministrativa.
"""

from typing import Dict, List, Optional


class DashboardTemplate:
    """Template modulare per la dashboard unificata."""
    
    @staticmethod
    def render() -> str:
        """Renderizza l'HTML completo della dashboard."""
        return f"""<!doctype html>
<html data-theme="corporate">
<head>
    {DashboardTemplate._render_head()}
</head>
<body>
    {DashboardTemplate._render_body()}
    {DashboardTemplate._render_scripts()}
</body>
</html>"""

    @staticmethod
    def _render_head() -> str:
        """Renderizza la sezione head con meta tag, CSS e stili."""
        return """
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
    </style>"""

    @staticmethod
    def _render_body() -> str:
        """Renderizza il body con drawer layout e contenuto principale."""
        return f"""
    <div class="drawer lg:drawer-open">
        <input id="drawer-toggle" type="checkbox" class="drawer-toggle" />
        
        <!-- Main Content -->
        <div class="drawer-content flex flex-col">
            {DashboardTemplate._render_navbar()}
            {DashboardTemplate._render_content_area()}
        </div>
        
        <!-- Sidebar -->
        {DashboardTemplate._render_sidebar()}
    </div>"""

    @staticmethod
    def _render_navbar() -> str:
        """Renderizza la navbar per mobile."""
        return """
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
            </div>"""

    @staticmethod
    def _render_content_area() -> str:
        """Renderizza l'area contenuti principale."""
        return """
            <!-- Content Area -->
            <div class="content-area bg-base-200 p-4 lg:p-6">
                <div id="main-content" class="max-w-7xl mx-auto">
                    <!-- Il contenuto verrà caricato dinamicamente -->
                    <div class="flex items-center justify-center h-96">
                        <span class="loading loading-spinner loading-lg"></span>
                    </div>
                </div>
            </div>"""

    @staticmethod
    def _render_sidebar() -> str:
        """Renderizza la sidebar con navigazione."""
        return """
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
                                <i class="fas fa-eye w-5"></i>
                                <span>Observability</span>
                            </summary>
                            <ul class="ml-4">
                                <li><a href="#" data-page="observability-ai">AI Usage</a></li>
                                <li><a href="#" data-page="observability-credits">Credits Ledger</a></li>
                                <li><a href="#" data-page="observability-rollout">Rollout Manager</a></li>
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
                                <li><a href="#" data-page="config-flows">Flow Configs</a></li>
                                <li><a href="#" data-page="config-payment">Payment Provider</a></li>
                                <li><a href="#" data-page="config-security">Security</a></li>
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
                    
                    <!-- Separator -->
                    <li class="mt-4 pt-4 border-t">
                        <button class="btn btn-sm btn-outline btn-primary w-full" onclick="clearLocalData()">
                            <i class="fas fa-trash"></i>
                            Clear Local Data
                        </button>
                    </li>
                </ul>
            </aside>
        </div>"""

    @staticmethod
    def _render_scripts() -> str:
        """Renderizza tutti gli script JavaScript necessari."""
        from .dashboard_scripts import get_dashboard_scripts
        return get_dashboard_scripts()
