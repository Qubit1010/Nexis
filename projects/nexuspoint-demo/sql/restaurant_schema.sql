-- Synthetic restaurant workspaces. Every mutation uses one business-scoped lock.
create extension if not exists btree_gist with schema public;
create table if not exists demo_restaurant_settings (
 slug text primary key references demo_businesses(slug), open_min int not null default 720,
 close_min int not null default 1440, accepting boolean not null default true,
 prep_minutes int not null default 30, seeded boolean not null default false,
 check(open_min>=0 and close_min<=1440 and close_min-open_min>=90), check(prep_minutes between 10 and 120)
);
create table if not exists demo_menu_items (
 id uuid primary key default gen_random_uuid(), slug text not null references demo_businesses(slug),
 name text not null, name_ur text not null, category text not null, description text not null,
 price int not null check(price between 1 and 100000), available boolean not null default true,
 allergens text[] not null default '{}', art text not null default 'karahi'
);
create table if not exists demo_restaurant_tables (
 id uuid primary key default gen_random_uuid(), slug text not null references demo_businesses(slug),
 name text not null, seats int not null check(seats between 1 and 20), area text not null, active boolean not null default true
);
create table if not exists demo_customers (
 id uuid primary key default gen_random_uuid(), slug text not null references demo_businesses(slug),
 visitor text not null, name text not null default 'Demo guest', created_at timestamptz not null default now(), unique(slug,visitor)
);
create table if not exists demo_orders (
 id uuid primary key default gen_random_uuid(), slug text not null references demo_businesses(slug),
 customer_id uuid not null references demo_customers(id), number bigint generated always as identity,
 items jsonb not null, total int not null, mode text not null check(mode in ('pickup','delivery','dine_in')),
 address text not null default '', table_id uuid references demo_restaurant_tables(id), notes text not null default '',
 status text not null default 'placed' check(status in ('placed','accepted','preparing','ready','out_for_delivery','completed','cancelled')),
 payment text not null default 'cash_due' check(payment in ('cash_due','paid_demo')),
 source text not null, request_id text not null, fingerprint text not null,
 timeline jsonb not null default '[]', estimated_at timestamptz not null,
 created_at timestamptz not null default now(), updated_at timestamptz not null default now(), unique(slug,request_id)
);
create table if not exists demo_reservations (
 id uuid primary key default gen_random_uuid(), slug text not null references demo_businesses(slug),
 customer_id uuid not null references demo_customers(id), table_id uuid not null references demo_restaurant_tables(id),
 party int not null check(party between 1 and 20), starts_at timestamptz not null, ends_at timestamptz not null,
 status text not null default 'confirmed' check(status in ('confirmed','seated','completed','cancelled','no_show')),
 notes text not null default '', source text not null, request_id text not null, fingerprint text not null,
 created_at timestamptz not null default now(), unique(slug,request_id),
 exclude using gist(table_id with =, tstzrange(starts_at,ends_at,'[)') with &&) where (status in ('confirmed','seated'))
);
create table if not exists demo_restaurant_waitlist (
 id uuid primary key default gen_random_uuid(), slug text not null references demo_businesses(slug),
 customer_id uuid not null references demo_customers(id), party int not null check(party between 1 and 20),
 status text not null default 'waiting' check(status in ('waiting','notified','seated','cancelled')),
 notes text not null default '', created_at timestamptz not null default now()
);
create table if not exists demo_restaurant_archives (
 id uuid primary key default gen_random_uuid(), slug text not null references demo_businesses(slug),
 data jsonb not null, archived_at timestamptz not null default now()
);
create index if not exists demo_orders_scope on demo_orders(slug,customer_id,created_at desc);
create index if not exists demo_reservations_scope on demo_reservations(slug,starts_at);
create or replace function demo_restaurant_action(p_slug text,p_visitor text,p_role text,p_action text,p_data jsonb default '{}')
returns jsonb language plpgsql security definer set search_path=public as $$
declare b demo_businesses; s demo_restaurant_settings; c demo_customers; o demo_orders; r demo_reservations;
 m demo_menu_items; tb demo_restaurant_tables; ln jsonb; snapshots jsonb:='[]'; total_value int:=0;
 qty int; spice text; start_time timestamptz; target text; request_key text; digest text; row_id uuid; minute_value int;
begin
 perform pg_advisory_xact_lock(hashtext('restaurant:'||p_slug));
 select * into b from demo_businesses where slug=p_slug and sector='food';
 if not found then raise exception 'INVALID: Unknown restaurant'; end if;
 if b.expires_at<=now() and p_action<>'reset' then raise exception 'EXPIRED: This preview has expired'; end if;
 if p_role not in ('customer','restaurant','kitchen','system') then raise exception 'INVALID: Invalid demo role'; end if;
 if p_action='reset' then
  if p_role<>'system' then raise exception 'INVALID: Reset is an owner action'; end if;
  insert into demo_restaurant_archives(slug,data) select p_slug,jsonb_build_object(
   'settings',(select to_jsonb(x) from demo_restaurant_settings x where slug=p_slug),
   'menu',(select jsonb_agg(x) from demo_menu_items x where slug=p_slug),'tables',(select jsonb_agg(x) from demo_restaurant_tables x where slug=p_slug),
   'customers',(select jsonb_agg(x) from demo_customers x where slug=p_slug),'orders',(select jsonb_agg(x) from demo_orders x where slug=p_slug),
   'reservations',(select jsonb_agg(x) from demo_reservations x where slug=p_slug),'waitlist',(select jsonb_agg(x) from demo_restaurant_waitlist x where slug=p_slug),
   'conversations',(select jsonb_agg(x) from demo_conversations x where slug=p_slug),
   'messages',(select jsonb_agg(x) from demo_messages x where conversation_id in(select id from demo_conversations where slug=p_slug)));
  delete from demo_orders where slug=p_slug; delete from demo_reservations where slug=p_slug;
  delete from demo_restaurant_waitlist where slug=p_slug; delete from demo_customers where slug=p_slug;
  delete from demo_restaurant_tables where slug=p_slug; delete from demo_menu_items where slug=p_slug;
  delete from demo_restaurant_settings where slug=p_slug; delete from demo_conversations where slug=p_slug;
  return '{"ok":true}';
 end if;
 insert into demo_restaurant_settings(slug) values(p_slug) on conflict do nothing;
 select * into s from demo_restaurant_settings where slug=p_slug;
 if p_action='seed' then
  if p_role<>'system' then raise exception 'INVALID: Seed is an owner action'; end if;
  if s.seeded then return '{"ok":true}'; end if;
  for ln in select value from jsonb_array_elements(p_data->'menu') loop
   insert into demo_menu_items(slug,name,name_ur,category,description,price,allergens,art) values
   (p_slug,ln->>'name',ln->>'name_ur',ln->>'category',ln->>'description',(ln->>'price')::int,
    array(select jsonb_array_elements_text(ln->'allergens')),ln->>'art');
  end loop;
  for ln in select value from jsonb_array_elements(p_data->'tables') loop
   insert into demo_restaurant_tables(slug,name,seats,area) values(p_slug,ln->>'name',(ln->>'seats')::int,ln->>'area');
  end loop;
  for qty in 1..3 loop
   insert into demo_customers(slug,visitor,name) values(p_slug,'sample-guest-'||qty,
    case qty when 1 then 'Ayesha Khan' when 2 then 'Bilal Ahmed' else 'Zainab Baloch' end) returning * into c;
   select * into m from demo_menu_items where slug=p_slug order by price desc limit 1 offset qty-1;
   insert into demo_orders(slug,customer_id,items,total,mode,notes,status,source,request_id,fingerprint,timeline,estimated_at,created_at)
    values(p_slug,c.id,jsonb_build_array(jsonb_build_object('item_id',m.id,'name',m.name,'name_ur',m.name_ur,'price',m.price,'quantity',1,'spice','medium','notes','Sample ticket')),
    m.price,case qty when 1 then 'pickup' when 2 then 'delivery' else 'dine_in' end,'Fictional outreach ticket',
    case qty when 1 then 'placed' when 2 then 'preparing' else 'ready' end,'sample','sample-order-'||qty,'sample',
    jsonb_build_array(jsonb_build_object('status','placed','at',now()-interval '8 minutes')),now()+interval '22 minutes',now()-interval '8 minutes');
   if qty<3 then
    start_time:=(((now() at time zone 'Asia/Karachi')::date+1)::text||' 18:00:00+05')::timestamptz;
    select * into tb from demo_restaurant_tables where slug=p_slug and seats=qty*2 order by name limit 1;
    if start_time+interval '90 minutes'<b.expires_at then
     insert into demo_reservations(slug,customer_id,table_id,party,starts_at,ends_at,notes,source,request_id,fingerprint)
      values(p_slug,c.id,tb.id,qty*2,start_time,start_time+interval '90 minutes','Fictional family booking','sample','sample-table-'||qty,'sample');
    end if;
   end if;
  end loop;
  update demo_restaurant_settings set seeded=true where slug=p_slug;
  return '{"ok":true}';
 end if;
 if p_visitor !~ '^[a-zA-Z0-9_-]{8,64}$' then raise exception 'INVALID: Invalid guest session'; end if;
 insert into demo_customers(slug,visitor) values(p_slug,p_visitor) on conflict do nothing;
 select * into c from demo_customers where slug=p_slug and visitor=p_visitor;
 if p_action='guest' then
  if p_role<>'restaurant' or length(coalesce(p_data->>'name','')) not between 1 and 80 then raise exception 'INVALID: Enter a sample guest name in the manager view'; end if;
  insert into demo_customers(slug,visitor,name) values(p_slug,'staff-'||gen_random_uuid(),p_data->>'name') returning * into c;
  return to_jsonb(c);
 end if;
 if p_action='customer' then
  if length(coalesce(p_data->>'name','')) between 1 and 80 then update demo_customers set name=p_data->>'name' where id=c.id returning * into c; end if;
  return to_jsonb(c);
 end if;
 if p_role='restaurant' and p_data ? 'customerId' then
  select * into c from demo_customers where slug=p_slug and id=(p_data->>'customerId')::uuid;
  if not found then raise exception 'INVALID: Unknown guest'; end if;
 end if;
 if p_action='order' then
  if p_role='kitchen' then raise exception 'INVALID: Kitchen cannot place orders'; end if;
  request_key:=p_data->>'requestId'; digest:=md5(p_data::text);
  if length(coalesce(request_key,'')) not between 8 and 100 then raise exception 'INVALID: Retry identifier required'; end if;
  select * into o from demo_orders where slug=p_slug and request_id=request_key;
  if found then
   if o.customer_id<>c.id or o.fingerprint<>digest then raise exception 'CONFLICT: Retry identifier already used for a different order'; end if;
   return to_jsonb(o);
  end if;
  if not s.accepting then raise exception 'CONFLICT: Demo ordering is paused. Ask staff for help'; end if;
  if p_data->>'mode' not in ('pickup','delivery','dine_in') then raise exception 'INVALID: Choose an order mode'; end if;
  if p_data->>'mode'='delivery' and length(coalesce(p_data->>'address',''))<5 then raise exception 'INVALID: Add a fictional delivery address'; end if;
  if p_data->>'mode'='dine_in' then
   select * into tb from demo_restaurant_tables where slug=p_slug and id=(p_data->>'tableId')::uuid and active;
   if not found then raise exception 'INVALID: Choose a sample table'; end if;
  end if;
  if jsonb_typeof(p_data->'items')<>'array' or jsonb_array_length(p_data->'items') not between 1 and 30 then raise exception 'INVALID: Add items to the basket'; end if;
  for ln in select value from jsonb_array_elements(p_data->'items') loop
   select * into m from demo_menu_items where slug=p_slug and id=(ln->>'itemId')::uuid;
   if not found then raise exception 'INVALID: Unknown menu item'; end if;
   if not m.available then raise exception 'CONFLICT: A basket item is sold out. Review your basket'; end if;
   qty:=(ln->>'quantity')::int; spice:=coalesce(ln->>'spice','medium');
   if qty not between 1 and 20 or spice not in ('mild','medium','hot') or length(coalesce(ln->>'notes',''))>300 then raise exception 'INVALID: Invalid item quantity or preferences'; end if;
   total_value:=total_value+m.price*qty;
   snapshots:=snapshots||jsonb_build_array(jsonb_build_object('item_id',m.id,'name',m.name,'name_ur',m.name_ur,'price',m.price,'quantity',qty,'spice',spice,'notes',coalesce(ln->>'notes','')));
  end loop;
  insert into demo_orders(slug,customer_id,items,total,mode,address,table_id,notes,source,request_id,fingerprint,timeline,estimated_at)
   values(p_slug,c.id,snapshots,total_value,p_data->>'mode',left(coalesce(p_data->>'address',''),300),tb.id,left(coalesce(p_data->>'notes',''),500),
    case when p_role='restaurant' then 'staff' when p_data->>'source'='chat' then 'chat' else 'portal' end,request_key,digest,
    jsonb_build_array(jsonb_build_object('status','placed','at',now())),now()+make_interval(mins=>s.prep_minutes)) returning * into o;
  insert into demo_events(slug,kind,detail) values(p_slug,'restaurant_order',jsonb_build_object('order_id',o.id,'source',o.source));
  return to_jsonb(o);
 end if;
 if p_action='order_status' or p_action='payment' then
  select * into o from demo_orders where slug=p_slug and id=(p_data->>'id')::uuid;
  if not found or (p_role='customer' and o.customer_id<>c.id) then raise exception 'NOT_FOUND: Order not found'; end if;
  if p_action='payment' then
   if p_role<>'restaurant' or o.status='cancelled' then raise exception 'INVALID: Manager can record a simulated payment'; end if;
   update demo_orders set payment='paid_demo',updated_at=now() where id=o.id returning * into o; return to_jsonb(o);
  end if;
  target:=p_data->>'status';
  if p_role='customer' and not(o.status='placed' and target='cancelled') then raise exception 'CONFLICT: Staff must change orders already accepted'; end if;
  if p_role='kitchen' and target not in ('preparing','ready') then raise exception 'INVALID: Kitchen can prepare or mark ready'; end if;
  if o.status=target then return to_jsonb(o); end if;
  if not((o.status='placed' and target in ('accepted','cancelled')) or (o.status='accepted' and target in ('preparing','cancelled'))
   or (o.status='preparing' and target='ready') or (o.status='ready' and (target='completed' or (target='out_for_delivery' and o.mode='delivery')))
   or (o.status='out_for_delivery' and target='completed')) then raise exception 'CONFLICT: Invalid order status transition'; end if;
  update demo_orders set status=target,updated_at=now(),timeline=timeline||jsonb_build_array(jsonb_build_object('status',target,'at',now())) where id=o.id returning * into o;
  insert into demo_events(slug,kind,detail) values(p_slug,'order_'||target,jsonb_build_object('order_id',o.id,'simulated_notice',true)); return to_jsonb(o);
 end if;
 if p_action in ('reserve','reservation') then
  if p_role='kitchen' then raise exception 'INVALID: Kitchen cannot change table bookings'; end if;
  if p_action='reservation' then
   select * into r from demo_reservations where slug=p_slug and id=(p_data->>'id')::uuid;
   if not found or (p_role='customer' and r.customer_id<>c.id) then raise exception 'NOT_FOUND: Booking not found'; end if;
   if not(p_data ? 'start') then
    target:=p_data->>'status';
    if p_role='customer' and target<>'cancelled' then raise exception 'INVALID: Guests can cancel or reschedule'; end if;
    if r.status=target then return to_jsonb(r); end if;
    if not((r.status='confirmed' and target in ('cancelled','seated','no_show')) or(r.status='seated' and target='completed')) then raise exception 'CONFLICT: Invalid table booking transition'; end if;
    if target='seated' and (r.starts_at at time zone 'Asia/Karachi')::date<>(now() at time zone 'Asia/Karachi')::date then raise exception 'INVALID: Check in on the booking day'; end if;
    update demo_reservations set status=target where id=r.id returning * into r; return to_jsonb(r);
   end if;
   if r.status<>'confirmed' then raise exception 'CONFLICT: Only confirmed bookings can move'; end if;
   qty:=r.party;
  else
   qty:=(p_data->>'party')::int; request_key:=p_data->>'requestId'; digest:=md5(p_data::text);
   if length(coalesce(request_key,'')) not between 8 and 100 then raise exception 'INVALID: Retry identifier required'; end if;
   select * into r from demo_reservations where slug=p_slug and request_id=request_key;
   if found then
    if r.customer_id<>c.id or r.fingerprint<>digest then raise exception 'CONFLICT: Retry identifier already used'; end if;
    return to_jsonb(r);
   end if;
  end if;
  start_time:=(p_data->>'start')::timestamptz;
  minute_value:=extract(hour from start_time at time zone 'Asia/Karachi')::int*60+extract(minute from start_time at time zone 'Asia/Karachi')::int;
  if qty not between 1 and 20 or start_time<=now() or start_time+interval '90 minutes'>b.expires_at
   or (start_time at time zone 'Asia/Karachi')::date>(now() at time zone 'Asia/Karachi')::date+13
   or extract(second from start_time)<>0 or minute_value%30<>0 or minute_value<s.open_min or minute_value+90>s.close_min then raise exception 'INVALID: Choose a future available 30-minute slot within demo hours'; end if;
  select * into tb from demo_restaurant_tables t where t.slug=p_slug and t.active and t.seats>=qty
   and (not(p_data ? 'tableId') or t.id=(p_data->>'tableId')::uuid)
   and not exists(select 1 from demo_reservations x where x.table_id=t.id and x.status in ('confirmed','seated') and x.id is distinct from r.id
    and x.starts_at<start_time+interval '90 minutes' and x.ends_at>start_time) order by seats,name limit 1;
  if not found then raise exception 'CONFLICT: This table time is full. Choose another slot'; end if;
  if p_action='reservation' then
   update demo_reservations set table_id=tb.id,starts_at=start_time,ends_at=start_time+interval '90 minutes' where id=r.id returning * into r;
  else
   insert into demo_reservations(slug,customer_id,table_id,party,starts_at,ends_at,notes,source,request_id,fingerprint)
    values(p_slug,c.id,tb.id,qty,start_time,start_time+interval '90 minutes',left(coalesce(p_data->>'notes',''),500),
    case when p_role='restaurant' then 'staff' when p_data->>'source'='chat' then 'chat' else 'portal' end,request_key,digest) returning * into r;
  end if;
  insert into demo_events(slug,kind,detail) values(p_slug,'table_booking',jsonb_build_object('reservation_id',r.id,'source',r.source)); return to_jsonb(r);
 end if;
 if p_role<>'restaurant' then raise exception 'INVALID: Use the manager demo for this action'; end if;
 if p_action='menu' then
  update demo_menu_items set available=coalesce((p_data->>'available')::boolean,available),price=coalesce((p_data->>'price')::int,price)
   where slug=p_slug and id=(p_data->>'id')::uuid returning * into m;
  if not found then raise exception 'NOT_FOUND: Menu item not found'; end if; return to_jsonb(m);
 elsif p_action='table' then
  row_id:=(p_data->>'id')::uuid;
  if (p_data->>'active')::boolean=false and exists(select 1 from demo_reservations where slug=p_slug and table_id=row_id and status in ('confirmed','seated')) then raise exception 'CONFLICT: Reschedule or finish table bookings first'; end if;
  update demo_restaurant_tables set active=(p_data->>'active')::boolean where slug=p_slug and id=row_id returning * into tb;
  if not found then raise exception 'NOT_FOUND: Table not found'; end if; return to_jsonb(tb);
 elsif p_action='settings' then
  if p_data ? 'openMin' and exists(select 1 from demo_reservations where slug=p_slug and status in ('confirmed','seated') and
   (extract(hour from starts_at at time zone 'Asia/Karachi')*60+extract(minute from starts_at at time zone 'Asia/Karachi')<(p_data->>'openMin')::int or
    extract(hour from starts_at at time zone 'Asia/Karachi')*60+extract(minute from starts_at at time zone 'Asia/Karachi')+90>(p_data->>'closeMin')::int)) then raise exception 'CONFLICT: Reschedule bookings before changing hours'; end if;
  update demo_restaurant_settings set accepting=coalesce((p_data->>'accepting')::boolean,accepting),prep_minutes=coalesce((p_data->>'prepMinutes')::int,prep_minutes),
   open_min=coalesce((p_data->>'openMin')::int,open_min),close_min=coalesce((p_data->>'closeMin')::int,close_min) where slug=p_slug returning * into s; return to_jsonb(s);
 elsif p_action='waitlist' then
  if p_data ? 'id' then
   target:=p_data->>'status'; if target not in ('notified','seated','cancelled') then raise exception 'INVALID: Invalid waitlist state'; end if;
   update demo_restaurant_waitlist set status=target where slug=p_slug and id=(p_data->>'id')::uuid returning id into row_id;
   if not found then raise exception 'NOT_FOUND: Waiting guest not found'; end if;
  else
   insert into demo_restaurant_waitlist(slug,customer_id,party,notes) values(p_slug,c.id,(p_data->>'party')::int,left(coalesce(p_data->>'notes',''),300)) returning id into row_id;
  end if;
  return jsonb_build_object('id',row_id);
 end if;
 raise exception 'INVALID: Unknown restaurant action';
end $$;
do $$ declare n text; begin
 foreach n in array array['demo_restaurant_settings','demo_menu_items','demo_restaurant_tables','demo_customers','demo_orders','demo_reservations','demo_restaurant_waitlist','demo_restaurant_archives'] loop
  execute format('alter table %I enable row level security',n);
 end loop;
end $$;
revoke all on function demo_restaurant_action(text,text,text,text,jsonb) from public,anon,authenticated;
grant execute on function demo_restaurant_action(text,text,text,text,jsonb) to service_role;
