-- Additive demo-only healthcare schema. Access remains server-side through the service role.
create table if not exists demo_doctors (
  id text primary key, slug text not null references demo_businesses(slug),
  name text not null, specialty text not null, bio text not null,
  modes jsonb not null default '["in_person","phone","video"]',
  schedule jsonb not null default '[]', active boolean not null default true
);
create table if not exists demo_patients (
  id uuid primary key default gen_random_uuid(), slug text not null references demo_businesses(slug),
  visitor text not null, name text not null default 'Demo patient',
  age integer, allergies jsonb not null default '[]', created_at timestamptz not null default now(),
  unique(slug, visitor)
);
create table if not exists demo_appointments (
  id uuid primary key default gen_random_uuid(), slug text not null references demo_businesses(slug),
  patient_id uuid not null references demo_patients(id), doctor_id text not null references demo_doctors(id),
  starts_at timestamptz not null, ends_at timestamptz not null,
  mode text not null check(mode in ('in_person','phone','video')),
  status text not null default 'confirmed' check(status in ('confirmed','checked_in','in_consultation','completed','cancelled','no_show')),
  source text not null, reason text not null default '', request_id text not null,
  queue_number integer, created_at timestamptz not null default now(), unique(slug, request_id),
  check(ends_at = starts_at + interval '30 minutes')
);
create unique index if not exists demo_appointment_slot on demo_appointments(doctor_id, starts_at)
  where status not in ('cancelled','no_show');
create index if not exists demo_appointment_business on demo_appointments(slug, starts_at);
create table if not exists demo_schedule_blocks (
  id uuid primary key default gen_random_uuid(), slug text not null references demo_businesses(slug),
  doctor_id text not null references demo_doctors(id), starts_at timestamptz not null, ends_at timestamptz not null,
  reason text not null default 'Unavailable', active boolean not null default true,
  check(ends_at > starts_at)
);
create table if not exists demo_clinical_records (
  id uuid primary key default gen_random_uuid(), slug text not null references demo_businesses(slug),
  patient_id uuid not null references demo_patients(id), doctor_id text not null references demo_doctors(id),
  appointment_id uuid references demo_appointments(id), visit_at timestamptz not null,
  published boolean not null default false, data jsonb not null,
  created_at timestamptz not null default now(), updated_at timestamptz not null default now()
);
create table if not exists demo_healthcare_seed (
  slug text primary key references demo_businesses(slug), seeded_at timestamptz not null default now()
);
create table if not exists demo_healthcare_archives (
  id uuid primary key default gen_random_uuid(), slug text not null references demo_businesses(slug),
  snapshot jsonb not null, archived_at timestamptz not null default now()
);
alter table demo_conversations add column if not exists staff_mode boolean not null default false;
alter table demo_conversations add column if not exists assigned_to text;
alter table demo_conversations add column if not exists booking_context jsonb;
alter table demo_messages add column if not exists cards jsonb;
alter table demo_doctors enable row level security;
alter table demo_patients enable row level security;
alter table demo_appointments enable row level security;
alter table demo_schedule_blocks enable row level security;
alter table demo_clinical_records enable row level security;
alter table demo_healthcare_seed enable row level security;
alter table demo_healthcare_archives enable row level security;

-- Serializing per clinic also protects schedule edits, queue numbers and reset operations.
create or replace function demo_validate_slot(p_slug text, p_doctor text, p_start timestamptz, p_mode text)
returns void language plpgsql set search_path = public as $$
declare d demo_doctors; local_start timestamp; local_end timestamp; day_schedule jsonb;
begin
  select * into d from demo_doctors where id=p_doctor and slug=p_slug and active;
  if not found then raise exception 'INVALID: Unknown doctor'; end if;
  if not d.modes ? p_mode then raise exception 'INVALID: Consultation mode unavailable'; end if;
  local_start := p_start at time zone 'Asia/Karachi';
  local_end := (p_start + interval '30 minutes') at time zone 'Asia/Karachi';
  if p_start <= now() or local_start::date > (now() at time zone 'Asia/Karachi')::date + 13
     or p_start + interval '30 minutes' > (select expires_at from demo_businesses where slug=p_slug)
     or extract(second from local_start) <> 0 or mod(extract(minute from local_start)::int,30) <> 0 then
    raise exception 'INVALID: Choose a future 30-minute slot within the demo booking window';
  end if;
  select s into day_schedule from jsonb_array_elements(d.schedule) s
    where (s->>'day')::int = extract(dow from local_start)::int
      and local_start::time >= (s->>'start')::time and local_end::time <= (s->>'end')::time
      and local_start::date = local_end::date limit 1;
  if day_schedule is null then raise exception 'CONFLICT: Doctor is outside scheduled hours'; end if;
  if exists(select 1 from demo_schedule_blocks where slug=p_slug and doctor_id=p_doctor and active
    and starts_at < p_start + interval '30 minutes' and ends_at > p_start) then
    raise exception 'CONFLICT: Doctor is unavailable for this slot';
  end if;
end $$;

create or replace function demo_book_appointment(p_slug text, p_patient uuid, p_doctor text,
  p_start timestamptz, p_mode text, p_source text, p_reason text, p_request text)
returns setof demo_appointments language plpgsql set search_path = public as $$
declare existing demo_appointments;
begin
  perform pg_advisory_xact_lock(hashtext('healthcare:' || p_slug));
  select * into existing from demo_appointments where slug=p_slug and request_id=p_request;
  if found then
    if existing.patient_id <> p_patient or existing.doctor_id <> p_doctor or existing.starts_at <> p_start or existing.mode <> p_mode then
      raise exception 'CONFLICT: Request identifier already used';
    end if;
    return next existing; return;
  end if;
  if not exists(select 1 from demo_patients where id=p_patient and slug=p_slug) then raise exception 'INVALID: Unknown patient'; end if;
  perform demo_validate_slot(p_slug,p_doctor,p_start,p_mode);
  if exists(select 1 from demo_appointments where doctor_id=p_doctor and starts_at=p_start and status not in ('cancelled','no_show')) then
    raise exception 'CONFLICT: This slot has just been booked. Choose another time';
  end if;
  return query insert into demo_appointments(slug,patient_id,doctor_id,starts_at,ends_at,mode,source,reason,request_id)
    values(p_slug,p_patient,p_doctor,p_start,p_start+interval '30 minutes',p_mode,p_source,p_reason,p_request) returning *;
end $$;

create or replace function demo_change_appointment(p_slug text, p_id uuid, p_status text,
  p_start timestamptz default null, p_doctor text default null, p_mode text default null)
returns setof demo_appointments language plpgsql set search_path = public as $$
declare a demo_appointments; n integer; d text; m text;
begin
  perform pg_advisory_xact_lock(hashtext('healthcare:' || p_slug));
  select * into a from demo_appointments where id=p_id and slug=p_slug for update;
  if not found then raise exception 'INVALID: Unknown appointment'; end if;
  if p_start is not null then
    if a.status not in ('confirmed','checked_in') then raise exception 'CONFLICT: This appointment cannot be rescheduled'; end if;
    d := coalesce(p_doctor,a.doctor_id); m := coalesce(p_mode,a.mode);
    perform demo_validate_slot(p_slug,d,p_start,m);
    if exists(select 1 from demo_appointments where doctor_id=d and starts_at=p_start and id<>p_id and status not in ('cancelled','no_show')) then
      raise exception 'CONFLICT: This slot has just been booked. Choose another time';
    end if;
    return query update demo_appointments set doctor_id=d,starts_at=p_start,ends_at=p_start+interval '30 minutes',
      mode=m,status='confirmed',queue_number=null where id=p_id returning *;
    return;
  end if;
  if a.status=p_status then return next a; return; end if;
  if not ((a.status='confirmed' and p_status in ('checked_in','in_consultation','cancelled','no_show'))
      or (a.status='checked_in' and p_status in ('in_consultation','cancelled','no_show'))
      or (a.status='in_consultation' and p_status='completed')) then
    raise exception 'CONFLICT: Invalid appointment status transition';
  end if;
  n := a.queue_number;
  if p_status='checked_in' then
    if (a.starts_at at time zone 'Asia/Karachi')::date <> (now() at time zone 'Asia/Karachi')::date then
      raise exception 'INVALID: Check-in opens on the appointment day';
    end if;
    select coalesce(max(queue_number),0)+1 into n from demo_appointments where slug=p_slug
      and (starts_at at time zone 'Asia/Karachi')::date=(a.starts_at at time zone 'Asia/Karachi')::date;
  end if;
  return query update demo_appointments set status=p_status,queue_number=n where id=p_id returning *;
end $$;

create or replace function demo_change_schedule(p_slug text,p_doctor text,p_schedule jsonb default null,
  p_start timestamptz default null,p_end timestamptz default null,p_reason text default 'Unavailable',p_remove uuid default null)
returns void language plpgsql set search_path = public as $$
declare a demo_appointments; local_start timestamp; local_end timestamp;
begin
  perform pg_advisory_xact_lock(hashtext('healthcare:' || p_slug));
  if not exists(select 1 from demo_doctors where id=p_doctor and slug=p_slug) then raise exception 'INVALID: Unknown doctor'; end if;
  if p_remove is not null then update demo_schedule_blocks set active=false where id=p_remove and slug=p_slug and doctor_id=p_doctor; return; end if;
  if p_schedule is not null then
    for a in select * from demo_appointments where slug=p_slug and doctor_id=p_doctor and starts_at>now() and status not in ('cancelled','no_show') loop
      local_start := a.starts_at at time zone 'Asia/Karachi'; local_end := a.ends_at at time zone 'Asia/Karachi';
      if not exists(select 1 from jsonb_array_elements(p_schedule) s where (s->>'day')::int=extract(dow from local_start)::int
        and local_start::time >= (s->>'start')::time and local_end::time <= (s->>'end')::time) then
        raise exception 'CONFLICT: Reschedule existing appointments before changing these hours';
      end if;
    end loop;
    update demo_doctors set schedule=p_schedule where id=p_doctor and slug=p_slug;
  else
    if p_end<=p_start or p_start is null or p_end is null then raise exception 'INVALID: Invalid block'; end if;
    if exists(select 1 from demo_appointments where slug=p_slug and doctor_id=p_doctor and status not in ('cancelled','no_show')
       and starts_at<p_end and ends_at>p_start) then raise exception 'CONFLICT: Reschedule appointments before blocking this time'; end if;
    insert into demo_schedule_blocks(slug,doctor_id,starts_at,ends_at,reason) values(p_slug,p_doctor,p_start,p_end,p_reason);
  end if;
end $$;

create or replace function demo_seed_healthcare(p_slug text,p_seed jsonb)
returns void language plpgsql set search_path = public as $$
begin
  perform pg_advisory_xact_lock(hashtext('healthcare:' || p_slug));
  if exists(select 1 from demo_healthcare_seed where slug=p_slug) then return; end if;
  insert into demo_doctors select * from jsonb_populate_recordset(null::demo_doctors,p_seed->'doctors');
  insert into demo_patients select * from jsonb_populate_recordset(null::demo_patients,p_seed->'patients');
  insert into demo_clinical_records select * from jsonb_populate_recordset(null::demo_clinical_records,p_seed->'records');
  insert into demo_appointments select * from jsonb_populate_recordset(null::demo_appointments,p_seed->'appointments');
  insert into demo_healthcare_seed(slug) values(p_slug);
end $$;

create or replace function demo_reset_healthcare(p_slug text) returns void language plpgsql set search_path = public as $$
begin
  perform pg_advisory_xact_lock(hashtext('healthcare:' || p_slug));
  insert into demo_healthcare_archives(slug,snapshot) values(p_slug,jsonb_build_object(
    'doctors',(select coalesce(jsonb_agg(d),'[]') from demo_doctors d where slug=p_slug),
    'patients',(select coalesce(jsonb_agg(p),'[]') from demo_patients p where slug=p_slug),
    'appointments',(select coalesce(jsonb_agg(a),'[]') from demo_appointments a where slug=p_slug),
    'records',(select coalesce(jsonb_agg(r),'[]') from demo_clinical_records r where slug=p_slug),
    'blocks',(select coalesce(jsonb_agg(b),'[]') from demo_schedule_blocks b where slug=p_slug),
    'conversations',(select coalesce(jsonb_agg(c),'[]') from demo_conversations c where slug=p_slug),
    'messages',(select coalesce(jsonb_agg(m),'[]') from demo_messages m join demo_conversations c on c.id=m.conversation_id where c.slug=p_slug)
  ));
  delete from demo_clinical_records where slug=p_slug;
  delete from demo_appointments where slug=p_slug;
  delete from demo_schedule_blocks where slug=p_slug;
  delete from demo_patients where slug=p_slug;
  delete from demo_doctors where slug=p_slug;
  delete from demo_healthcare_seed where slug=p_slug;
  delete from demo_conversations where slug=p_slug;
end $$;

-- These functions are not exposed to anon/authenticated Supabase clients.
revoke all on function demo_validate_slot(text,text,timestamptz,text) from public, anon, authenticated;
revoke all on function demo_book_appointment(text,uuid,text,timestamptz,text,text,text,text) from public, anon, authenticated;
revoke all on function demo_change_appointment(text,uuid,text,timestamptz,text,text) from public, anon, authenticated;
revoke all on function demo_change_schedule(text,text,jsonb,timestamptz,timestamptz,text,uuid) from public, anon, authenticated;
revoke all on function demo_seed_healthcare(text,jsonb) from public, anon, authenticated;
revoke all on function demo_reset_healthcare(text) from public, anon, authenticated;
grant execute on function demo_validate_slot(text,text,timestamptz,text) to service_role;
grant execute on function demo_book_appointment(text,uuid,text,timestamptz,text,text,text,text) to service_role;
grant execute on function demo_change_appointment(text,uuid,text,timestamptz,text,text) to service_role;
grant execute on function demo_change_schedule(text,text,jsonb,timestamptz,timestamptz,text,uuid) to service_role;
grant execute on function demo_seed_healthcare(text,jsonb) to service_role;
grant execute on function demo_reset_healthcare(text) to service_role;
