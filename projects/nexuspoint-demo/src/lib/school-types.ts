import { dayAfter, localDate } from './healthcare-types.ts';
export type SchoolRole='parent'|'school'|'teacher';
export type Family={id:string;visitor:string;name:string};
export type SchoolTeacher={id:string;name:string;subject:string};
export type SchoolClass={id:string;name:string;teacher_id:string;room:string};
export type Student={id:string;family_id:string;class_id:string;name:string;roll:string};
export type Attendance={id:string;student_id:string;class_id:string;day:string;status:'present'|'absent'|'late'|'excused';note:string};
export type Homework={id:string;class_id:string;teacher_id:string;title:string;subject:string;instructions:string;due:string;published:boolean};
export type Submission={id:string;assignment_id:string;student_id:string;text:string;feedback:string;status:'submitted'|'reviewed';updated_at:string};
export type Assessment={id:string;class_id:string;teacher_id:string;title:string;subject:string;total:number;grades:Record<string,number>;published:boolean;exam_date:string;comment:string};
export type Invoice={id:string;student_id:string;period:string;amount:number;due:string;status:'issued'|'void';paid:boolean};
export type FeeClaim={id:string;invoice_id:string;family_id:string;reference:string;status:'pending'|'verified'|'rejected';note:string;created_at:string;verified_at:string|null};
export type LeaveRequest={id:string;student_id:string;from_day:string;to_day:string;reason:string;status:'pending'|'approved'|'declined';note:string};
export type Admission={id:string;family_id:string;name:string;program:string;note:string;status:'submitted'|'reviewing'|'accepted'|'closed';created_at:string};
export type CampusVisit={id:string;family_id:string;starts_at:string;ends_at:string;status:'confirmed'|'arrived'|'completed'|'cancelled'|'no_show';notes:string;source:string};
export type SchoolNotice={id:string;title:string;body:string;published:boolean;created_at:string};
export type Lesson={id:string;class_id:string;teacher_id:string;day:number;start_min:number;end_min:number;subject:string;room:string};
export type SchoolSettings={hours:{day:number;start:number;end:number}[];seeded:boolean};
export type SchoolBlock={id:string;starts_at:string;ends_at:string;reason:string};
export type SchoolState={family:Family;families:Family[];students:Student[];classes:SchoolClass[];teachers:SchoolTeacher[];attendance:Attendance[];homework:Homework[];submissions:Submission[];assessments:Assessment[];invoices:Invoice[];claims:FeeClaim[];leaves:LeaveRequest[];admissions:Admission[];visits:CampusVisit[];notices:SchoolNotice[];lessons:Lesson[];settings:SchoolSettings;blocks:SchoolBlock[];conversations:import('./healthcare-types.ts').ClinicConversation[];activity:{kind:string;at:string;detail:Record<string,unknown>}[];server_time:string;expires_at:string};
export const feeMoney=(n:number)=>`PKR ${n.toLocaleString('en-US')}`;
export function campusSlots(date:string,settings:SchoolSettings,busy:{starts_at:string;ends_at:string}[],expires:string,now=new Date()){
 if(!/^\d{4}-\d{2}-\d{2}$/.test(date)||date<localDate(now)||date>dayAfter(localDate(now),13))return [];
 const midnight=new Date(`${date}T00:00:00+05:00`);if(!Number.isFinite(midnight.getTime())||localDate(midnight)!==date)return [];
 const day=new Date(`${date}T12:00:00+05:00`).getUTCDay(),slots:string[]=[];
 for(const h of settings.hours.filter(h=>h.day===day))for(let m=h.start;m+30<=h.end;m+=30){
  const start=midnight.getTime()+m*60000,end=start+1800000;
  if(start<=now.getTime()||end>new Date(expires).getTime())continue;
  if(!busy.some(b=>new Date(b.starts_at).getTime()<end&&new Date(b.ends_at).getTime()>start))slots.push(new Date(start).toISOString());
 }
 return [...new Set(slots)].sort();
}
export function attendanceSummary(rows:Attendance[]){
 const counted=rows.filter(r=>r.status!=='excused'),present=counted.filter(r=>r.status==='present'||r.status==='late').length;
 return {recorded:rows.length,present,absent:counted.length-present,percent:counted.length?Math.round(present/counted.length*100):null};
}
