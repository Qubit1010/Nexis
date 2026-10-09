-- Prospect Demo Kit schema (idempotent). Applied via scripts/setup_db.py through the
-- Supabase Management API. RLS on with no policies: only the service role (server side) reads/writes.

create table if not exists demo_businesses (
  slug        text primary key,
  token       text not null,
  code        text unique not null,           -- short code carried in the WhatsApp deep link
  sector      text not null,                  -- healthcare | food | education
  name        text not null,
  profile     jsonb not null,                 -- facts (from Maps) + sector samples (labelled)
  xray        jsonb,                          -- review analysis
  site        jsonb,                          -- mini-site + draft posts
  roi         jsonb,                          -- calculator defaults
  health      jsonb,                          -- digital health check scores
  created_at  timestamptz not null default now(),
  expires_at  timestamptz not null
);

create table if not exists demo_conversations (
  id          uuid primary key default gen_random_uuid(),
  slug        text not null references demo_businesses(slug) on delete cascade,
  channel     text not null,                  -- web | whatsapp
  visitor     text not null,                  -- random browser id, or sha256 of the WhatsApp number
  stage       text,
  summary     text,
  answers     jsonb,
  action      jsonb,
  handoff     boolean not null default false,
  created_at  timestamptz not null default now(),
  last_at     timestamptz not null default now()
);
create unique index if not exists demo_conv_unique on demo_conversations (slug, channel, visitor);
create index if not exists demo_conv_visitor on demo_conversations (visitor, last_at desc);

create table if not exists demo_messages (
  id              bigserial primary key,
  conversation_id uuid not null references demo_conversations(id) on delete cascade,
  role            text not null,              -- customer | business
  content         text not null,
  source          text,                       -- claude | scripted | fallback
  latency_ms      int,
  at              timestamptz not null default now()
);
create index if not exists demo_msg_conv on demo_messages (conversation_id, id);

create table if not exists demo_events (
  id      bigserial primary key,
  slug    text,
  kind    text not null,                      -- view | chat_start | booking | handoff | expired_hit
  detail  jsonb,
  at      timestamptz not null default now()
);
create index if not exists demo_events_slug on demo_events (slug, at desc);

alter table demo_businesses    enable row level security;
alter table demo_conversations enable row level security;
alter table demo_messages      enable row level security;
alter table demo_events        enable row level security;
