import os
import time
import signal
import subprocess
from typing import Optional

import httpx
from dotenv import load_dotenv


def wait_for_health(base_url: str, timeout: float = 30.0) -> bool:
    start = time.time()
    while time.time() - start < timeout:
        try:
            r = httpx.get(f"{base_url}/health", timeout=2.0)
            if r.status_code == 200:
                return True
        except Exception:
            pass
        time.sleep(0.5)
    return False


def main() -> int:
    # Carica .env dalla root di flow_starter
    load_dotenv()

    # Imposta variabili per il test
    os.environ.setdefault("CORE_BASE_URL", "http://127.0.0.1:5050/core/v1")

    # OPZ: usa SUPABASE_URL e SUPABASE_SERVICE_KEY da .env se non settate
    supabase_url = os.environ.get("SUPABASE_URL")
    supabase_key = os.environ.get("SUPABASE_SERVICE_KEY")
    if not supabase_url or not supabase_key:
        print("[warn] SUPABASE_URL o SUPABASE_SERVICE_KEY non impostati; il test fallirà.")

    # Avvia Uvicorn (Core)
    env = os.environ.copy()
    uvicorn_cmd = [
        "python",
        "-m",
        "uvicorn",
        "app.main:app",
        "--host",
        "127.0.0.1",
        "--port",
        env.get("CORE_PORT", "5050"),
    ]

    print("[info] Avvio Core API con Uvicorn...")
    proc: Optional[subprocess.Popen] = None
    try:
        proc = subprocess.Popen(uvicorn_cmd, cwd=os.path.dirname(os.path.dirname(__file__)), env=env)
        ok = wait_for_health("http://127.0.0.1:5050")
        if not ok:
            print("[error] Core non raggiungibile su /health entro il timeout")
            return 1

        # Esegui pytest sul test specifico
        print("[info] Eseguo pytest: tests/e2e_affordability_and_debit.py")
        result = subprocess.run(
            ["python", "-m", "pytest", "-q", "tests/e2e_affordability_and_debit.py"],
            cwd=os.path.dirname(os.path.dirname(__file__)),
            env=env,
        )
        return result.returncode

    finally:
        if proc and proc.poll() is None:
            print("[info] Arresto Core API...")
            try:
                if os.name == "nt":
                    proc.terminate()
                else:
                    os.kill(proc.pid, signal.SIGTERM)
            except Exception:
                pass


if __name__ == "__main__":
    raise SystemExit(main())


