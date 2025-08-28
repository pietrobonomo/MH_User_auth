from __future__ import annotations

"""
Utility di override per Flowise, allineata alla logica esistente:
- Carica brand_voice e config da file o da override passati
- Costruisce overrideConfig.vars con mapping coerente (tone_of_voice, stopwords, ecc.)
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional


def _process_replacement_rules(rules: List[Dict[str, str]]) -> List[Dict[str, str]]:
    if not rules or not isinstance(rules, list):
        return []
    processed: List[Dict[str, str]] = []
    for rule in rules:
        if isinstance(rule, dict) and 'forbidden' in rule and 'replacement' in rule:
            if rule['forbidden'] and rule['replacement']:
                processed.append({"forbidden": rule['forbidden'], "replacement": rule['replacement']})
    return processed


def _load_json(path: Path) -> Dict[str, Any]:
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def generate_flowise_override(
    platform: Optional[str] = None,
    *,
    brand_voice_override: Optional[Dict[str, Any]] = None,
    config_override: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Genera la configurazione override per Flowise.

    Origine dati:
    - Se forniti, usa brand_voice_override e config_override
    - Altrimenti prova da file:
      - FLOWISE_BRAND_VOICE_PATH (default: backend/data/brand_voice.json)
      - FLOWISE_CONFIG_PATH (default: backend/data/config.json)
    """
    if brand_voice_override is not None and config_override is not None:
        brand_voice = brand_voice_override
        config = config_override
    else:
        bv_path = Path(os.environ.get('FLOWISE_BRAND_VOICE_PATH', 'backend/data/brand_voice.json'))
        cfg_path = Path(os.environ.get('FLOWISE_CONFIG_PATH', 'backend/data/config.json'))
        if not bv_path.exists():
            raise FileNotFoundError(f"File brand_voice.json non trovato in {bv_path}")
        if not cfg_path.exists():
            raise FileNotFoundError(f"File config.json non trovato in {cfg_path}")
        brand_voice = _load_json(bv_path)
        config = _load_json(cfg_path)

    processed_rules = _process_replacement_rules(brand_voice.get('replacement_rules', []))

    vars_payload: Dict[str, Any] = {
        "brand_name": brand_voice.get('brand_name', ''),
        "language": config.get('language', 'italiano'),
        "tone_of_voice": brand_voice.get('brand_personality', []),
        "target_audience": brand_voice.get('target_audience', ''),
        "stopwords": brand_voice.get('forbidden_words', ''),
        "word_replacement": processed_rules,
        "fb_post_examples": brand_voice.get('social_examples', {}).get('facebook', ''),
        "linkedin_post_examples": brand_voice.get('social_examples', {}).get('linkedin', ''),
        "X_post_examples": brand_voice.get('social_examples', {}).get('X', ''),
        "content": "",
        "platform": platform or "",
        "test_override_active": "OVERRIDE_ATTIVO",
    }

    return {"overrideConfig": {"vars": vars_payload}}


