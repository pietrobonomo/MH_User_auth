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
