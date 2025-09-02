# Flow Starter - App Skeleton (Client)

Questo è uno scheletro client minimo per consumare le API di Flow Starter da una web app (Next.js / SvelteKit / Vite).

## Variabili d'ambiente (client)

Crea un `.env.local` (o equivalente) con:

- NEXT_PUBLIC_FLOW_STARTER_API = Base API del Core (es: https://your-core.com/core/v1)
- NEXT_PUBLIC_SUPABASE_URL = URL del progetto Supabase
- NEXT_PUBLIC_SUPABASE_ANON_KEY = Anon key di Supabase (solo lato client)

Esempio `.env.local`:
```
NEXT_PUBLIC_FLOW_STARTER_API=https://your-core.com/core/v1
NEXT_PUBLIC_SUPABASE_URL=https://xxx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

## Esempio d'uso (framework-agnostico)

Funzione JS per eseguire un flow via Flow Starter gestendo l'errore 402 (crediti):
```
export async function runAI(userToken, flowKey, inputData, appId = null) {
  const API = (process.env.NEXT_PUBLIC_FLOW_STARTER_API || '').replace(/\/$/, '');
  const headers = {
    'Authorization': `Bearer ${userToken}`,
    'Content-Type': 'application/json'
  };
  if (appId) headers['X-App-Id'] = appId; // solo per multi-tenant

  const resp = await fetch(`${API}/providers/flowise/execute`, {
    method: 'POST',
    headers,
    body: JSON.stringify({ flow_key: flowKey, data: inputData })
  });

  if (resp.status === 402) {
    const err = await resp.json();
    throw new Error(`CREDITS_NEEDED:${err.shortage ?? ''}`);
  }

  const data = await resp.json();
  return data.result; // { text, metadata, ... }
}
```

## Next.js (Quick start)

1) Crea app:
```
npx create-next-app@latest my-app
cd my-app
```
2) Copia la funzione `runAI` in `lib/flowStarter.js` e configura `.env.local`.
3) Usa la funzione in una page o componente client-side.

Nota: l'autenticazione utente (ottenere `userToken`) si fa via Supabase Auth nel client e si passa il token JWT al Core.

## SvelteKit/Vite
Usa la stessa funzione `runAI` in un file utility e importala nei componenti. Le env pubbliche saranno accessibili come `import.meta.env.VITE_*` (rinomina le chiavi di conseguenza).

## Deploy su Railway (client)

- Crea un nuovo progetto Railway per il client o aggiungi un servizio static/Next.
- Imposta le env pubbliche del client (NEXT_PUBLIC_*).
- Punta `NEXT_PUBLIC_FLOW_STARTER_API` all'istanza Core deployata.

## Flowise

Il Core dialoga con Flowise. Puoi ospitare Flowise dal tuo fork GitHub o usare l'immagine Docker ufficiale.
- Fork: pietrobonomo/Flowise → vedi repo: https://github.com/pietrobonomo/Flowise
- Immagine: flowiseai/flowise:<version>

## Checklist di progetto

- [ ] Core su Railway con env configurate
- [ ] Flowise raggiungibile e FLOWISE_BASE_URL impostata nel Core
- [ ] Supabase: URL + anon key nel client; service key nel Core
- [ ] Client deployato con NEXT_PUBLIC_FLOW_STARTER_API puntato al Core
