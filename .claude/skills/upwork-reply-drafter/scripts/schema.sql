-- Upwork Reply Drafter conversation memory. Run ONCE in the Supabase SQL Editor.
-- One row per Upwork client conversation, keyed by identity (client slug / Upwork
-- profile or job URL). Separate from the sales-playbook `conversations` table because
-- Upwork stages + fields differ. RLS on, no anon policy: only the service-role key
-- (server-side in the dashboard API routes) can touch it.

create table if not exists upwork_conversations (
  id bigint generated always as identity primary key,
  identity text not null,              -- normalized: client slug, Upwork profile/job URL, or hashed name
  client_name text default '',
  job_title text default '',
  job_type text default '',            -- Web Dev | Marketing Automation | AI Services
  profile text default '',             -- one-line client/job profile used in prompts
  situation text default 'pre_hire',   -- pre_hire | active | closeout | reactivation
  stage text default 'pre_hire',       -- pre_hire | negotiating | active | delivered | reviewed | reactivation | dead
  exchange_count int default 0,        -- number of CLIENT replies in the thread
  thread text default '',              -- full "[Me]: / [Them]:" transcript, latest paste wins
  last_draft text default '',
  last_contact text default '',        -- YYYY-MM-DD
  updated_at timestamptz not null default now(),
  unique (identity)
);

alter table upwork_conversations enable row level security;
