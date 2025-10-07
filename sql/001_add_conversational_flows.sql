-- Migration: Aggiunge supporto per flow conversazionali
-- Esegui questo file su database esistenti per aggiungere la funzionalità sessioni

-- Aggiungi colonna is_conversational a flow_configs
ALTER TABLE public.flow_configs 
ADD COLUMN IF NOT EXISTS is_conversational boolean DEFAULT false;

-- Aggiungi colonna per metadata aggiuntivi (future estensioni)
ALTER TABLE public.flow_configs 
ADD COLUMN IF NOT EXISTS metadata jsonb DEFAULT '{}'::jsonb;

-- Crea tabella per tracking delle sessioni (opzionale, per analytics)
CREATE TABLE IF NOT EXISTS public.flow_sessions (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  session_id text NOT NULL,
  user_id uuid REFERENCES public.profiles(id) ON DELETE CASCADE,
  app_id text NOT NULL,
  flow_key text NOT NULL,
  flow_id text NOT NULL,
  first_message_at timestamp with time zone DEFAULT now(),
  last_message_at timestamp with time zone DEFAULT now(),
  message_count integer DEFAULT 1,
  metadata jsonb DEFAULT '{}'::jsonb,
  created_at timestamp with time zone DEFAULT now(),
  updated_at timestamp with time zone DEFAULT now(),
  UNIQUE(session_id, user_id)
);

-- Indici per performance
CREATE INDEX IF NOT EXISTS idx_flow_sessions_user_id ON public.flow_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_flow_sessions_session_id ON public.flow_sessions(session_id);
CREATE INDEX IF NOT EXISTS idx_flow_sessions_app_flow ON public.flow_sessions(app_id, flow_key);
CREATE INDEX IF NOT EXISTS idx_flow_sessions_last_message ON public.flow_sessions(last_message_at DESC);

-- RLS per flow_sessions (solo il proprietario può vedere le proprie sessioni)
ALTER TABLE public.flow_sessions ENABLE ROW LEVEL SECURITY;

DO $$ 
BEGIN
  BEGIN
    CREATE POLICY flow_sessions_select_self ON public.flow_sessions
      FOR SELECT USING (user_id = auth.uid());
  EXCEPTION WHEN duplicate_object THEN NULL;
  END;
END $$;

-- Commenti per documentazione
COMMENT ON COLUMN public.flow_configs.is_conversational IS 
  'Se true, il flow mantiene la conversazione tra chiamate successive usando session_id';

COMMENT ON TABLE public.flow_sessions IS 
  'Tracking delle sessioni conversazionali per analytics e debugging';
