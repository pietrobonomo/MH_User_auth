"""
Advanced Pricing System - Flow Starter
=====================================
Sistema di pricing avanzato con margini e costi configurabili dinamicamente.
Permette simulazioni di business cambiando revenue target e costi fissi.
"""
import os
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List
import httpx
from dataclasses import dataclass, field, asdict, fields

logger = logging.getLogger(__name__)

@dataclass
class FixedCost:
    """Rappresenta un singolo costo fisso mensile."""
    name: str
    cost_usd: float

@dataclass
class PricingConfig:
    """Configurazione pricing dinamica e personalizzabile."""
    
    # Obiettivi di business
    monthly_revenue_target_usd: float = 1000.0

    # Costi fissi mensili in valore assoluto (USD)
    fixed_monthly_costs_usd: List[FixedCost] = field(default_factory=lambda: [
        FixedCost(name="Infrastructure", cost_usd=50.0),
        FixedCost(name="Payment Processor", cost_usd=50.0),
        FixedCost(name="Business & Marketing", cost_usd=150.0),
        FixedCost(name="Support & Maintenance", cost_usd=80.0),
        FixedCost(name="Legal & Accounting", cost_usd=50.0),
    ])

    # Conversione base
    usd_to_credits: float = 100.0  # 1 USD = 100 crediti
    
    # Margini target
    target_margin_multiplier: float = 2.5  # 2.5x margin target

    # Override costo base per flow (key: flow_key o flow_id), valore in USD
    flow_costs_usd: Dict[str, float] = field(default_factory=dict)
    
    # Overhead totale calcolato dinamicamente
    @property
    def total_overhead_percentage(self) -> float:
        """Calcola l'incidenza percentuale totale dell'overhead sul revenue target."""
        if self.monthly_revenue_target_usd <= 0:
            return 0.0
        
        total_fixed_costs = sum(cost.cost_usd for cost in self.fixed_monthly_costs_usd)
        # Include costo mensile stimato dei crediti di signup (solo BI)
        try:
            total_fixed_costs += float(self.signup_initial_credits_cost_usd or 0.0) * int(getattr(self, 'bi_monthly_new_users', 0) or 0)
        except Exception:
            pass
        return total_fixed_costs / self.monthly_revenue_target_usd

    @property
    def total_overhead_multiplier(self) -> float:
        """Calcola l'overhead totale come moltiplicatore."""
        return 1.0 + self.total_overhead_percentage
    
    # Moltiplicatore finale per crediti
    @property
    def final_credit_multiplier(self) -> float:
        """Calcola moltiplicatore finale per convertire costi in crediti."""
        return self.target_margin_multiplier * self.total_overhead_multiplier * self.usd_to_credits
    
    # Costi minimi per evitare addebiti a 0.00
    minimum_operation_cost_credits: float = 0.01

    # Nuovi campi gestiti da business dashboard
    # Crediti iniziali assegnati all'iscrizione utente
    signup_initial_credits: float = 0.0
    # Soglie minime di affordability per app: app_id -> credits richiesti
    minimum_affordability_per_app: Dict[str, float] = field(default_factory=dict)

    # Rollout: rimosso dal modello operativo (gestito per-piano in billing_configs)

    # Sconti e pacchetti (business)
    plan_discounts_percent: Dict[str, float] = field(default_factory=dict)  # plan_id -> percentuale sconto
    signup_initial_credits_cost_usd: float = 0.0  # costo da considerare a P&L per crediti di benvenuto
    # BI: stima nuovi utenti/mese per forecast signup cost
    bi_monthly_new_users: int = 0

    # Revenue recognition
    unused_credits_recognized_as_revenue: bool = True

class AdvancedPricingSystem:
    """
    Sistema di pricing avanzato con configurazione dinamica per simulazioni di business.
    """
    
    def __init__(self, config_file: str):
        self.config_file = config_file
        # Fonte primaria: Supabase (per-azienda). Fallback a default se Supabase non disponibile.
        self.config = PricingConfig()
        
        # Costi base delle operazioni in USD (hardcoded ma basati su dati reali)
        # In futuro, anche questi potrebbero diventare configurabili
        self.operation_costs_usd = {
            # Costi placeholder per Flowise e OpenRouter
            "flowise_execute": 0.025,  # Costo medio stimato per un flow complesso
            "openrouter_chat": 0.015,   # Costo medio stimato per una chat
            
            # Esempi di costi più granulari (da implementare se necessario)
            "text_generation_short": 0.005,
            "text_generation_long": 0.030,
            "image_generation": 0.040,
        }

    def _load_config(self) -> PricingConfig:
        """Legacy rimosso: ritorna default."""
        return PricingConfig()

    async def _load_from_supabase_async(self, app_id: Optional[str] = None) -> Optional[PricingConfig]:
        """Carica la configurazione da Supabase.
        
        Strategia:
        - Carica SEMPRE la riga 'default' (single source of truth a livello progetto)
        - Per retrocompatibilità, se specificato, prova anche la riga per app_id
        - Se viene trovata una config valida, aggiorna self.config e la ritorna
        """
        supabase_url = os.environ.get("SUPABASE_URL")
        service_key = os.environ.get("SUPABASE_SERVICE_KEY")
        if not supabase_url or not service_key:
            return None
        headers = {
            "apikey": service_key,
            "Authorization": f"Bearer {service_key}",
            "Accept": "application/json",
        }
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                # 1) Prova riga 'default'
                r = await client.get(f"{supabase_url}/rest/v1/pricing_configs?app_id=eq.default&select=config", headers=headers)
                cfg_obj: Optional[Dict[str, Any]] = None
                if r.status_code == 200:
                    data = r.json()
                    if data:
                        cfg_obj = data[0].get("config") or {}
                # 2) Retrocompatibilità: se non trovata e app_id specificato, prova quella riga
                if cfg_obj is None and app_id and app_id != "default":
                    r2 = await client.get(f"{supabase_url}/rest/v1/pricing_configs?app_id=eq.{app_id}&select=config", headers=headers)
                    if r2.status_code == 200:
                        data2 = r2.json()
                        if data2:
                            cfg_obj = data2[0].get("config") or {}

            if cfg_obj is None:
                return None

            # Parsing e normalizzazione
            if not isinstance(cfg_obj, dict):
                cfg_obj = json.loads(cfg_obj) if isinstance(cfg_obj, str) else {}

            # Filtra chiavi sconosciute per compat con versioni legacy
            valid_field_names = {f.name for f in fields(PricingConfig)}
            filtered: Dict[str, Any] = {k: v for k, v in cfg_obj.items() if k in valid_field_names}

            # Normalizzazioni
            if 'fixed_monthly_costs_usd' in filtered:
                try:
                    filtered['fixed_monthly_costs_usd'] = [FixedCost(**c) for c in filtered['fixed_monthly_costs_usd']]
                except Exception:
                    filtered['fixed_monthly_costs_usd'] = []
            if 'flow_costs_usd' not in filtered or not isinstance(filtered.get('flow_costs_usd'), dict):
                filtered['flow_costs_usd'] = {}

            loaded = PricingConfig(**filtered)
            # Aggiorna in memoria per uso successivo
            self.config = loaded
            logger.info("📥 Pricing config caricata da Supabase (source=default%s)", f", fallback={app_id}" if app_id and app_id != "default" else "")
            return loaded
        except Exception as e:
            logger.warning(f"⚠️ Errore caricamento pricing da Supabase: {e}")
            return None

    def save_to_supabase(self, app_id: str, config: Optional[PricingConfig] = None) -> bool:
        """Salva la configurazione su Supabase come fonte di verità.
        Ritorna True/False senza sollevare eccezioni."""
        supabase_url = os.environ.get("SUPABASE_URL")
        service_key = os.environ.get("SUPABASE_SERVICE_KEY")
        if not supabase_url or not service_key:
            return False
        cfg_obj = config or self.config
        try:
            payload = asdict(cfg_obj)
            # Filtra eventuali chiavi legacy di rollout per evitare duplicazioni con billing_configs
            for k in [
                'rollout_interval', 'rollout_credits_per_period', 'rollout_max_credits_rollover',
                'rollout_proration', 'rollout_percentage', 'rollout_scheduler_enabled', 'rollout_scheduler_time_utc'
            ]:
                if k in payload:
                    payload.pop(k, None)
            headers = {
                "apikey": service_key,
                "Authorization": f"Bearer {service_key}",
                "Content-Type": "application/json",
                "Prefer": "resolution=merge-duplicates,return=representation",
            }
            with httpx.Client(timeout=12.0) as client:
                r = client.post(f"{supabase_url}/rest/v1/pricing_configs", headers=headers, json={"app_id": app_id, "config": payload})
            return r.status_code in (200, 201)
        except Exception as e:
            logger.warning(f"⚠️ Errore salvataggio pricing su Supabase: {e}")
            return False

    def save_config(self, config: Optional[PricingConfig] = None) -> bool:
        """Legacy rimosso: non salva su file. Ritorna True per compatibilità."""
        return True

    def get_config(self) -> PricingConfig:
        """Ritorna la configurazione corrente."""
        return self.config

    def update_config(self, new_config_data: Dict[str, Any]) -> PricingConfig:
        """Aggiorna la configurazione e la salva."""
        # Filtra chiavi legacy di rollout dal payload in ingresso
        for k in [
            'rollout_interval', 'rollout_credits_per_period', 'rollout_max_credits_rollover',
            'rollout_proration', 'rollout_percentage', 'rollout_scheduler_enabled', 'rollout_scheduler_time_utc'
        ]:
            if k in new_config_data:
                new_config_data.pop(k, None)

        # Crea una nuova istanza di PricingConfig partendo dai dati forniti
        if 'fixed_monthly_costs_usd' in new_config_data:
            new_config_data['fixed_monthly_costs_usd'] = [FixedCost(**cost) for cost in new_config_data['fixed_monthly_costs_usd']]
        if 'flow_costs_usd' in new_config_data and not isinstance(new_config_data['flow_costs_usd'], dict):
            new_config_data['flow_costs_usd'] = {}
        
        self.config = PricingConfig(**new_config_data)
        logging.info("🔧 Configurazione pricing aggiornata (in memoria).")
        return self.config

    def calculate_operation_cost_credits(self, operation_type: str, context: Optional[Dict] = None) -> float:
        """
        Calcola il costo finale in crediti per una data operazione.
        - Supporta override per flow specifico (context['flow_key'] o context['flow_id']).
        """
        context = context or {}

        # Determina costo base USD
        base_cost_usd = self.operation_costs_usd.get(operation_type, 0.01)
        
        if operation_type == "flowise_execute":
            # Priorità: flow_key, poi flow_id
            flow_key = context.get("flow_key") if isinstance(context, dict) else None
            flow_id = context.get("flow_id") if isinstance(context, dict) else None
            if flow_key and flow_key in self.config.flow_costs_usd:
                base_cost_usd = float(self.config.flow_costs_usd[flow_key])
            elif flow_id and flow_id in self.config.flow_costs_usd:
                base_cost_usd = float(self.config.flow_costs_usd[flow_id])
        
        final_cost_credits = base_cost_usd * self.config.final_credit_multiplier
        
        # Applica il costo minimo per garantire sostenibilità
        cost = max(final_cost_credits, self.config.minimum_operation_cost_credits)
        
        logging.debug(f"💰 Costo calcolato per '{operation_type}' (base ${base_cost_usd:.6f}): {cost:.2f} crediti")
        return round(cost, 2)

    def calculate_flow_pricing(self, flow_key: Optional[str], flow_id: Optional[str]) -> Dict[str, float]:
        """Ritorna un breakdown dei moltiplicatori business per un flow.
        Keys: usd_to_credits, overhead_multiplier, margin_multiplier, final_credit_multiplier, final_cost_credits, final_cost_usd
        Nota: base_cost_usd è stato rimosso per evitare ambiguità.
        """
        # Base USD (override per flow o default op)
        base_cost_usd = self.operation_costs_usd.get("flowise_execute", 0.01)
        if flow_key and flow_key in self.config.flow_costs_usd:
            base_cost_usd = float(self.config.flow_costs_usd[flow_key])
        elif flow_id and flow_id in self.config.flow_costs_usd:
            base_cost_usd = float(self.config.flow_costs_usd[flow_id])

        overhead_multiplier = self.config.total_overhead_multiplier
        margin_multiplier = self.config.target_margin_multiplier
        usd_to_credits = self.config.usd_to_credits
        final_credit_multiplier = overhead_multiplier * margin_multiplier * usd_to_credits
        usd_multiplier = overhead_multiplier * margin_multiplier
        total_multiplier_percent = usd_multiplier * 100.0
        markup_percent = (usd_multiplier - 1.0) * 100.0
        final_cost_credits = max(base_cost_usd * final_credit_multiplier, self.config.minimum_operation_cost_credits)
        # Prezzo finale anche in USD (prima della conversione crediti): divide per usd_to_credits
        final_cost_usd = round(final_cost_credits / usd_to_credits, 6) if usd_to_credits else round(base_cost_usd * overhead_multiplier * margin_multiplier, 6)

        return {
            "usd_to_credits": float(usd_to_credits),
            "overhead_multiplier": round(overhead_multiplier, 6),
            "margin_multiplier": round(margin_multiplier, 6),
            "final_credit_multiplier": round(final_credit_multiplier, 6),
            "usd_multiplier": round(usd_multiplier, 6),
            "total_multiplier_percent": round(total_multiplier_percent, 3),
            "markup_percent": round(markup_percent, 3),
            "final_cost_credits": round(final_cost_credits, 2),
            "final_cost_usd": final_cost_usd,
        }
