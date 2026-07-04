-- Sales Playbook conversation memory. Run ONCE in the Supabase SQL Editor.
-- One row per prospect conversation, keyed by (channel, identity).
-- RLS stays enabled with no anon policies: only the service-role key
-- (server-side in convo.py and the dashboard API routes) can touch it.

create table if not exists conversations (
  id bigint generated always as identity primary key,
  channel text not null,               -- linkedin | instagram | facebook
  identity text not null,              -- normalized: LI /in/ slug, IG @handle, FB slug/id
  name text default '',
  profile text default '',             -- one-line profile used in prompts
  stage text default 'qualify',        -- qualify|label|deepen|proof|objection|ask|booked|dead
  exchange_count int default 0,        -- number of PROSPECT replies in thread
  meeting_status text default 'none',  -- none|asked|booked|declined|ghosted
  last_contact text default '',        -- YYYY-MM-DD
  thread text default '',              -- full "[Me]: / [Them]:" transcript; latest paste wins
  last_draft text default '',
  updated_at timestamptz not null default now(),
  unique (channel, identity)
);

alter table conversations enable row level security;
