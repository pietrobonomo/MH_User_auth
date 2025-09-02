from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from typing import Dict
import os
from dotenv import load_dotenv
import asyncio
from datetime import datetime, timedelta, timezone
import httpx
from pathlib import Path

# Carica variabili da .env PRIMA di importare router/endpoints che le usano
load_dotenv()

from app.api.router import api_router

app = FastAPI(
    title="Flow Starter Core API",
    description="Core API standalone per auth/crediti/proxy AI",
    version="0.1.0"
)

origins = [
    os.environ.get("CORE_CORS_ORIGIN", "http://127.0.0.1:5173"),
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_origin_regex=r"https?://(localhost|127\.0\.0\.1):\d+",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Monta router principale
app.include_router(api_router, prefix="/core/v1")

# Monta file statici per la dashboard
static_path = Path(__file__).parent / "static"
if static_path.exists():
    app.mount("/static", StaticFiles(directory=str(static_path)), name="static")

@app.get("/health")
async def health() -> Dict[str, str]:
    """Health check semplice.

    Returns:
        Dict[str, str]: Stato del servizio.
    """
    return {"status": "ok"}


# =============================
# Rollout Scheduler (opzionale)
# =============================

async def _has_run_this_month(supabase_url: str, service_key: str) -> bool:
    """Controlla se esiste già un run di rollout nel mese corrente (UTC)."""
    now = datetime.now(timezone.utc)
    start_month = datetime(year=now.year, month=now.month, day=1, tzinfo=timezone.utc)
    headers = {
        "apikey": service_key,
        "Authorization": f"Bearer {service_key}",
        "Accept": "application/json",
    }
    url = (
        f"{supabase_url}/rest/v1/credits_rollout_runs"
        f"?run_timestamp=gte.{start_month.isoformat()}&select=id&limit=1"
    )
    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            r = await client.get(url, headers=headers)
            if r.status_code != 200:
                return False
            rows = r.json() or []
            return len(rows) > 0
    except Exception:
        return False


async def _rollout_scheduler_loop() -> None:
    """Loop semplice: ogni giorno all'ora configurata controlla ed esegue rollout mensile se necessario.

    Env:
      CORE_ENABLE_ROLLOUT_SCHEDULER = '1' per attivare
      CORE_ROLLOUT_TIME_UTC = '03:00' (HH:MM) default
      CORE_APP_ID = 'default'
      CORE_ROLLOUT_FORCE_DAILY = '0' (se '1' esegue ogni giorno per test)
    """
    supabase_url = os.environ.get("SUPABASE_URL")
    service_key = os.environ.get("SUPABASE_SERVICE_KEY")
    if not supabase_url or not service_key:
        return

    app_id = os.environ.get("CORE_APP_ID", "default")
    time_str = os.environ.get("CORE_ROLLOUT_TIME_UTC", "03:00")
    force_daily = (os.environ.get("CORE_ROLLOUT_FORCE_DAILY", "0").lower() in ("1", "true", "yes"))

    # Parse HH:MM
    try:
        hh, mm = [int(x) for x in time_str.split(":")]
        target_hour, target_minute = hh, mm
    except Exception:
        target_hour, target_minute = 3, 0

    while True:
        now = datetime.now(timezone.utc)
        today_target = now.replace(hour=target_hour, minute=target_minute, second=0, microsecond=0)
        if today_target <= now:
            # programma per domani
            today_target = today_target + timedelta(days=1)
        await asyncio.sleep(max(1.0, (today_target - now).total_seconds()))

        # È arrivata l'ora del controllo
        try:
            # Condizione di esecuzione: primo giorno del mese o force_daily per test
            now2 = datetime.now(timezone.utc)
            is_first_day = now2.day == 1
            if not (is_first_day or force_daily):
                continue

            # Evita doppi run controllando se c'è già un run nel mese
            if not force_daily and await _has_run_this_month(supabase_url, service_key):
                continue

            from app.services.credits_supabase import SupabaseCreditsLedger
            ledger = SupabaseCreditsLedger()
            result = await ledger.rollout_monthly_credits(app_id=app_id, dry_run=False)
            # Log semplice a console
            print(f"[rollout] executed at {now2.isoformat()} → success={result.get('success')} processed={result.get('users_processed')} total={result.get('total_credits_accredited')}")
        except Exception as e:
            print(f"[rollout] error: {e}")


@app.on_event("startup")
async def _startup_tasks() -> None:
    if os.environ.get("CORE_ENABLE_ROLLOUT_SCHEDULER", "0").lower() in ("1", "true", "yes"):
        asyncio.create_task(_rollout_scheduler_loop())
