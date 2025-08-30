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
from dataclasses import dataclass, field, asdict

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
    # Soglia minima di affordability a livello app per sbloccare operazioni
    minimum_affordability_credits: float = 0.0

class AdvancedPricingSystem:
    """
    Sistema di pricing avanzato con configurazione dinamica per simulazioni di business.
    """
    
    def __init__(self, config_file: str):
        self.config_file = config_file
        self.config = self._load_config()
        
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
        """Carica la configurazione da un file JSON, o ne crea uno di default."""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    data = json.load(f)
                    # Converte la lista di dizionari in una lista di oggetti FixedCost
                    if 'fixed_monthly_costs_usd' in data:
                        data['fixed_monthly_costs_usd'] = [FixedCost(**cost) for cost in data['fixed_monthly_costs_usd']]
                    # Garantisce la presenza del mapping per flow
                    if 'flow_costs_usd' not in data or not isinstance(data['flow_costs_usd'], dict):
                        data['flow_costs_usd'] = {}
                    return PricingConfig(**data)
            except (json.JSONDecodeError, TypeError, KeyError) as e:
                logging.warning(f"⚠️ Errore nel caricare {self.config_file}: {e}. Verrà creato un nuovo file di default.")
        
        # Se il file non esiste o è corrotto, crea e salva una config di default
        default_config = PricingConfig()
        self.save_config(default_config)
        return default_config

    def save_config(self, config: Optional[PricingConfig] = None) -> bool:
        """Salva la configurazione corrente o una fornita su file JSON."""
        config_to_save = config or self.config
        try:
            # Assicura che la directory esista
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            with open(self.config_file, 'w') as f:
                # Usa asdict per convertire la dataclass (e gli oggetti FixedCost annidati) in un dizionario
                json.dump(asdict(config_to_save), f, indent=2)
            logging.info(f"💾 Configurazione pricing salvata in {self.config_file}")
            return True
        except Exception as e:
            logging.error(f"❌ Errore durante il salvataggio della configurazione: {e}")
            return False

    def get_config(self) -> PricingConfig:
        """Ritorna la configurazione corrente."""
        return self.config

    def update_config(self, new_config_data: Dict[str, Any]) -> PricingConfig:
        """Aggiorna la configurazione e la salva."""
        # Crea una nuova istanza di PricingConfig partendo dai dati forniti
        if 'fixed_monthly_costs_usd' in new_config_data:
            new_config_data['fixed_monthly_costs_usd'] = [FixedCost(**cost) for cost in new_config_data['fixed_monthly_costs_usd']]
        if 'flow_costs_usd' in new_config_data and not isinstance(new_config_data['flow_costs_usd'], dict):
            new_config_data['flow_costs_usd'] = {}
        
        self.config = PricingConfig(**new_config_data)
        self.save_config()
        logging.info("🔧 Configurazione pricing aggiornata e salvata.")
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
