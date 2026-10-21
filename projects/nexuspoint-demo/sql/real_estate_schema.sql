-- Synthetic real-estate workspaces: buyer portal, agent pipeline, manager view.
-- Additive only: new demo_re_* tables and one function. Every mutation takes one business-scoped
-- advisory lock; site visits also have a per-agent exclusion constraint, so two buyers can never
-- hold the same agent at the same time even if the lock were bypassed.
create extension if not exists btree_gist with schema public;

create table if not exists demo_re_settings (
 slug text primary key references demo_businesses(slug),
 open_min int not null default 600, close_min int not null default 1080,
 visit_minutes int not null default 60, seeded boolean not null default false,
 check(open_min>=0 and close_min<=1440 and close_min-open_min>=60), check(visit_minutes in (30,45,60,90))
);
create table if not exists demo_re_agents (
 id uuid primary key default gen_random_uuid(), slug text not null references demo_businesses(slug),
 name text not null, name_ur text not null default '', title text not null default 'Sales agent',
 areas text not null default '', active boolean not null default true, created_at timestamptz not null default now()
);
create table if not exists demo_re_listings (
 id uuid primary key default gen_random_uuid(), slug text not null references demo_businesses(slug),
 code text not null, title text not null, title_ur text not null default '',
 kind text not null check(kind in ('plot','house','apartment','commercial','file')),
 society text not null, society_ur text not null default '', block text not null default '',
 size_value numeric not null check(size_value>0), size_unit text not null check(size_unit in ('marla','kanal','sqft')),
 beds int, baths int, price bigint not null check(price between 100000 and 100000000000),
 status text not null default 'available' check(status in ('available','reserved','sold')),
 features text[] not null default '{}', description text not null default '', description_ur text not null default '',
 art text not null default 'plot', created_at timestamptz not null default now(), unique(slug,code)
);
create table if not exists demo_re_buyers (
 id uuid primary key default gen_random_uuid(), slug text not null references demo_businesses(slug),
 visitor text not null, name text not null default 'Demo buyer', overseas boolean not null default false,
 country text not null default '', created_at timestamptz not null default now(), unique(slug,visitor)
);
create table if not exists demo_re_leads (
 id uuid primary key default gen_random_uuid(), slug text not null references demo_businesses(slug),
 buyer_id uuid not null references demo_re_buyers(id),
 source text not null check(source in ('chat','website','facebook','zameen','walk_in','referral','phone')),
 stage text not null default 'new' check(stage in ('new','qualified','visit_booked','negotiating','won','lost')),
 budget bigint check(budget is null or budget between 100000 and 100000000000),
 area text not null default '', size text not null default '', kind text not null default '', timeline text not null default '',
 overseas boolean, country text not null default '', listing_id uuid references demo_re_listings(id),
 agent_id uuid references demo_re_agents(id), conversation_id uuid,
 summary text not null default '', notes text not null default '', lost_reason text not null default '',
 history jsonb not null default '[]', request_id text not null, fingerprint text not null,
 created_at timestamptz not null default now(), first_reply_at timestamptz, updated_at timestamptz not null default now(),
 unique(slug,request_id)
);
create table if not exists demo_re_visits (
 id uuid primary key default gen_random_uuid(), slug text not null references demo_businesses(slug),
 lead_id uuid not null references demo_re_leads(id), buyer_id uuid not null references demo_re_buyers(id),
 agent_id uuid not null references demo_re_agents(id), listing_id uuid references demo_re_listings(id),
 starts_at timestamptz not null, ends_at timestamptz not null,
 status text not null default 'confirmed' check(status in ('confirmed','completed','cancelled','no_show')),
 notes text not null default '', source text not null, request_id text not null, fingerprint text not null,
 created_at timestamptz not null default now(), unique(slug,request_id),
 exclude using gist(agent_id with =, tstzrange(starts_at,ends_at,'[)') with &&) where (status='confirmed')
);
create table if not exists demo_re_archives (
 id uuid primary key default gen_random_uuid(), slug text not null references demo_businesses(slug),
 data jsonb not null, archived_at timestamptz not null default now()
);
create index if not exists demo_re_leads_scope on demo_re_leads(slug,stage,updated_at desc);
create index if not exists demo_re_visits_scope on demo_re_visits(slug,starts_at);

create or replace function demo_re_action(p_slug text,p_visitor text,p_role text,p_action text,p_data jsonb default '{}')
returns jsonb language plpgsql security definer set search_path=public as $$
declare b demo_businesses; s demo_re_settings; c demo_re_buyers; l demo_re_leads; v demo_re_visits; ag demo_re_agents;
 li demo_re_listings; ln jsonb; n int; start_time timestamptz; dur interval; minute_value int; target text;
 request_key text; digest text; received timestamptz; agent_ids uuid[]; listing_ids uuid[]; row_id uuid;
begin
 perform pg_advisory_xact_lock(hashtext('real-estate:'||p_slug));
 select * into b from demo_businesses where slug=p_slug and sector='real-estate';
 if not found then raise exception 'INVALID: Unknown property demo'; end if;
 if b.expires_at<=now() and p_action<>'reset' then raise exception 'EXPIRED: This preview has expired'; end if;
 if p_role not in ('buyer','agent','manager','system') then raise exception 'INVALID: Invalid demo role'; end if;

 if p_action='reset' then
  if p_role<>'system' then raise exception 'INVALID: Reset is an owner action'; end if;
  insert into demo_re_archives(slug,data) select p_slug,jsonb_build_object(
   'settings',(select to_jsonb(x) from demo_re_settings x where slug=p_slug),
   'agents',(select jsonb_agg(x) from demo_re_agents x where slug=p_slug),'listings',(select jsonb_agg(x) from demo_re_listings x where slug=p_slug),
   'buyers',(select jsonb_agg(x) from demo_re_buyers x where slug=p_slug),'leads',(select jsonb_agg(x) from demo_re_leads x where slug=p_slug),
   'visits',(select jsonb_agg(x) from demo_re_visits x where slug=p_slug),
   'conversations',(select jsonb_agg(x) from demo_conversations x where slug=p_slug),
   'messages',(select jsonb_agg(x) from demo_messages x where conversation_id in(select id from demo_conversations where slug=p_slug)));
  delete from demo_re_visits where slug=p_slug; delete from demo_re_leads where slug=p_slug;
  delete from demo_re_buyers where slug=p_slug; delete from demo_re_listings where slug=p_slug;
  delete from demo_re_agents where slug=p_slug; delete from demo_re_settings where slug=p_slug;
  delete from demo_conversations where slug=p_slug;
  return '{"ok":true}';
 end if;

 insert into demo_re_settings(slug) values(p_slug) on conflict do nothing;
 select * into s from demo_re_settings where slug=p_slug;
 dur:=make_interval(mins=>s.visit_minutes);

 if p_action='seed' then
  if p_role<>'system' then raise exception 'INVALID: Seed is an owner action'; end if;
  if s.seeded then return '{"ok":true}'; end if;
  agent_ids:='{}'; listing_ids:='{}';
  for ln in select value from jsonb_array_elements(p_data->'agents') loop
   insert into demo_re_agents(slug,name,name_ur,title,areas) values(p_slug,ln->>'name',coalesce(ln->>'name_ur',''),coalesce(ln->>'title','Sales agent'),coalesce(ln->>'areas',''))
    returning id into row_id; agent_ids:=agent_ids||row_id;
  end loop;
  for ln in select value from jsonb_array_elements(p_data->'listings') loop
   insert into demo_re_listings(slug,code,title,title_ur,kind,society,society_ur,block,size_value,size_unit,beds,baths,price,status,features,description,description_ur,art)
    values(p_slug,ln->>'code',ln->>'title',coalesce(ln->>'title_ur',''),ln->>'kind',ln->>'society',coalesce(ln->>'society_ur',''),coalesce(ln->>'block',''),
     (ln->>'size_value')::numeric,ln->>'size_unit',(ln->>'beds')::int,(ln->>'baths')::int,(ln->>'price')::bigint,coalesce(ln->>'status','available'),
     array(select jsonb_array_elements_text(coalesce(ln->'features','[]'))),coalesce(ln->>'description',''),coalesce(ln->>'description_ur',''),coalesce(ln->>'art','plot'))
    returning id into row_id; listing_ids:=listing_ids||row_id;
  end loop;
  n:=0;
  for ln in select value from jsonb_array_elements(coalesce(p_data->'leads','[]')) loop
   n:=n+1;
   insert into demo_re_buyers(slug,visitor,name,overseas,country) values(p_slug,'sample-buyer-'||n,ln->>'name',coalesce((ln->>'overseas')::boolean,false),coalesce(ln->>'country',''))
    returning * into c;
   received:=now()-make_interval(hours=>coalesce((ln->>'age_hours')::int,1));
   insert into demo_re_leads(slug,buyer_id,source,stage,budget,area,size,kind,timeline,overseas,country,listing_id,agent_id,summary,notes,lost_reason,history,request_id,fingerprint,created_at,first_reply_at,updated_at)
    values(p_slug,c.id,ln->>'source',ln->>'stage',(ln->>'budget')::bigint,coalesce(ln->>'area',''),coalesce(ln->>'size',''),coalesce(ln->>'kind',''),coalesce(ln->>'timeline',''),
     (ln->>'overseas')::boolean,coalesce(ln->>'country',''),
     case when ln ? 'listing' then listing_ids[(ln->>'listing')::int+1] end,
     case when ln ? 'agent' then agent_ids[(ln->>'agent')::int+1] end,
     coalesce(ln->>'summary',''),coalesce(ln->>'notes',''),coalesce(ln->>'lost_reason',''),
     jsonb_build_array(jsonb_build_object('kind','created','text','Sample lead from '||(ln->>'source'),'at',received)),
     'sample-lead-'||n,'sample',received,
     case when ln ? 'reply_seconds' then received+make_interval(secs=>(ln->>'reply_seconds')::int) end,received)
    returning * into l;
   if ln ? 'visit_day' and l.agent_id is not null then
    start_time:=(((now() at time zone 'Asia/Karachi')::date+(ln->>'visit_day')::int)::text||' '||lpad(coalesce(ln->>'visit_hour','11'),2,'0')||':00:00+05')::timestamptz;
    -- negative days are past visits that already happened (completed); future ones are confirmed
    if (ln->>'visit_day')::int<0 or (start_time>now() and start_time+dur<=b.expires_at) then
     insert into demo_re_visits(slug,lead_id,buyer_id,agent_id,listing_id,starts_at,ends_at,status,notes,source,request_id,fingerprint)
      values(p_slug,l.id,c.id,l.agent_id,l.listing_id,start_time,start_time+dur,case when (ln->>'visit_day')::int<0 then 'completed' else 'confirmed' end,
       'Sample site visit','sample','sample-visit-'||n,'sample');
    end if;
   end if;
  end loop;
  update demo_re_settings set seeded=true where slug=p_slug;
  return '{"ok":true}';
 end if;

 if p_visitor !~ '^[a-zA-Z0-9_-]{8,64}$' then raise exception 'INVALID: Invalid demo session'; end if;
 insert into demo_re_buyers(slug,visitor) values(p_slug,p_visitor) on conflict do nothing;
 select * into c from demo_re_buyers where slug=p_slug and visitor=p_visitor;

 if p_action='buyer' then
  update demo_re_buyers set
   name=case when length(coalesce(p_data->>'name','')) between 1 and 80 then p_data->>'name' else name end,
   overseas=coalesce((p_data->>'overseas')::boolean,overseas),
   country=case when p_data ? 'country' then left(coalesce(p_data->>'country',''),60) else country end
   where id=c.id returning * into c;
  return to_jsonb(c);
 end if;

 -- Chat qualification: one lead per conversation, fields only ever filled in, never invented.
 if p_action='qualify' or p_action='enquiry' then
  if p_role<>'buyer' then raise exception 'INVALID: Buyers create enquiries'; end if;
  request_key:=p_data->>'requestId';
  if length(coalesce(request_key,'')) not between 8 and 100 then raise exception 'INVALID: Retry identifier required'; end if;
  if (p_data->>'budget') is not null and (p_data->>'budget')::bigint not between 100000 and 100000000000 then raise exception 'INVALID: Budget out of range'; end if;
  if p_data ? 'listingId' then
   select * into li from demo_re_listings where slug=p_slug and id=(p_data->>'listingId')::uuid;
   if not found then raise exception 'INVALID: Unknown listing'; end if;
  end if;
  if length(coalesce(p_data->>'name','')) between 1 and 80 then update demo_re_buyers set name=p_data->>'name' where id=c.id returning * into c; end if;
  if (p_data->>'overseas') is not null then update demo_re_buyers set overseas=(p_data->>'overseas')::boolean,country=left(coalesce(p_data->>'country',country),60) where id=c.id returning * into c; end if;
  select * into l from demo_re_leads where slug=p_slug and request_id=request_key;
  if p_action='enquiry' then
   digest:=md5((p_data-'receivedAt')::text);
   if found then
    if l.buyer_id<>c.id or l.fingerprint<>digest then raise exception 'CONFLICT: Retry identifier already used for a different enquiry'; end if;
    return to_jsonb(l);
   end if;
  elsif found and l.buyer_id<>c.id then raise exception 'CONFLICT: Retry identifier belongs to another buyer';
  end if;
  received:=least(now(),greatest(now()-interval '10 minutes',coalesce((p_data->>'receivedAt')::timestamptz,now())));
  if l.id is null then
   insert into demo_re_leads(slug,buyer_id,source,request_id,fingerprint,created_at,conversation_id,history)
    values(p_slug,c.id,case when p_action='enquiry' then 'website' else 'chat' end,request_key,
     case when p_action='enquiry' then md5((p_data-'receivedAt')::text) else 'chat' end,received,(p_data->>'conversationId')::uuid,
     jsonb_build_array(jsonb_build_object('kind','created','text',case when p_action='enquiry' then 'Website lead form' else 'WhatsApp assistant conversation' end,'at',received)))
    returning * into l;
   insert into demo_events(slug,kind,detail) values(p_slug,'re_lead',jsonb_build_object('lead_id',l.id,'source',l.source));
  end if;
  update demo_re_leads set
   budget=coalesce((p_data->>'budget')::bigint,budget),
   area=coalesce(nullif(left(p_data->>'area',80),''),area), size=coalesce(nullif(left(p_data->>'size',40),''),size),
   kind=coalesce(nullif(left(p_data->>'kind',20),''),kind), timeline=coalesce(nullif(left(p_data->>'timeline',60),''),timeline),
   overseas=coalesce((p_data->>'overseas')::boolean,overseas), country=coalesce(nullif(left(p_data->>'country',60),''),country),
   listing_id=coalesce(li.id,listing_id), summary=coalesce(nullif(left(p_data->>'summary',600),''),summary),
   notes=case when p_action='enquiry' and length(coalesce(p_data->>'message',''))>0 then left(p_data->>'message',500) else notes end,
   first_reply_at=coalesce(first_reply_at,now()), updated_at=now()
   where id=l.id returning * into l;
  if l.stage='new' and l.budget is not null and l.area<>'' and l.size<>'' then
   update demo_re_leads set stage='qualified',history=history||jsonb_build_array(jsonb_build_object('kind','stage','text','qualified','at',now())) where id=l.id returning * into l;
  end if;
  if (p_data->>'handoff')::boolean is true then
   update demo_re_leads set history=history||jsonb_build_array(jsonb_build_object('kind','handoff','text',left(coalesce(p_data->>'handoffReason','Agent requested'),200),'at',now())) where id=l.id returning * into l;
  end if;
  return to_jsonb(l);
 end if;

 if p_action in ('reserve','visit') then
  if p_action='visit' then
   select * into v from demo_re_visits where slug=p_slug and id=(p_data->>'id')::uuid;
   if not found or (p_role='buyer' and v.buyer_id<>c.id) then raise exception 'NOT_FOUND: Visit not found'; end if;
   select * into l from demo_re_leads where id=v.lead_id;
   if not(p_data ? 'start') then
    target:=p_data->>'status';
    if p_role='buyer' and target<>'cancelled' then raise exception 'INVALID: Buyers can cancel or reschedule'; end if;
    if target not in ('completed','cancelled','no_show') then raise exception 'INVALID: Invalid visit status'; end if;
    if v.status=target then return to_jsonb(v); end if;
    if v.status<>'confirmed' then raise exception 'CONFLICT: Only confirmed visits can change'; end if;
    if target in ('completed','no_show') and v.starts_at>now() then raise exception 'INVALID: Mark a visit after it starts'; end if;
    update demo_re_visits set status=target where id=v.id returning * into v;
    if target in ('cancelled','no_show') and l.stage='visit_booked' and not exists(select 1 from demo_re_visits x where x.lead_id=l.id and x.status='confirmed') then
     update demo_re_leads set stage='qualified',updated_at=now() where id=l.id;
    end if;
    update demo_re_leads set history=history||jsonb_build_array(jsonb_build_object('kind','visit','text','Visit '||target,'at',now())),updated_at=now() where id=l.id;
    insert into demo_events(slug,kind,detail) values(p_slug,'re_visit_'||target,jsonb_build_object('visit_id',v.id,'simulated_notice',true));
    return to_jsonb(v);
   end if;
   if v.status<>'confirmed' then raise exception 'CONFLICT: Only confirmed visits can move'; end if;
  else
   request_key:=p_data->>'requestId'; digest:=md5(p_data::text);
   if length(coalesce(request_key,'')) not between 8 and 100 then raise exception 'INVALID: Retry identifier required'; end if;
   select * into v from demo_re_visits where slug=p_slug and request_id=request_key;
   if found then
    if v.fingerprint<>digest or (p_role='buyer' and v.buyer_id<>c.id) then raise exception 'CONFLICT: Retry identifier already used'; end if;
    return to_jsonb(v);
   end if;
   if p_data ? 'leadId' then
    select * into l from demo_re_leads where slug=p_slug and id=(p_data->>'leadId')::uuid;
    if not found or (p_role='buyer' and l.buyer_id<>c.id) then raise exception 'NOT_FOUND: Lead not found'; end if;
   elsif p_role='buyer' then
    select * into l from demo_re_leads where slug=p_slug and buyer_id=c.id and stage not in ('won','lost') order by updated_at desc limit 1;
    if not found then
     insert into demo_re_leads(slug,buyer_id,source,request_id,fingerprint,first_reply_at,history)
      values(p_slug,c.id,case when p_data->>'source'='chat' then 'chat' else 'website' end,'visit-lead-'||request_key,'visit',now(),
       jsonb_build_array(jsonb_build_object('kind','created','text','Site visit request','at',now()))) returning * into l;
     insert into demo_events(slug,kind,detail) values(p_slug,'re_lead',jsonb_build_object('lead_id',l.id,'source',l.source));
    end if;
   else raise exception 'INVALID: Choose a lead for this visit';
   end if;
   if l.stage in ('won','lost') then raise exception 'CONFLICT: Reopen the lead before booking a visit'; end if;
   if p_data ? 'listingId' then
    select * into li from demo_re_listings where slug=p_slug and id=(p_data->>'listingId')::uuid;
    if not found then raise exception 'INVALID: Unknown listing'; end if;
    if li.status='sold' then raise exception 'CONFLICT: This sample listing is sold'; end if;
   end if;
  end if;
  start_time:=(p_data->>'start')::timestamptz;
  minute_value:=extract(hour from start_time at time zone 'Asia/Karachi')::int*60+extract(minute from start_time at time zone 'Asia/Karachi')::int;
  if start_time<=now() or start_time+dur>b.expires_at
   or (start_time at time zone 'Asia/Karachi')::date>(now() at time zone 'Asia/Karachi')::date+13
   or extract(second from start_time)<>0 or minute_value<s.open_min or minute_value+s.visit_minutes>s.close_min
   or (minute_value-s.open_min)%s.visit_minutes<>0 then raise exception 'INVALID: Choose a future site-visit slot within office hours'; end if;
  select a.* into ag from demo_re_agents a where a.slug=p_slug and a.active
   and (not(p_data ? 'agentId') or a.id=(p_data->>'agentId')::uuid)
   and not exists(select 1 from demo_re_visits x where x.agent_id=a.id and x.status='confirmed' and x.id is distinct from v.id
    and x.starts_at<start_time+dur and x.ends_at>start_time)
   order by (a.id=coalesce(v.agent_id,l.agent_id)) desc nulls last,
    (select count(*) from demo_re_visits x where x.agent_id=a.id and x.status='confirmed'), a.name limit 1;
  if not found then raise exception 'CONFLICT: No agent is free at that time. Choose another slot'; end if;
  if p_action='visit' then
   update demo_re_visits set agent_id=ag.id,starts_at=start_time,ends_at=start_time+dur where id=v.id returning * into v;
   update demo_re_leads set history=history||jsonb_build_array(jsonb_build_object('kind','visit','text','Visit moved','at',now())),updated_at=now() where id=l.id;
  else
   insert into demo_re_visits(slug,lead_id,buyer_id,agent_id,listing_id,starts_at,ends_at,notes,source,request_id,fingerprint)
    values(p_slug,l.id,l.buyer_id,ag.id,coalesce(li.id,l.listing_id),start_time,start_time+dur,left(coalesce(p_data->>'notes',''),500),
     case when p_role in ('agent','manager') then 'staff' when p_data->>'source'='chat' then 'chat' else 'portal' end,request_key,digest)
    returning * into v;
   update demo_re_leads set agent_id=coalesce(agent_id,ag.id),listing_id=coalesce(li.id,listing_id),
    stage=case when stage in ('new','qualified') then 'visit_booked' else stage end,
    first_reply_at=coalesce(first_reply_at,now()),updated_at=now(),
    history=history||jsonb_build_array(jsonb_build_object('kind','visit','text','Site visit booked with '||ag.name,'at',now()))
    where id=l.id;
  end if;
  insert into demo_events(slug,kind,detail) values(p_slug,'re_visit',jsonb_build_object('visit_id',v.id,'source',v.source));
  return to_jsonb(v);
 end if;

 if p_role='buyer' then raise exception 'INVALID: Use the agent or manager demo for this action'; end if;

 if p_action='stage' then
  select * into l from demo_re_leads where slug=p_slug and id=(p_data->>'id')::uuid;
  if not found then raise exception 'NOT_FOUND: Lead not found'; end if;
  target:=p_data->>'stage';
  if l.stage=target then return to_jsonb(l); end if;
  if not((l.stage='new' and target in ('qualified','lost')) or (l.stage='qualified' and target in ('visit_booked','negotiating','lost'))
   or (l.stage='visit_booked' and target in ('qualified','negotiating','lost')) or (l.stage='negotiating' and target in ('won','lost','visit_booked'))
   or (l.stage='lost' and target='new')) then raise exception 'CONFLICT: Invalid pipeline move'; end if;
  if target='lost' and length(coalesce(p_data->>'reason','')) not between 2 and 200 then raise exception 'INVALID: Add a reason for a lost lead'; end if;
  if target='visit_booked' and not exists(select 1 from demo_re_visits x where x.lead_id=l.id and x.status='confirmed') then raise exception 'CONFLICT: Book a site visit first'; end if;
  if target in ('lost','won') then update demo_re_visits set status='cancelled' where lead_id=l.id and status='confirmed' and starts_at>now(); end if;
  update demo_re_leads set stage=target,lost_reason=case when target='lost' then p_data->>'reason' when target='new' then '' else lost_reason end,updated_at=now(),
   history=history||jsonb_build_array(jsonb_build_object('kind','stage','text',target,'at',now())) where id=l.id returning * into l;
  insert into demo_events(slug,kind,detail) values(p_slug,'re_stage',jsonb_build_object('lead_id',l.id,'stage',target));
  return to_jsonb(l);
 elsif p_action='assign' then
  select * into ag from demo_re_agents where slug=p_slug and id=(p_data->>'agentId')::uuid and active;
  if not found then raise exception 'INVALID: Choose an active agent'; end if;
  update demo_re_leads set agent_id=ag.id,updated_at=now(),history=history||jsonb_build_array(jsonb_build_object('kind','assign','text','Assigned to '||ag.name,'at',now()))
   where slug=p_slug and id=(p_data->>'id')::uuid returning * into l;
  if not found then raise exception 'NOT_FOUND: Lead not found'; end if;
  return to_jsonb(l);
 elsif p_action='note' then
  if length(coalesce(p_data->>'text','')) not between 1 and 500 then raise exception 'INVALID: Write a short note'; end if;
  update demo_re_leads set updated_at=now(),history=history||jsonb_build_array(jsonb_build_object('kind','note','text',p_data->>'text','at',now()))
   where slug=p_slug and id=(p_data->>'id')::uuid returning * into l;
  if not found then raise exception 'NOT_FOUND: Lead not found'; end if;
  return to_jsonb(l);
 elsif p_action='listing' then
  if p_data->>'status' not in ('available','reserved','sold') then raise exception 'INVALID: Invalid listing status'; end if;
  update demo_re_listings set status=p_data->>'status' where slug=p_slug and id=(p_data->>'id')::uuid returning * into li;
  if not found then raise exception 'NOT_FOUND: Listing not found'; end if;
  return to_jsonb(li);
 end if;

 if p_role<>'manager' then raise exception 'INVALID: Use the manager demo for this action'; end if;
 if p_action='agent' then
  row_id:=(p_data->>'id')::uuid;
  if (p_data->>'active')::boolean=false and exists(select 1 from demo_re_visits where agent_id=row_id and status='confirmed' and starts_at>now()) then
   raise exception 'CONFLICT: Move this agent''s confirmed visits first'; end if;
  update demo_re_agents set active=(p_data->>'active')::boolean where slug=p_slug and id=row_id returning * into ag;
  if not found then raise exception 'NOT_FOUND: Agent not found'; end if;
  return to_jsonb(ag);
 elsif p_action='settings' then
  if exists(select 1 from demo_re_visits where slug=p_slug and status='confirmed' and starts_at>now() and
   (extract(hour from starts_at at time zone 'Asia/Karachi')*60+extract(minute from starts_at at time zone 'Asia/Karachi')<(p_data->>'openMin')::int or
    extract(hour from ends_at at time zone 'Asia/Karachi')*60+extract(minute from ends_at at time zone 'Asia/Karachi')>(p_data->>'closeMin')::int)) then
   raise exception 'CONFLICT: Move visits outside the new hours first'; end if;
  update demo_re_settings set open_min=(p_data->>'openMin')::int,close_min=(p_data->>'closeMin')::int where slug=p_slug returning * into s;
  return to_jsonb(s);
 end if;
 raise exception 'INVALID: Unknown property action';
end $$;

do $$ declare t text; begin
 foreach t in array array['demo_re_settings','demo_re_agents','demo_re_listings','demo_re_buyers','demo_re_leads','demo_re_visits','demo_re_archives'] loop
  execute format('alter table %I enable row level security',t);
 end loop;
end $$;
revoke all on function demo_re_action(text,text,text,text,jsonb) from public,anon,authenticated;
grant execute on function demo_re_action(text,text,text,text,jsonb) to service_role;
