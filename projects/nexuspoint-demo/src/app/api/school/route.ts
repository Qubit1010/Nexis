import { NextResponse } from 'next/server';
import { authorised,expired,getBusiness,rest,logEvent,type Conversation } from '@/lib/db';
import { schoolAction,schoolAvailability,schoolState } from '@/lib/school';
import type { SchoolRole } from '@/lib/school-types';
export const dynamic='force-dynamic';
const json=(data:unknown,status=200)=>NextResponse.json(data,{status,headers:{'Cache-Control':'no-store'}});
const bad=(m:string):never=>{throw new Error('INVALID: '+m)};
const uuid=(v:unknown)=>typeof v==='string'&&/^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i.test(v);
const day=(v:unknown)=>typeof v==='string'&&/^\d{4}-\d{2}-\d{2}$/.test(v)&&Number.isFinite(Date.parse(v))&&new Date(v).toISOString().slice(0,10)===v;
const instant=(v:unknown)=>typeof v==='string'&&/[zZ]|[+-]\d{2}:\d{2}$/.test(v)&&Number.isFinite(Date.parse(v));
function text(d:Record<string,unknown>,key:string,max=2000,required=false){const v=d[key];if(required&&(typeof v!=='string'||!v.trim()))bad('Enter '+key);if(v!==undefined&&(typeof v!=='string'||v.length>max))bad('Invalid '+key);}
async function access(p:Record<string,unknown>){
 if(typeof p.slug!=='string'||typeof p.t!=='string')bad('Invalid demo link');
 const b=await getBusiness(p.slug as string);if(!authorised(b,p.t as string)||b.sector!=='education')throw new Error('NOT_FOUND: Education demo not found');
 if(expired(b))throw new Error('EXPIRED: This preview has expired');
 if(typeof p.visitor!=='string'||!/^[a-zA-Z0-9_-]{8,64}$/.test(p.visitor)||!['parent','school','teacher'].includes(p.role as string))bad('Invalid demo session');
 return {b,visitor:p.visitor as string,role:p.role as SchoolRole};
}
function error(e:unknown){const m=e instanceof Error?e.message:'';const match=m.match(/(INVALID|CONFLICT|NOT_FOUND|EXPIRED): ([^"\\]+)/);return json({error:match?.[2]??'School connection problem. Please try again.'},match?({INVALID:400,CONFLICT:409,NOT_FOUND:404,EXPIRED:410}[match[1]]??500):500)}
export async function GET(req:Request){try{
 const p=Object.fromEntries(new URL(req.url).searchParams),{b,visitor,role}=await access({...p,role:p.role??'parent'});
 if(p.teacherId&&!uuid(p.teacherId))bad('Invalid teacher');
 if(p.date){if(!day(p.date))bad('Choose a valid day');return json({slots:await schoolAvailability(b,p.date)});}
 return json(await schoolState(b,visitor,role,p.teacherId));
}catch(e){return error(e)}}
export async function POST(req:Request){try{
 const p=await req.json().catch(()=>bad('Invalid request'));if(JSON.stringify(p).length>80000)bad('Request is too large');
 const {b,visitor,role}=await access({...p,role:p.role??'parent'}),action=p.action;
 const d={...p};for(const k of ['slug','t','visitor','role','action'])delete d[k];
 if(role==='teacher'&&!uuid(d.teacherId))bad('Choose a sample teacher');
 for(const k of ['id','teacherId','studentId','classId','assignmentId','lessonTeacherId'])if(d[k]!==undefined&&!uuid(d[k]))bad('Invalid '+k);
 if(d.requestId!==undefined&&(typeof d.requestId!=='string'||d.requestId.length<8||d.requestId.length>100))bad('Retry identifier required');
 for(const k of ['title','subject','period','name','program','room','reference','assignedTo'])text(d,k,k==='assignedTo'?80:150);
 for(const k of ['text','instructions','feedback','comment','body'])text(d,k,3000);
 for(const k of ['notes','note','reason'])text(d,k,600);
 if(action==='attendance'){
  if(!day(d.day)||!uuid(d.classId)||!Array.isArray(d.rows)||!d.rows.length||d.rows.length>100||d.rows.some((r:Record<string,unknown>)=>!r||!uuid(r.studentId)||!['present','absent','late','excused'].includes(r.status as string)||r.note!==undefined&&(typeof r.note!=='string'||r.note.length>300)))bad('Choose a class, recorded day and valid attendance rows');
 }
 if(action==='homework'||action==='assessment'){
  if(!uuid(d.classId))bad('Choose a class');text(d,'title',150,true);text(d,'subject',150,true);
  if(action==='homework'){if(!day(d.due))bad('Choose a due date');text(d,'instructions',3000,true);}
  else {if(!day(d.examDate)||!Number.isInteger(d.total)||d.total<1||d.total>1000||!d.grades||Array.isArray(d.grades)||typeof d.grades!=='object'||Object.entries(d.grades).some(([k,v])=>!uuid(k)||typeof v!=='number'||!Number.isFinite(v)||v<0||v>d.total))bad('Enter an exam date, total and valid marks');}
 }
 if(action==='publish'&&(!uuid(d.id)||!['homework','assessment','notice'].includes(d.kind)))bad('Choose a draft to publish');
 if(action==='submission'){if(!uuid(d.studentId)||!uuid(d.assignmentId))bad('Choose student and homework');text(d,role==='parent'?'text':'feedback',3000,true);}
 if(action==='invoice'){if(!uuid(d.studentId)||!day(d.due)||!Number.isInteger(d.amount)||d.amount<1||d.amount>1000000)bad('Enter student, sample amount and due date');text(d,'period',150,true);}
 if(action==='claim'){if(!uuid(d.id))bad('Choose an invoice');text(d,'reference',150,true);}
 if(action==='verify'&&(!uuid(d.id)||!['verified','rejected'].includes(d.status)))bad('Choose a payment and review outcome');
 if(action==='void_invoice'&&!uuid(d.id))bad('Choose an invoice');
 if(action==='leave'){if(!uuid(d.studentId)||!day(d.from)||!day(d.to)||d.to<d.from)bad('Choose valid leave dates');text(d,'reason',600,true);}
 if(action==='leave_status'&&(!uuid(d.id)||!['approved','declined'].includes(d.status)))bad('Choose a request and review outcome');
 if(action==='admission'){text(d,'name',80,true);text(d,'program',150,true);}
 if(action==='admission_status'&&(!uuid(d.id)||!['reviewing','accepted','closed'].includes(d.status)))bad('Choose an application status');
 if(action==='visit'&&!instant(d.start))bad('Choose a campus visit time');
 if(action==='visit_status'&&(!uuid(d.id)||(d.start!==undefined?!instant(d.start):!['arrived','completed','cancelled','no_show'].includes(d.status))))bad('Choose a valid visit action');
 if(action==='block'&&!d.id&&(!instant(d.start)||!instant(d.end)))bad('Choose a blocked interval');
 if(action==='notice'){text(d,'title',150,true);text(d,'body',3000,true);}
 if(action==='student'){if(!uuid(d.classId))bad('Choose class');text(d,'name',80,true);}
 if(action==='lesson'&&(!uuid(d.classId)||!d.id&&(!uuid(d.lessonTeacherId)||!Number.isInteger(d.day)||d.day<0||d.day>6||!Number.isInteger(d.startMin)||!Number.isInteger(d.endMin)||d.startMin<0||d.endMin>1440||d.endMin<=d.startMin)))bad('Enter a valid class, teacher and lesson time');
 if(action==='conversation'){
  if(role!=='school'||!uuid(d.id))bad('Use the school office inbox');
  const scope=`slug=eq.${encodeURIComponent(b.slug)}&id=eq.${d.id}`;
  const c=(await rest<Conversation>('GET',`demo_conversations?${scope}&limit=1`))[0];if(!c)throw new Error('NOT_FOUND: Conversation not found');
  if(d.text){if(!c.staff_mode)bad('Take over before replying');await rest('POST','demo_messages',{conversation_id:c.id,role:'business',content:d.text,source:'staff'},'return=minimal');}
  const patch:Record<string,unknown>={last_at:new Date().toISOString()};
  if(typeof d.staffMode==='boolean'){patch.staff_mode=d.staffMode;patch.handoff=d.staffMode;}
  if(d.assignedTo!==undefined)patch.assigned_to=d.assignedTo||null;
  await rest('PATCH',`demo_conversations?${scope}`,patch,'return=minimal');return json({result:{ok:true}});
 }
 if(action==='reminder'){if(role!=='school')bad('Use the office workspace');await logEvent(b.slug,'school_reminder',{message:d.note??'Sample fee follow-up',simulated:true});return json({result:{ok:true}});}
 if(!['family','student','attendance','homework','assessment','publish','submission','invoice','claim','verify','void_invoice','leave','leave_status','admission','admission_status','visit','visit_status','block','notice','lesson'].includes(action))bad('Unknown action');
 return json({result:await schoolAction(b,visitor,role,action,d)});
}catch(e){return error(e)}}
