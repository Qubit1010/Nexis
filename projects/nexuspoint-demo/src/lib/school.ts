import { rest, transcript, type Business, type Conversation } from './db.ts';
import { rpc } from './healthcare.ts';
import { campusSlots, type SchoolRole, type SchoolState, type Family, type CampusVisit, type SchoolSettings } from './school-types.ts';
const q=(slug:string)=>`slug=eq.${encodeURIComponent(slug)}`;
export function schoolSeed(b:Business){
 const college=/college/i.test(b.profile.facts.category??b.name);
 return {classes:college?['FSc Part I · Pre-medical','FSc Part II · Pre-engineering']:['Class 6 · Section B','Class 8 · Section A'],
  hours:Array.from({length:6},(_,i)=>[{day:i+1,start:480,end:810},...(college?[{day:i+1,start:840,end:1080}]:[])]).flat()};
}
export async function ensureSchool(b:Business){
 if(!(await rest<SchoolSettings>('GET',`demo_school_settings?${q(b.slug)}&seeded=eq.true&limit=1`))[0])
  await rpc('demo_school_action',{p_slug:b.slug,p_visitor:'system-seed',p_role:'system',p_action:'seed',p_data:schoolSeed(b)});
}
export async function schoolAction<T=unknown>(b:Business,visitor:string,role:SchoolRole,action:string,data:Record<string,unknown>):Promise<T>{
 await ensureSchool(b);return rpc<T>('demo_school_action',{p_slug:b.slug,p_visitor:visitor,p_role:role,p_action:action,p_data:data});
}
export async function schoolAvailability(b:Business,date:string){
 await ensureSchool(b);const scope=q(b.slug);
 const [settings,visits,blocks]=await Promise.all([rest<SchoolSettings>('GET',`demo_school_settings?${scope}`),rest<CampusVisit>('GET',`demo_campus_visits?${scope}&status=in.(confirmed,arrived)`),rest<SchoolState['blocks'][number]>('GET',`demo_school_blocks?${scope}`)]);
 return campusSlots(date,settings[0],[...visits,...blocks],b.expires_at);
}
export async function schoolState(b:Business,visitor:string,role:SchoolRole,teacherId?:string):Promise<SchoolState>{
 await ensureSchool(b);const family=await schoolAction<Family>(b,visitor,role,'family',{});
 const scope=q(b.slug),office=role==='school',parent=role==='parent';
 const [classes,teachers,students,settings]=await Promise.all([
  rest<SchoolState['classes'][number]>('GET',`demo_school_classes?${scope}&order=name`),rest<SchoolState['teachers'][number]>('GET',`demo_school_teachers?${scope}&order=name`),
  rest<SchoolState['students'][number]>('GET',`demo_students?${scope}${parent?`&family_id=eq.${family.id}`:''}&order=name`),
  rest<SchoolSettings>('GET',`demo_school_settings?${scope}`)]);
 const teacher=teachers.find(t=>t.id===teacherId)??teachers[0];
 if(role==='teacher'&&teacherId&&!teachers.some(t=>t.id===teacherId))throw new Error('NOT_FOUND: Teacher not found');
 const visibleClasses=parent?classes.filter(c=>students.some(s=>s.class_id===c.id)):office?classes:classes.filter(c=>c.teacher_id===teacher.id);
 const visibleStudents=parent||office?students:students.filter(s=>visibleClasses.some(c=>c.id===s.class_id));
 const studentScope=`&student_id=in.(${visibleStudents.map(s=>s.id).join(',')||'00000000-0000-0000-0000-000000000000'})`;
 const classScope=`&class_id=in.(${visibleClasses.map(c=>c.id).join(',')||'00000000-0000-0000-0000-000000000000'})`;
 const [families,attendance,homework,submissions,assessments,invoices,claims,leaves,admissions,visits,notices,lessons,blocks,conversations,activity]=await Promise.all([
  office?rest<Family>('GET',`demo_families?${scope}`):Promise.resolve([family]),
  rest<SchoolState['attendance'][number]>('GET',`demo_attendance?${scope}${studentScope}&order=day.desc&limit=1000`),
  rest<SchoolState['homework'][number]>('GET',`demo_homework?${scope}${classScope}${parent?'&published=eq.true':''}&order=due.desc`),
  rest<SchoolState['submissions'][number]>('GET',`demo_submissions?${scope}${studentScope}`),
  rest<SchoolState['assessments'][number]>('GET',`demo_assessments?${scope}${classScope}${parent?'&published=eq.true':''}&order=exam_date.desc`),
  role==='teacher'?Promise.resolve([]):rest<SchoolState['invoices'][number]>('GET',`demo_fee_invoices?${scope}${studentScope}&order=due.desc`),
  role==='teacher'?Promise.resolve([]):rest<SchoolState['claims'][number]>('GET',`demo_fee_claims?${scope}${parent?`&family_id=eq.${family.id}`:''}&order=created_at.desc`),
  rest<SchoolState['leaves'][number]>('GET',`demo_leave_requests?${scope}${studentScope}&order=from_day.desc`),
  role==='teacher'?Promise.resolve([]):rest<SchoolState['admissions'][number]>('GET',`demo_admissions?${scope}${parent?`&family_id=eq.${family.id}`:''}&order=created_at.desc`),
  role==='teacher'?Promise.resolve([]):rest<CampusVisit>('GET',`demo_campus_visits?${scope}${parent?`&family_id=eq.${family.id}`:''}&order=starts_at`),
  rest<SchoolState['notices'][number]>('GET',`demo_school_notices?${scope}${office?'':'&published=eq.true'}&order=created_at.desc`),
  rest<SchoolState['lessons'][number]>('GET',`demo_lessons?${scope}${classScope}&order=day,start_min`),
  office?rest<SchoolState['blocks'][number]>('GET',`demo_school_blocks?${scope}&order=starts_at`):Promise.resolve([]),
  office?rest<Conversation>('GET',`demo_conversations?${scope}&order=last_at.desc&limit=50`):Promise.resolve([]),
  office?rest<SchoolState['activity'][number]>('GET',`demo_events?${scope}&kind=like.school_*&order=at.desc&limit=30`):Promise.resolve([])
 ]);
 return {family,families,students:visibleStudents,classes:visibleClasses,teachers,settings:settings[0],attendance,homework,submissions,assessments:parent?assessments.map(a=>({...a,grades:Object.fromEntries(Object.entries(a.grades).filter(([id])=>visibleStudents.some(s=>s.id===id)))})):assessments,
  invoices,claims,leaves,admissions,visits,notices,lessons,blocks,conversations:await Promise.all(conversations.map(async c=>({...c,staff_mode:!!c.staff_mode,assigned_to:c.assigned_to??null,messages:await transcript(c.id)}))),activity,server_time:new Date().toISOString(),expires_at:b.expires_at};
}
