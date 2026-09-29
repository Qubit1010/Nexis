-- Proposal views and signatures. Supabase project jmfbbwxdguvbtflnwmos (shared with sales-playbook).
-- RLS is on with no policies: only the service role (the Vercel function, local scripts) can read or write.
create table if not exists proposal_events (
  id bigint generated always as identity primary key,
  proposal_id text not null,
  version_hash text not null,
  event_type text not null check (event_type in ('view', 'sign')),
  signer_name text,
  signer_email text,
  signer_title text,
  option_id text,
  option_name text,
  amount_due numeric,
  currency text,
  consent_text text,
  signature_png text,
  ip text,
  user_agent text,
  created_at timestamptz not null default now()
);

create index if not exists proposal_events_lookup on proposal_events (proposal_id, event_type);

-- One signature per proposal id, ever. A revised deal is a new proposal id.
create unique index if not exists proposal_events_one_signature on proposal_events (proposal_id) where event_type = 'sign';

alter table proposal_events enable row level security;
