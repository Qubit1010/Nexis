import { randomUUID } from 'node:crypto';
import { updateConversation,type Business,type Conversation } from './db.ts';
import { schoolAction,schoolAvailability,schoolState } from './school.ts';
import { attendanceSummary,feeMoney,type CampusVisit,type Admission } from './school-types.ts';
import { dayAfter,localDate,dateLabel,timeLabel,type Choice } from './healthcare-types.ts';
import { detectLang } from './scripted.ts';
import { urgentMessage } from './brain.ts';
export async function schoolChat(b:Business,c:Conversation,text:string,choice?:Choice){
 // Preserve the shared deterministic urgent-message handler, even during an active school flow.
 if(urgentMessage(text)){await updateConversation(c.id,{booking_context:{}});return null;}
 let ctx={...(c.booking_context??{})};
 const detected=detectLang(text),remembered=ctx.schoolLang;
 const lang=(choice||ctx.schoolFlow==='admission_name')&&['en','ur','roman'].includes(remembered??'')?remembered:detected;
 const say=(en:string,ur:string,roman:string)=>lang==='ur'?ur:lang==='roman'?roman:en;
 const wantsStaff=/\b(?:talk|speak|connect|transfer).*(?:person|human|staff|office|teacher)|insaan se|عملے سے بات|استاد سے بات/i.test(text);
 if(!choice&&!ctx.schoolFlow&&!wantsStaff&&!/fee|fees|paid|payment|challan|attendance|absent|result|marks|grade|homework|assignment|admission|enrol|enroll|campus|visit|book|leave|teacher|principal|complaint|bully|فیس|حاضری|نتائج|نمبر|ہوم ورک|داخلہ|ملاقات|چھٹی|شکایت|dakhla|baqi|hazri|chutti/i.test(text))return null;
 const s=await schoolState(b,c.visitor,'parent');
 const card=(kind:Choice['kind'],value:string,label:string):Choice=>({kind,value,label});
 const finish=async(reply:string,cards:Choice[]=[],stage='qualifying')=>{await updateConversation(c.id,{booking_context:{...ctx,schoolLang:lang}});return {reply,cards,stage,summary:'Connected school demo · '+(ctx.schoolFlow??'information')};};
 if(wantsStaff||/complaint|bully|principal|teacher.*(?:rude|abuse)|شکایت/i.test(text)){ctx={};return finish(say('I have flagged this conversation for the school office. Please share your concern; a staff member can take over. Notifications are simulated.','یہ گفتگو دفتر کے لیے نشان لگائی گئی ہے۔ اپنی شکایت بتائیں، عملہ جواب دے سکتا ہے۔ اطلاع صرف نمونہ ہے۔','Yeh guftagu office ke liye flag ho gayi. Apni shikayat batayein, staff jawab de sakta hai. Ittila sirf demo hai.'),[],'needs_human');}
 if(!choice){
  if(/campus|visit|book|ملاقات/i.test(text)){ctx={schoolFlow:'visit',requestId:randomUUID(),date:text.match(/\d{4}-\d{2}-\d{2}/)?.[0]??(/tomorrow|kal|کل/i.test(text)?dayAfter(localDate()):localDate())};}
  else if(/admission|enrol|dakhla|داخلہ/i.test(text)&&ctx.schoolFlow!=='admission_name'&&ctx.schoolFlow!=='admission_program')ctx={schoolFlow:'admission_name',requestId:randomUUID()};
  else if(/fee|paid|payment|challan|فیس|baqi/i.test(text))ctx={schoolFlow:'fees'};
  else if(/attendance|absent|حاضری|hazri/i.test(text))ctx={schoolFlow:'attendance'};
  else if(/result|marks|grade|نتائج|نمبر/i.test(text))ctx={schoolFlow:'results'};
  else if(/homework|assignment|ہوم ورک/i.test(text))ctx={schoolFlow:'homework'};
  else if(/leave|chutti|چھٹی/i.test(text))return finish(say('Use the parent portal to submit a sample leave request with dates and reason. The office reviews it; approval does not automatically change attendance.','والدین پورٹل میں تاریخ اور وجہ کے ساتھ نمونہ چھٹی کی درخواست دیں۔ دفتر جائزہ لے گا، حاضری خود بخود تبدیل نہیں ہوتی۔','Parent portal mein tareekh aur wajah ke saath sample chutti request dein. Office review karega; hazri khud nahi badlegi.'));
 }
 if(ctx.schoolFlow==='admission_name'){
  if(c.booking_context?.schoolFlow==='admission_name'&&!/admission|enrol|dakhla|داخلہ/i.test(text)){
   if(text.trim().length<2||text.length>80)return finish(say('Enter a short fictional applicant name.','مختصر فرضی طالب علم کا نام لکھیں۔','Mukhtasar farzi student ka naam likhein.'));
   ctx.name=text.trim();ctx.schoolFlow='admission_program';
  }else return finish(say('I can save an illustrative admissions enquiry. What fictional applicant name should I use? No actual admission is granted.','نمونہ داخلہ درخواست محفوظ کر سکتا ہوں۔ فرضی طالب علم کا نام کیا ہے؟ حقیقی داخلہ نہیں ہوگا۔','Sample dakhla request save kar sakta hoon. Farzi student ka naam kya hai? Asal dakhla nahi hoga.'));
 }
 if(ctx.schoolFlow==='admission_program'){
  if(choice?.kind!=='school_program')return finish(say('Choose an illustrative programme for this sample enquiry.','نمونہ درخواست کے لیے پروگرام منتخب کریں۔','Sample request ke liye programme chunein.'),s.classes.map(cl=>card('school_program',cl.id,cl.name)));
  const cl=s.classes.find(cl=>cl.id===choice.value);if(!cl)return finish(say('That programme is unknown. Please ask the office.','یہ پروگرام معلوم نہیں۔ دفتر سے رابطہ کریں۔','Yeh programme maloom nahi. Office se rabta karein.'),[],'needs_human');
  const a=await schoolAction<Admission>(b,c.visitor,'parent','admission',{name:ctx.name,program:cl.name,note:'Fictional chat enquiry',requestId:ctx.requestId});
  await updateConversation(c.id,{action:{type:'admission',details:[{key:'Sample application',value:a.id},{key:'Programme',value:cl.name}]}});
  ctx={};return finish(say('Your sample admissions enquiry is saved for office review. It appears in the parent portal and office dashboard. Would you like to book a campus visit?','نمونہ داخلہ درخواست دفتر کے جائزے کے لیے محفوظ ہے۔ والدین اور دفتر پورٹل میں موجود ہے۔ کیمپس ملاقات بک کرنا چاہتے ہیں؟','Sample dakhla request office review ke liye save hai. Parent aur office portal mein nazar aayegi. Campus visit book karna chahenge?'),[card('school_visit','visit',say('Book a campus visit','کیمپس ملاقات بک کریں','Campus visit book karein'))],'warm');
 }
 if(choice?.kind==='school_visit')ctx={schoolFlow:'visit',requestId:randomUUID(),date:dayAfter(localDate())};
 if(ctx.schoolFlow==='visit'){
  if(choice?.kind==='school_time')ctx.start=choice.value;
  if(choice?.kind==='school_confirm'){
   if(!ctx.start)return finish(say('Choose an available time first.','پہلے دستیاب وقت منتخب کریں۔','Pehle available waqt chunein.'));
   try{
    const v=await schoolAction<CampusVisit>(b,c.visitor,'parent','visit',{start:ctx.start,requestId:ctx.requestId,source:'chat',notes:'Fictional admissions campus visit'});
    await updateConversation(c.id,{action:{type:'visit',details:[{key:'Sample campus visit',value:v.id},{key:'Time (PKT)',value:dateLabel(v.starts_at)+' '+timeLabel(v.starts_at)}]}});
    ctx={};return finish(say('Sample campus visit confirmed for '+dateLabel(v.starts_at)+' at '+timeLabel(v.starts_at)+' PKT. Saved in your portal and office calendar.','نمونہ کیمپس ملاقات محفوظ ہو گئی، '+dateLabel(v.starts_at,'ur')+' '+timeLabel(v.starts_at,'ur')+'۔','Sample campus visit '+dateLabel(v.starts_at)+' '+timeLabel(v.starts_at)+' PKT par confirm hai. Parent aur office calendar mein save hai.'),[],'warm');
   }catch{delete ctx.start;ctx.requestId=randomUUID();return finish(say('That time could not be reserved. Please choose a fresh slot or ask the office.','یہ وقت محفوظ نہیں ہو سکا۔ نیا وقت منتخب کریں یا دفتر سے رابطہ کریں۔','Yeh waqt reserve nahi hua. Naya waqt chunein ya office se rabta karein.'),[card('school_visit','visit',say('Check availability','دستیاب اوقات','Available waqt'))]);}
  }
  if(ctx.start)return finish(say('Confirm a fictional campus visit on '+dateLabel(ctx.start)+' at '+timeLabel(ctx.start)+' PKT?','کیا '+dateLabel(ctx.start,'ur')+' '+timeLabel(ctx.start,'ur')+' پر نمونہ ملاقات محفوظ کریں؟','Kya '+dateLabel(ctx.start)+' '+timeLabel(ctx.start)+' PKT par sample visit save karein?'),[card('school_confirm','confirm',say('Confirm campus visit','ملاقات کی تصدیق','Visit confirm karein'))]);
  const d=text.match(/\d{4}-\d{2}-\d{2}/)?.[0];if(d)ctx.date=d;
  let slots=await schoolAvailability(b,ctx.date??localDate());
  if(!slots.length&&ctx.date===localDate()){ctx.date=dayAfter(localDate());slots=await schoolAvailability(b,ctx.date);}
  return finish(say('Available sample office slots on '+ctx.date+'. All times PKT. Send a YYYY-MM-DD date to change the day.','نمونہ دستیاب اوقات، '+ctx.date+'۔ تمام اوقات پاکستانی ہیں۔ دن بدلنے کے لیے YYYY-MM-DD لکھیں۔','Sample office slots '+ctx.date+' par. Tamam waqt PKT hain. Din badalne ke liye YYYY-MM-DD likhein.'),slots.slice(0,12).map(x=>card('school_time',x,timeLabel(x,lang))));
 }
 if(['fees','attendance','results','homework'].includes(ctx.schoolFlow)){
  if(choice?.kind==='school_student')ctx.student=choice.value;
  else {const matched=s.students.find(st=>text.toLowerCase().includes(st.name.toLowerCase()));if(matched)ctx.student=matched.id;}
  const st=s.students.find(st=>st.id===ctx.student);
  if(!st)return finish(say('Choose a linked fictional student. I only show this demo family’s recorded information; other students go to the office.','منسلک فرضی طالب علم منتخب کریں۔ صرف اس نمونہ خاندان کے ریکارڈ دکھا سکتا ہوں۔ دوسرے طلبہ کے لیے دفتر سے رابطہ کریں۔','Linked farzi student chunein. Sirf is demo family ke records dikhata hoon; doosre students ke liye office se rabta karein.'),s.students.map(st=>card('school_student',st.id,st.name+' · '+s.classes.find(cl=>cl.id===st.class_id)?.name)));
  let reply='';
  if(ctx.schoolFlow==='fees'){
   const rows=s.invoices.filter(i=>i.student_id===st.id&&i.status==='issued');
   const facts=rows.map(i=>i.period+': '+feeMoney(i.amount)+' · '+(i.paid?'verified demo payment':s.claims.some(c=>c.invoice_id===i.id&&c.status==='pending')?'awaiting office verification':'pending')+' · due '+i.due).join('; ');
   reply=say(st.name+' · '+(facts||'No fee invoice recorded.')+' These are fictional fees. Saying “paid” does not verify payment; submit a demo reference in the portal for office review.',st.name+' · '+(facts||'فیس ریکارڈ موجود نہیں۔')+' یہ فرضی فیس ہے۔ ادائیگی کی تصدیق دفتر کرے گا۔',st.name+' · '+(facts||'Fee record maujood nahi.')+' Yeh farzi fees hain. Paid kehne se tasdeeq nahi hoti; portal mein demo reference dein, office review karega.');
  }else if(ctx.schoolFlow==='attendance'){
   const rows=s.attendance.filter(a=>a.student_id===st.id),sum=attendanceSummary(rows);
   const facts=sum.recorded?sum.present+' present/late, '+sum.absent+' absent, '+sum.recorded+' recorded days. Latest: '+rows[0].day+' '+rows[0].status:'No attendance recorded';
   reply=say(st.name+' · '+facts+'. Unrecorded days are unknown, not absences.',st.name+' · '+facts+'۔ بغیر ریکارڈ دن کو غیر حاضری نہیں کہا جائے گا۔',st.name+' · '+facts+'. Jis din ka record nahi, woh ghair hazri nahi hai.');
  }else if(ctx.schoolFlow==='results'){
   const rows=s.assessments.filter(a=>a.class_id===st.class_id);
   const facts=rows.map(a=>a.title+': '+(a.grades[st.id]===undefined?'not recorded':a.grades[st.id]+'/'+a.total)+' · '+a.exam_date).join('; ');
   reply=say(st.name+' · '+(facts||'No published results.')+' Only published, recorded marks appear here.',st.name+' · '+(facts||'شائع شدہ نتائج موجود نہیں۔')+' صرف شائع شدہ ریکارڈ دکھایا جاتا ہے۔',st.name+' · '+(facts||'Published results nahi.')+' Sirf published recorded marks dikhaye jaate hain.');
  }else{
   const facts=s.homework.filter(h=>h.class_id===st.class_id).map(h=>h.title+' · due '+h.due).join('; ');
   reply=say(st.name+' · '+(facts||'No published homework.')+' Submit a sample response in the parent portal.',st.name+' · '+(facts||'شائع شدہ ہوم ورک موجود نہیں۔')+' پورٹل میں نمونہ جواب دیں۔',st.name+' · '+(facts||'Published homework nahi.')+' Parent portal mein sample jawab dein.');
  }
  ctx={};return finish(reply,[],'warm');
 }
 ctx={};return finish(say('The school office can confirm that information. Please use the parent portal for recorded attendance, fees, homework and results.','دفتر اس معلومات کی تصدیق کرے گا۔ حاضری، فیس، ہوم ورک اور نتائج والدین پورٹل میں دیکھیں۔','Office is maloomat ki tasdeeq karega. Hazri, fee, homework aur results parent portal mein dekhein.'),[],'needs_human');
}
