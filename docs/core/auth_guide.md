## Auth (Supabase) – Guida rapida per app client

Flow Starter non reinventa l'auth: usa Supabase Auth. Per semplificare gli sviluppatori, esponiamo degli endpoint proxy sotto `/core/v1/auth/*` e una mini libreria nel client skeleton.

### Variabili richieste
- `SUPABASE_URL`
- `SUPABASE_ANON_KEY`

### Endpoints disponibili
- `POST /core/v1/auth/signup` – body: `{ email, password, redirect_to? }`
- `POST /core/v1/auth/login` – body: `{ email, password }` → `{ access_token, refresh_token, ... }`
- `POST /core/v1/auth/refresh` – body: `{ refresh_token }`
- `POST /core/v1/auth/logout` – header: `Authorization: Bearer <access_token>`
- `GET /core/v1/auth/user` – header: `Authorization: Bearer <access_token>`

### Esempi

```bash
# Login
curl -s -X POST "$API/core/v1/auth/login" \
  -H 'Content-Type: application/json' \
  -d '{"email":"user@example.com","password":"Passw0rd!"}'
```

```bash
# Get user
curl -s "$API/core/v1/auth/user" \
  -H "Authorization: Bearer $ACCESS_TOKEN"
```

### Client JavaScript (client_skeleton)
Nel file `client_skeleton/lib/flowStarter.js` sono disponibili:
- `signupAuth(apiBase, email, password, redirectTo)`
- `loginAuth(apiBase, email, password)`
- `refreshAuth(apiBase, refreshToken)`
- `logoutAuth(apiBase, accessToken)`
- `getUserAuth(apiBase, accessToken)`

Esempio Next.js:
```js
import { loginAuth, getUserAuth } from '@/lib/flowStarter';

const API = process.env.NEXT_PUBLIC_FLOW_STARTER_API;

const { access_token } = await loginAuth(API, email, password);
const me = await getUserAuth(API, access_token);
```

### Note
- Gli endpoint sono thin proxies verso Supabase Auth. È possibile usare direttamente l’SDK Supabase se preferisci.
- Per sviluppo locale, metti `SUPABASE_URL`, `SUPABASE_ANON_KEY` nel `.env` e riavvia.

