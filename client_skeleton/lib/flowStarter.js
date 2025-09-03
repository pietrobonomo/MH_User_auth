export async function runAI(userToken, flowKey, inputData, appId = null) {
  const apiBase = (process.env.NEXT_PUBLIC_FLOW_STARTER_API || '').replace(/\/$/, '');
  if (!apiBase) throw new Error('Missing NEXT_PUBLIC_FLOW_STARTER_API');

  const headers = {
    'Authorization': `Bearer ${userToken}`,
    'Content-Type': 'application/json'
  };
  if (appId) headers['X-App-Id'] = appId; // solo per multi-tenant

  const response = await fetch(`${apiBase}/providers/flowise/execute`, {
    method: 'POST',
    headers,
    body: JSON.stringify({ flow_key: flowKey, data: inputData })
  });

  if (response.status === 402) {
    const err = await response.json();
    throw new Error(`CREDITS_NEEDED:${err.shortage ?? ''}`);
  }

  if (!response.ok) {
    const text = await response.text();
    throw new Error(`Core error ${response.status}: ${text}`);
  }

  const data = await response.json();
  return data.result;
}

// Auth helpers (proxy Supabase via Flow Starter)
export async function signupAuth(apiBase, email, password, redirectTo) {
  apiBase = (apiBase || process.env.NEXT_PUBLIC_FLOW_STARTER_API || '').replace(/\/$/, '');
  const res = await fetch(`${apiBase}/auth/signup`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password, redirect_to: redirectTo })
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function loginAuth(apiBase, email, password) {
  apiBase = (apiBase || process.env.NEXT_PUBLIC_FLOW_STARTER_API || '').replace(/\/$/, '');
  const res = await fetch(`${apiBase}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password })
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json(); // { access_token, refresh_token, ... }
}

export async function refreshAuth(apiBase, refreshToken) {
  apiBase = (apiBase || process.env.NEXT_PUBLIC_FLOW_STARTER_API || '').replace(/\/$/, '');
  const res = await fetch(`${apiBase}/auth/refresh`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ refresh_token: refreshToken })
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function logoutAuth(apiBase, accessToken) {
  apiBase = (apiBase || process.env.NEXT_PUBLIC_FLOW_STARTER_API || '').replace(/\/$/, '');
  const res = await fetch(`${apiBase}/auth/logout`, {
    method: 'POST',
    headers: { 'Authorization': `Bearer ${accessToken}` }
  });
  if (!res.ok) throw new Error(await res.text());
  return { status: 'ok' };
}

export async function getUserAuth(apiBase, accessToken) {
  apiBase = (apiBase || process.env.NEXT_PUBLIC_FLOW_STARTER_API || '').replace(/\/$/, '');
  const res = await fetch(`${apiBase}/auth/user`, {
    headers: { 'Authorization': `Bearer ${accessToken}` }
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}
