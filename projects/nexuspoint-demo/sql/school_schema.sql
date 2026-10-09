-- Fictional education workspaces. Service-role RPCs own all writes and lock per business.
create extension if not exists btree_gist with schema public;
create table if not exists demo_school_settings(slug text primary key references demo_businesses(slug),hours jsonb not null,seeded boolean not null default false);
create table if not exists demo_school_teachers(id uuid primary key default gen_random_uuid(),slug text not null references demo_businesses(slug),name text not null,subject text not null);
create table if not exists demo_school_classes(id uuid primary key default gen_random_uuid(),slug text not null references demo_businesses(slug),name text not null,teacher_id uuid not null references demo_school_teachers(id),room text not null);
create table if not exists demo_families(id uuid primary key default gen_random_uuid(),slug text not null references demo_businesses(slug),visitor text not null,name text not null default 'Demo family',unique(slug,visitor));
create table if not exists demo_students(id uuid primary key default gen_random_uuid(),slug text not null references demo_businesses(slug),family_id uuid not null references demo_families(id),class_id uuid not null references demo_school_classes(id),name text not null,roll text not null);
create table if not exists demo_attendance(id uuid primary key default gen_random_uuid(),slug text not null references demo_businesses(slug),student_id uuid not null references demo_students(id),class_id uuid not null references demo_school_classes(id),day date not null,status text not null check(status in ('present','absent','late','excused')),note text not null default '',unique(student_id,day));
create table if not exists demo_homework(id uuid primary key default gen_random_uuid(),slug text not null references demo_businesses(slug),class_id uuid not null references demo_school_classes(id),teacher_id uuid not null references demo_school_teachers(id),title text not null,subject text not null,instructions text not null,due date not null,published boolean not null default false);
create table if not exists demo_submissions(id uuid primary key default gen_random_uuid(),slug text not null references demo_businesses(slug),assignment_id uuid not null references demo_homework(id),student_id uuid not null references demo_students(id),text text not null,feedback text not null default '',status text not null default 'submitted' check(status in ('submitted','reviewed')),updated_at timestamptz not null default now(),unique(assignment_id,student_id));
create table if not exists demo_assessments(id uuid primary key default gen_random_uuid(),slug text not null references demo_businesses(slug),class_id uuid not null references demo_school_classes(id),teacher_id uuid not null references demo_school_teachers(id),title text not null,subject text not null,total int not null check(total between 1 and 1000),grades jsonb not null default '{}',published boolean not null default false,exam_date date not null,comment text not null default '');
create table if not exists demo_fee_invoices(id uuid primary key default gen_random_uuid(),slug text not null references demo_businesses(slug),student_id uuid not null references demo_students(id),period text not null,amount int not null check(amount between 1 and 1000000),due date not null,status text not null default 'issued' check(status in ('issued','void')),paid boolean not null default false);
create table if not exists demo_fee_claims(id uuid primary key default gen_random_uuid(),slug text not null references demo_businesses(slug),invoice_id uuid not null references demo_fee_invoices(id),family_id uuid not null references demo_families(id),reference text not null,status text not null default 'pending' check(status in ('pending','verified','rejected')),note text not null default '',created_at timestamptz not null default now(),verified_at timestamptz);
create unique index if not exists demo_fee_pending on demo_fee_claims(invoice_id) where status in ('pending','verified');
create table if not exists demo_leave_requests(id uuid primary key default gen_random_uuid(),slug text not null references demo_businesses(slug),student_id uuid not null references demo_students(id),from_day date not null,to_day date not null,reason text not null,status text not null default 'pending' check(status in ('pending','approved','declined')),note text not null default '',check(to_day>=from_day));
create table if not exists demo_admissions(id uuid primary key default gen_random_uuid(),slug text not null references demo_businesses(slug),family_id uuid not null references demo_families(id),name text not null,program text not null,note text not null default '',status text not null default 'submitted' check(status in ('submitted','reviewing','accepted','closed')),created_at timestamptz not null default now());
create table if not exists demo_campus_visits(id uuid primary key default gen_random_uuid(),slug text not null references demo_businesses(slug),family_id uuid not null references demo_families(id),starts_at timestamptz not null,ends_at timestamptz not null,status text not null default 'confirmed' check(status in ('confirmed','arrived','completed','cancelled','no_show')),notes text not null default '',source text not null,exclude using gist(slug with =,tstzrange(starts_at,ends_at,'[)') with &&) where(status in ('confirmed','arrived')));
create table if not exists demo_school_notices(id uuid primary key default gen_random_uuid(),slug text not null references demo_businesses(slug),title text not null,body text not null,published boolean not null default false,created_at timestamptz not null default now());
create table if not exists demo_lessons(id uuid primary key default gen_random_uuid(),slug text not null references demo_businesses(slug),class_id uuid not null references demo_school_classes(id),teacher_id uuid not null references demo_school_teachers(id),day int not null check(day between 0 and 6),start_min int not null,end_min int not null,subject text not null,room text not null,check(start_min>=0 and end_min<=1440 and end_min>start_min),exclude using gist(class_id with =,day with =,int4range(start_min,end_min,'[)') with &&),exclude using gist(teacher_id with =,day with =,int4range(start_min,end_min,'[)') with &&));
create table if not exists demo_school_blocks(id uuid primary key default gen_random_uuid(),slug text not null references demo_businesses(slug),starts_at timestamptz not null,ends_at timestamptz not null,reason text not null,check(ends_at>starts_at));
create table if not exists demo_school_requests(slug text not null references demo_businesses(slug),request_id text not null,visitor text not null,role text not null,action text not null,fingerprint text not null,result jsonb not null,primary key(slug,request_id));
create table if not exists demo_school_archives(id uuid primary key default gen_random_uuid(),slug text not null references demo_businesses(slug),data jsonb not null,archived_at timestamptz not null default now());
create index if not exists demo_students_scope on demo_students(slug,family_id);
create index if not exists demo_attendance_scope on demo_attendance(slug,day);
create index if not exists demo_school_visits_scope on demo_campus_visits(slug,starts_at);

create or replace function demo_school_family(p_slug text,p_visitor text) returns demo_families language plpgsql security definer set search_path=public as $$
declare f demo_families; st demo_students; cl demo_school_classes; ar demo_assessments; n int:=0; j int; d date:=(now() at time zone 'Asia/Karachi')::date;
begin
 select * into f from demo_families where slug=p_slug and visitor=p_visitor;
 if found then return f;end if;
 insert into demo_families(slug,visitor) values(p_slug,p_visitor) returning * into f;
 for cl in select * from demo_school_classes where slug=p_slug order by name loop
  n:=n+1;
  insert into demo_students(slug,family_id,class_id,name,roll) values(p_slug,f.id,cl.id,case n when 1 then 'Ayesha Khan' else 'Hasan Khan' end,'DEMO-'||upper(substr(gen_random_uuid()::text,1,5))) returning * into st;
  for j in 1..7 loop
   if extract(dow from d-j)<>0 then insert into demo_attendance(slug,student_id,class_id,day,status) values(p_slug,st.id,cl.id,d-j,case when j=3 and n=1 then 'absent' when j=2 then 'late' else 'present' end);end if;
  end loop;
  insert into demo_fee_invoices(slug,student_id,period,amount,due) values(p_slug,st.id,to_char(d,'Month YYYY')||' · sample tuition',case n when 1 then 6500 else 7000 end,d+7);
  for ar in select * from demo_assessments where slug=p_slug and class_id=cl.id and published loop
   update demo_assessments set grades=grades||jsonb_build_object(st.id::text,case n when 1 then 38 else 41 end) where id=ar.id;
  end loop;
 end loop;
 return f;
end $$;

create or replace function demo_school_action(p_slug text,p_visitor text,p_role text,p_action text,p_data jsonb default '{}') returns jsonb language plpgsql security definer set search_path=public as $$
declare b demo_businesses; s demo_school_settings; f demo_families; st demo_students; cl demo_school_classes; t demo_school_teachers;
 hw demo_homework; sub demo_submissions; ar demo_assessments; inv demo_fee_invoices; claim demo_fee_claims; lv demo_leave_requests; adm demo_admissions; v demo_campus_visits; nt demo_school_notices; lesson demo_lessons;
 prior demo_school_requests; x jsonb; row_id uuid; teacher uuid; result jsonb; target text; req text; digest text; dt date; n int; start_time timestamptz; end_time timestamptz; data_archive jsonb:='{}'; table_name text;
begin
 perform pg_advisory_xact_lock(hashtext('school:'||p_slug));
 select * into b from demo_businesses where slug=p_slug and sector='education';
 if not found then raise exception 'NOT_FOUND: Education demo not found';end if;
 if p_role not in ('parent','school','teacher','system') then raise exception 'INVALID: Invalid role';end if;
 if b.expires_at<=now() and p_action<>'reset' then raise exception 'EXPIRED: This preview has expired';end if;
 if p_action='reset' then
  if p_role<>'system' then raise exception 'INVALID: Reset is an owner action';end if;
  foreach table_name in array array['demo_school_settings','demo_school_teachers','demo_school_classes','demo_families','demo_students','demo_attendance','demo_homework','demo_submissions','demo_assessments','demo_fee_invoices','demo_fee_claims','demo_leave_requests','demo_admissions','demo_campus_visits','demo_school_notices','demo_lessons','demo_school_blocks','demo_school_requests','demo_conversations'] loop
   execute format('select coalesce(jsonb_agg(archiverow),''[]'') from %I archiverow where slug=$1',table_name) into result using p_slug;
   data_archive:=data_archive||jsonb_build_object(table_name,result);
  end loop;
  data_archive:=data_archive||jsonb_build_object('messages',(select jsonb_agg(archiverow) from demo_messages archiverow where conversation_id in(select id from demo_conversations where slug=p_slug)));
  insert into demo_school_archives(slug,data) values(p_slug,data_archive);
  foreach table_name in array array['demo_submissions','demo_fee_claims','demo_fee_invoices','demo_leave_requests','demo_attendance','demo_admissions','demo_campus_visits','demo_students','demo_families','demo_assessments','demo_homework','demo_lessons','demo_school_classes','demo_school_teachers','demo_school_notices','demo_school_blocks','demo_school_settings','demo_school_requests','demo_conversations'] loop
   execute format('delete from %I where slug=$1',table_name) using p_slug;
  end loop;
  return '{"ok":true}';
 end if;
 if p_action='seed' then
  if p_role<>'system' then raise exception 'INVALID: Seed is an owner action';end if;
  select * into s from demo_school_settings where slug=p_slug;
  if s.seeded then return '{"ok":true}';end if;
  insert into demo_school_settings(slug,hours,seeded) values(p_slug,p_data->'hours',true);
  for n in 1..2 loop
   insert into demo_school_teachers(slug,name,subject) values(p_slug,case n when 1 then 'Ms. Sara Ahmed' else 'Mr. Hamza Baloch' end,case n when 1 then 'Biology' else 'Mathematics' end) returning * into t;
   insert into demo_school_classes(slug,name,teacher_id,room) values(p_slug,p_data->'classes'->>(n-1),t.id,'Room '||(n+10)) returning * into cl;
   insert into demo_homework(slug,class_id,teacher_id,title,subject,instructions,due,published) values(p_slug,cl.id,t.id,case n when 1 then 'Cell structure worksheet' else 'Algebra practice set' end,t.subject,'Fictional learning task: complete questions 1–5 and share your sample response.',(now() at time zone 'Asia/Karachi')::date+2,true);
   insert into demo_homework(slug,class_id,teacher_id,title,subject,instructions,due) values(p_slug,cl.id,t.id,'Next lesson · draft',t.subject,'Unpublished sample task.',(now() at time zone 'Asia/Karachi')::date+4);
   insert into demo_assessments(slug,class_id,teacher_id,title,subject,total,published,exam_date,comment) values(p_slug,cl.id,t.id,'September assessment · sample',t.subject,50,true,(now() at time zone 'Asia/Karachi')::date-7,'Fictional recorded marks. Revise the practice questions.');
  end loop;
  -- Teacher timetables use non-overlapping class periods.
  for cl in select * from demo_school_classes where slug=p_slug loop
   select * into t from demo_school_teachers where id=cl.teacher_id;
   for n in 1..6 loop
    insert into demo_lessons(slug,class_id,teacher_id,day,start_min,end_min,subject,room) values(p_slug,cl.id,t.id,n,540,585,t.subject,cl.room),(p_slug,cl.id,t.id,n,660,705,t.subject||' tutorial',cl.room);
   end loop;
  end loop;
  perform demo_school_family(p_slug,'sample-family-01');perform demo_school_family(p_slug,'sample-family-02');
  insert into demo_school_notices(slug,title,body,published) values(p_slug,'Welcome to your connected campus','Fictional students, classes, fees and results for this outreach walkthrough. All campus times are PKT.',true);
  return '{"ok":true}';
 end if;
 if p_visitor !~ '^[a-zA-Z0-9_-]{8,64}$' then raise exception 'INVALID: Invalid family session';end if;
 f:=demo_school_family(p_slug,p_visitor);
 if p_action='family' then return to_jsonb(f);end if;
 if p_role='teacher' then
  teacher:=(p_data->>'teacherId')::uuid;
  select * into t from demo_school_teachers where slug=p_slug and id=teacher;
  if not found then raise exception 'INVALID: Choose your sample teacher';end if;
 end if;
 req:=p_data->>'requestId';digest:=md5(p_data::text);
 if req is not null then
  if length(req) not between 8 and 100 then raise exception 'INVALID: Retry identifier required';end if;
  select * into prior from demo_school_requests where slug=p_slug and request_id=req;
  if found then
   if prior.visitor<>p_visitor or prior.role<>p_role or prior.action<>p_action or prior.fingerprint<>digest then raise exception 'CONFLICT: Retry identifier used for a different action';end if;
   return prior.result;
  end if;
 end if;
 if p_action in ('claim','admission','visit','invoice','leave') and req is null then raise exception 'INVALID: Retry identifier required';end if;
 if p_data ? 'studentId' then
  select * into st from demo_students where slug=p_slug and id=(p_data->>'studentId')::uuid;
  if not found or (p_role='parent' and st.family_id<>f.id) then raise exception 'NOT_FOUND: Student not found';end if;
  select * into cl from demo_school_classes where id=st.class_id and slug=p_slug;
  if p_role='teacher' and cl.teacher_id<>teacher then raise exception 'NOT_FOUND: Student not assigned to this teacher';end if;
 end if;
 if p_data ? 'classId' then
  select * into cl from demo_school_classes where slug=p_slug and id=(p_data->>'classId')::uuid;
  if not found or (p_role='teacher' and cl.teacher_id<>teacher) then raise exception 'NOT_FOUND: Class not assigned to this teacher';end if;
 end if;
 if p_action='student' then
  if p_role<>'school' or cl.id is null then raise exception 'INVALID: Office and class required';end if;
  if st.id is not null then update demo_students set name=p_data->>'name',class_id=cl.id where id=st.id returning * into st;
  else insert into demo_students(slug,family_id,class_id,name,roll) values(p_slug,f.id,cl.id,p_data->>'name','DEMO-'||upper(substr(gen_random_uuid()::text,1,5))) returning * into st;end if;
  result:=to_jsonb(st);
 elsif p_action='attendance' then
  if p_role not in ('teacher','school') or cl.id is null then raise exception 'INVALID: Select a class in the staff workspace';end if;
  dt:=(p_data->>'day')::date;if dt>(now() at time zone 'Asia/Karachi')::date or dt<(now() at time zone 'Asia/Karachi')::date-365 then raise exception 'INVALID: Choose a recorded day in the past year';end if;
  if jsonb_typeof(p_data->'rows')<>'array' or jsonb_array_length(p_data->'rows') not between 1 and 100 then raise exception 'INVALID: Add attendance rows';end if;
  for x in select value from jsonb_array_elements(p_data->'rows') loop
   select * into st from demo_students where slug=p_slug and class_id=cl.id and id=(x->>'studentId')::uuid;
   if not found or x->>'status' not in ('present','absent','late','excused') then raise exception 'INVALID: Invalid class attendance row';end if;
   insert into demo_attendance(slug,student_id,class_id,day,status,note) values(p_slug,st.id,cl.id,dt,x->>'status',left(coalesce(x->>'note',''),300)) on conflict(student_id,day) do update set status=excluded.status,note=excluded.note,class_id=excluded.class_id;
  end loop;result:='{"ok":true}';
 elsif p_action in ('homework','assessment') then
  if p_role not in ('teacher','school') or cl.id is null then raise exception 'INVALID: Choose an assigned class';end if;
  row_id:=(p_data->>'id')::uuid;
  if p_action='homework' then
   if row_id is not null then
    select * into hw from demo_homework where slug=p_slug and id=row_id and class_id=cl.id;
    if not found then raise exception 'NOT_FOUND: Homework not found';end if;
   end if;
   if row_id is null then insert into demo_homework(slug,class_id,teacher_id,title,subject,instructions,due) values(p_slug,cl.id,cl.teacher_id,p_data->>'title',p_data->>'subject',p_data->>'instructions',(p_data->>'due')::date) returning * into hw;
   else update demo_homework set title=p_data->>'title',subject=p_data->>'subject',instructions=p_data->>'instructions',due=(p_data->>'due')::date,published=false where id=hw.id returning * into hw;end if;
   result:=to_jsonb(hw);
  else
   if row_id is not null then select * into ar from demo_assessments where slug=p_slug and id=row_id and class_id=cl.id;if not found then raise exception 'NOT_FOUND: Assessment not found';end if;end if;
   if jsonb_typeof(p_data->'grades')<>'object' or (p_data->>'total')::int not between 1 and 1000 then raise exception 'INVALID: Invalid assessment';end if;
   for target,x in select key,value from jsonb_each(p_data->'grades') loop
    if not exists(select 1 from demo_students where slug=p_slug and class_id=cl.id and id=target::uuid) or jsonb_typeof(x)<>'number' or (x::text)::numeric<0 or (x::text)::numeric>(p_data->>'total')::int then raise exception 'INVALID: Marks must belong to this class and be within the total';end if;
   end loop;
   if row_id is null then insert into demo_assessments(slug,class_id,teacher_id,title,subject,total,grades,exam_date,comment) values(p_slug,cl.id,cl.teacher_id,p_data->>'title',p_data->>'subject',(p_data->>'total')::int,p_data->'grades',(p_data->>'examDate')::date,coalesce(p_data->>'comment','')) returning * into ar;
   else update demo_assessments set title=p_data->>'title',subject=p_data->>'subject',total=(p_data->>'total')::int,grades=p_data->'grades',exam_date=(p_data->>'examDate')::date,comment=coalesce(p_data->>'comment',''),published=false where id=ar.id returning * into ar;end if;
   result:=to_jsonb(ar);
  end if;
 elsif p_action='publish' then
  if p_role not in ('teacher','school') then raise exception 'INVALID: Staff publication required';end if;
  row_id:=(p_data->>'id')::uuid;
  if p_data->>'kind'='homework' then
   select * into hw from demo_homework where slug=p_slug and id=row_id;
   if not found or (p_role='teacher' and hw.teacher_id<>teacher) then raise exception 'NOT_FOUND: Homework not assigned';end if;
   update demo_homework set published=true where id=row_id returning * into hw;result:=to_jsonb(hw);
  elsif p_data->>'kind'='assessment' then
   select * into ar from demo_assessments where slug=p_slug and id=row_id;
   if not found or (p_role='teacher' and ar.teacher_id<>teacher) then raise exception 'NOT_FOUND: Assessment not assigned';end if;
   update demo_assessments set published=true where id=row_id returning * into ar;result:=to_jsonb(ar);
  elsif p_data->>'kind'='notice' and p_role='school' then
   update demo_school_notices set published=true where slug=p_slug and id=row_id returning * into nt;if not found then raise exception 'NOT_FOUND: Notice not found';end if;result:=to_jsonb(nt);
  else raise exception 'INVALID: Choose publication type';end if;
 elsif p_action='submission' then
  select * into hw from demo_homework where slug=p_slug and id=(p_data->>'assignmentId')::uuid and published;
  if not found or st.id is null or hw.class_id<>st.class_id then raise exception 'NOT_FOUND: Published homework not found for this student';end if;
  if p_role='parent' then
   insert into demo_submissions(slug,assignment_id,student_id,text) values(p_slug,hw.id,st.id,p_data->>'text') on conflict(assignment_id,student_id) do update set text=excluded.text,feedback='',status='submitted',updated_at=now() returning * into sub;
  elsif p_role in ('teacher','school') then
   update demo_submissions set feedback=p_data->>'feedback',status='reviewed',updated_at=now() where slug=p_slug and student_id=st.id and assignment_id=hw.id returning * into sub;if not found then raise exception 'NOT_FOUND: Submission not found';end if;
  end if;result:=to_jsonb(sub);
 elsif p_action='invoice' then
  if p_role<>'school' or st.id is null then raise exception 'INVALID: Office must issue a fee invoice';end if;
  insert into demo_fee_invoices(slug,student_id,period,amount,due) values(p_slug,st.id,p_data->>'period',(p_data->>'amount')::int,(p_data->>'due')::date) returning * into inv;result:=to_jsonb(inv);
 elsif p_action='claim' then
  if p_role<>'parent' then raise exception 'INVALID: Use the parent portal';end if;
  select i.* into inv from demo_fee_invoices i join demo_students owner_student on owner_student.id=i.student_id where i.slug=p_slug and i.id=(p_data->>'id')::uuid and owner_student.family_id=f.id;
  if not found then raise exception 'NOT_FOUND: Invoice not found';end if;
  if inv.paid or inv.status='void' or exists(select 1 from demo_fee_claims where invoice_id=inv.id and status='pending') then raise exception 'CONFLICT: This invoice is already paid, void or awaiting verification';end if;
  insert into demo_fee_claims(slug,invoice_id,family_id,reference) values(p_slug,inv.id,f.id,p_data->>'reference') returning * into claim;result:=to_jsonb(claim);
 elsif p_action='verify' then
  if p_role<>'school' or p_data->>'status' not in ('verified','rejected') then raise exception 'INVALID: Office verification required';end if;
  select * into claim from demo_fee_claims where slug=p_slug and id=(p_data->>'id')::uuid;
  if not found then raise exception 'NOT_FOUND: Payment claim not found';end if;
  if claim.status<>'pending' then raise exception 'CONFLICT: Payment has already been reviewed';end if;
  update demo_fee_claims set status=p_data->>'status',note=coalesce(p_data->>'note',''),verified_at=now() where id=claim.id returning * into claim;
  if claim.status='verified' then update demo_fee_invoices set paid=true where id=claim.invoice_id;end if;result:=to_jsonb(claim);
 elsif p_action='void_invoice' then
  if p_role<>'school' then raise exception 'INVALID: Office required';end if;
  select * into inv from demo_fee_invoices where slug=p_slug and id=(p_data->>'id')::uuid;
  if not found then raise exception 'NOT_FOUND: Invoice not found';end if;
  if inv.paid or exists(select 1 from demo_fee_claims where invoice_id=inv.id and status='pending') then raise exception 'CONFLICT: Review pending payment before voiding';end if;
  update demo_fee_invoices set status='void' where id=inv.id returning * into inv;result:=to_jsonb(inv);
 elsif p_action='leave' then
  if p_role<>'parent' or st.id is null then raise exception 'INVALID: Parent and student required';end if;
  if (p_data->>'from')::date<(now() at time zone 'Asia/Karachi')::date or (p_data->>'to')::date>(p_data->>'from')::date+30 then raise exception 'INVALID: Choose up to 31 upcoming days';end if;
  insert into demo_leave_requests(slug,student_id,from_day,to_day,reason) values(p_slug,st.id,(p_data->>'from')::date,(p_data->>'to')::date,p_data->>'reason') returning * into lv;result:=to_jsonb(lv);
 elsif p_action='leave_status' then
  if p_role<>'school' or p_data->>'status' not in ('approved','declined') then raise exception 'INVALID: Office review required';end if;
  update demo_leave_requests set status=p_data->>'status',note=coalesce(p_data->>'note','') where slug=p_slug and id=(p_data->>'id')::uuid and status='pending' returning * into lv;
  if not found then raise exception 'CONFLICT: Leave request unavailable or already reviewed';end if;result:=to_jsonb(lv);
 elsif p_action='admission' then
  if p_role='teacher' then raise exception 'INVALID: Admissions are handled by the office';end if;
  insert into demo_admissions(slug,family_id,name,program,note) values(p_slug,f.id,p_data->>'name',p_data->>'program',coalesce(p_data->>'note','')) returning * into adm;result:=to_jsonb(adm);
 elsif p_action='admission_status' then
  if p_role<>'school' or p_data->>'status' not in ('reviewing','accepted','closed') then raise exception 'INVALID: Office review required';end if;
  update demo_admissions set status=p_data->>'status' where slug=p_slug and id=(p_data->>'id')::uuid returning * into adm;
  if not found then raise exception 'NOT_FOUND: Admission not found';end if;result:=to_jsonb(adm);
 elsif p_action in ('visit','visit_status') then
  if p_role='teacher' then raise exception 'INVALID: Campus visits are handled by the office';end if;
  if p_action='visit_status' then
   select * into v from demo_campus_visits where slug=p_slug and id=(p_data->>'id')::uuid;
   if not found or(p_role='parent' and v.family_id<>f.id) then raise exception 'NOT_FOUND: Campus visit not found';end if;
   if p_data ? 'start' then if v.status<>'confirmed' then raise exception 'CONFLICT: Only confirmed visits can be rescheduled';end if;
   else
    target:=p_data->>'status';
    if (p_role='parent' and target<>'cancelled') or not((v.status='confirmed' and target in ('arrived','cancelled','no_show')) or (v.status='arrived' and target='completed')) then raise exception 'CONFLICT: Invalid visit status transition';end if;
    update demo_campus_visits set status=target where id=v.id returning * into v;result:=to_jsonb(v);
   end if;
  end if;
  if result is null then
   start_time:=(p_data->>'start')::timestamptz;end_time:=start_time+interval '30 minutes';
   dt:=(start_time at time zone 'Asia/Karachi')::date;n:=extract(hour from start_time at time zone 'Asia/Karachi')::int*60+extract(minute from start_time at time zone 'Asia/Karachi')::int;
   select * into s from demo_school_settings where slug=p_slug;
   if start_time<=now() or dt>(now() at time zone 'Asia/Karachi')::date+13 or end_time>b.expires_at or extract(second from start_time)<>0 or n%30<>0 then raise exception 'INVALID: Choose a future 30-minute slot within this preview';end if;
   if not exists(select 1 from jsonb_array_elements(s.hours) h where (h->>'day')::int=extract(dow from dt) and n>=(h->>'start')::int and n+30<=(h->>'end')::int) then raise exception 'CONFLICT: Campus office is closed at that time';end if;
   if exists(select 1 from demo_school_blocks where slug=p_slug and starts_at<end_time and ends_at>start_time) or exists(select 1 from demo_campus_visits where slug=p_slug and status in ('confirmed','arrived') and id is distinct from v.id and starts_at<end_time and ends_at>start_time) then raise exception 'CONFLICT: That campus visit time is unavailable';end if;
   if p_action='visit' then insert into demo_campus_visits(slug,family_id,starts_at,ends_at,notes,source) values(p_slug,f.id,start_time,end_time,coalesce(p_data->>'notes',''),case when p_role='school' then 'office' when p_data->>'source'='chat' then 'chat' else 'portal' end) returning * into v;
   else update demo_campus_visits set starts_at=start_time,ends_at=end_time where id=v.id returning * into v;end if;result:=to_jsonb(v);
  end if;
 elsif p_action='block' then
  if p_role<>'school' then raise exception 'INVALID: Office required';end if;
  if p_data ? 'id' then delete from demo_school_blocks where slug=p_slug and id=(p_data->>'id')::uuid returning id into row_id;if not found then raise exception 'NOT_FOUND: Block not found';end if;
  else
   start_time:=(p_data->>'start')::timestamptz;end_time:=(p_data->>'end')::timestamptz;
   if start_time<=now() or end_time<=start_time or end_time>b.expires_at then raise exception 'INVALID: Use a future interval within preview expiry';end if;
   if exists(select 1 from demo_campus_visits where slug=p_slug and status in ('confirmed','arrived') and starts_at<end_time and ends_at>start_time) then raise exception 'CONFLICT: Reschedule booked visits before blocking this time';end if;
   insert into demo_school_blocks(slug,starts_at,ends_at,reason) values(p_slug,start_time,end_time,coalesce(p_data->>'reason','Office unavailable'));
  end if;result:='{"ok":true}';
 elsif p_action='notice' then
  if p_role<>'school' then raise exception 'INVALID: Office required';end if;
  if p_data ? 'id' then update demo_school_notices set title=p_data->>'title',body=p_data->>'body',published=false where slug=p_slug and id=(p_data->>'id')::uuid returning * into nt;if not found then raise exception 'NOT_FOUND: Notice not found';end if;
  else insert into demo_school_notices(slug,title,body) values(p_slug,p_data->>'title',p_data->>'body') returning * into nt;end if;result:=to_jsonb(nt);
 elsif p_action='lesson' then
  if p_role<>'school' or cl.id is null then raise exception 'INVALID: Office and class required';end if;
  if p_data ? 'id' then delete from demo_lessons where slug=p_slug and id=(p_data->>'id')::uuid returning id into row_id;if not found then raise exception 'NOT_FOUND: Lesson not found';end if;
  else
   select * into t from demo_school_teachers where slug=p_slug and id=(p_data->>'lessonTeacherId')::uuid;if not found then raise exception 'INVALID: Teacher not found';end if;
   if exists(select 1 from demo_lessons where slug=p_slug and day=(p_data->>'day')::int and (class_id=cl.id or teacher_id=t.id) and start_min<(p_data->>'endMin')::int and end_min>(p_data->>'startMin')::int) then raise exception 'CONFLICT: Class or teacher already has a lesson at that time';end if;
   insert into demo_lessons(slug,class_id,teacher_id,day,start_min,end_min,subject,room) values(p_slug,cl.id,t.id,(p_data->>'day')::int,(p_data->>'startMin')::int,(p_data->>'endMin')::int,p_data->>'subject',p_data->>'room') returning * into lesson;result:=to_jsonb(lesson);
  end if;result:=coalesce(result,'{"ok":true}');
 else raise exception 'INVALID: Unknown school action';
 end if;
 if req is not null then insert into demo_school_requests(slug,request_id,visitor,role,action,fingerprint,result) values(p_slug,req,p_visitor,p_role,p_action,digest,result);end if;
 insert into demo_events(slug,kind,detail) values(p_slug,'school_'||p_action,jsonb_build_object('role',p_role,'simulated',true));
 return result;
exception when exclusion_violation or unique_violation then raise exception 'CONFLICT: This slot or submission changed. Refresh and try again';
end $$;

do $$ declare n text;begin
 foreach n in array array['demo_school_settings','demo_school_teachers','demo_school_classes','demo_families','demo_students','demo_attendance','demo_homework','demo_submissions','demo_assessments','demo_fee_invoices','demo_fee_claims','demo_leave_requests','demo_admissions','demo_campus_visits','demo_school_notices','demo_lessons','demo_school_blocks','demo_school_requests','demo_school_archives'] loop
  execute format('alter table %I enable row level security',n);
 end loop;
end $$;
revoke all on function demo_school_family(text,text) from public,anon,authenticated;
revoke all on function demo_school_action(text,text,text,text,jsonb) from public,anon,authenticated;
grant execute on function demo_school_family(text,text) to service_role;
grant execute on function demo_school_action(text,text,text,text,jsonb) to service_role;
notify pgrst,'reload schema';
