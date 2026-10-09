"""Isolated connected school checks, including two businesses and two families.
python tests/school_eval.py [base_url] [--vercel]
Fixtures are archived afterwards; outreach analytics remain intact.
"""
import concurrent.futures,json,secrets,urllib.parse
from datetime import datetime,timedelta,timezone
import healthcare_eval as h
ROOT=h.ROOT;BASE=h.BASE;VISITOR='school-evaluation-family';passed=[]
def check(name,value):
 assert value,name
 passed.append(name);print('PASS',name,flush=True)
def fixture():
 template=json.loads((ROOT.parent/'quetta-local-market/data/demos/tameer-e-nau-public-college-ac62.json').read_text(encoding='utf-8'))
 b={k:template[k]for k in ['profile','xray','site','roi','health']}
 b.update(slug='school-qa-'+secrets.token_hex(4),token=secrets.token_urlsafe(20),code='E'+secrets.token_hex(4),sector='education',name='[QA] Fictional college',expires_at=(datetime.now(timezone.utc)+timedelta(days=14)).isoformat())
 h.db('demo_businesses','POST',b);return b
def cleanup(b):
 h.db('rpc/demo_school_action','POST',{'p_slug':b['slug'],'p_visitor':'system-reset','p_role':'system','p_action':'reset','p_data':{}})
 h.db('demo_businesses?slug=eq.'+b['slug'],'PATCH',{'expires_at':(datetime.now(timezone.utc)-timedelta(minutes=1)).isoformat()})
def api(b,body=None,role='parent',visitor=VISITOR,**params):
 p={'slug':b['slug'],'t':b['token'],'visitor':visitor,'role':role,**params}
 return h.request(BASE+'/api/school','POST',{**p,**body})if body is not None else h.request(BASE+'/api/school?'+urllib.parse.urlencode(p))
def chat(b,text,choice=None):
 return h.request(BASE+'/api/chat','POST',{'slug':b['slug'],'t':b['token'],'visitor':VISITOR,'text':text,**({'choice':choice}if choice else {})})
def main():
 a=fixture();b=fixture()
 try:
  status,s=api(a);check('college seed, linked children and published samples',status==200 and len(s['students'])==2 and all('FSc'in c['name']for c in s['classes'])and len(s['homework'])==2 and len(s['assessments'])==2)
  _,again=api(a);check('family and children persist after refresh',s['family']['id']==again['family']['id']and s['students']==again['students'])
  st=s['students'][0];cl=next(c for c in s['classes']if c['id']==st['class_id']);teacher=cl['teacher_id'];other_teacher=next(te['id']for te in s['teachers']if te['id']!=teacher)
  _,office=api(a,role='school');check('office sees synthetic families and classes',len(office['students'])>=6 and len(office['homework'])==4)
  _,ts=api(a,role='teacher',teacherId=teacher);check('teacher sees assigned class without fees or admissions',len(ts['classes'])==1 and not ts['invoices'] and not ts['claims'] and not ts['admissions'] and all(x['class_id']==cl['id']for x in ts['students']))
  check('parent grades exclude other families',all(set(ar['grades']).issubset({st['id']for st in s['students']})for ar in s['assessments']))
  _,other=api(a,visitor='school-other-family');check('families cannot read one another',not set(st['id']for st in s['students']).intersection(st['id']for st in other['students']))
  today=datetime.now(h.PKT).date().isoformat()
  attendance={'action':'attendance','teacherId':teacher,'classId':cl['id'],'day':today,'rows':[{'studentId':st['id'],'status':'present','note':'Sample attendance'}]}
  status,_=api(a,attendance,role='teacher');check('teacher records class attendance',status==200)
  _,current=api(a);check('attendance reaches parent',any(x['student_id']==st['id']and x['day']==today and x['status']=='present'for x in current['attendance']))
  status,_=api(a,attendance);check('parent cannot write attendance',status==400)
  status,_=api(a,{**attendance,'teacherId':other_teacher},role='teacher');check('teacher cannot write another class',status==404)
  status,_=api(a,{**attendance,'day':(datetime.now(h.PKT)+timedelta(days=1)).date().isoformat()},role='teacher');check('future attendance refused',status==400)
  wrong_class=next(child for child in other['students']if child['class_id']!=cl['id'])
  status,_=api(a,{**attendance,'rows':[{'studentId':st['id'],'status':'absent'},{'studentId':wrong_class['id'],'status':'present'}]},role='teacher');check('mixed wrong-class attendance rejects whole transaction',status==400)
  _,current=api(a);check('rejected batch leaves original attendance',next(x for x in current['attendance']if x['student_id']==st['id']and x['day']==today)['status']=='present')
  hw={'action':'homework','teacherId':teacher,'classId':cl['id'],'title':'QA published worksheet','subject':'Biology','instructions':'Synthetic worksheet questions','due':today,'requestId':'qa-homework-first'}
  status,out=api(a,hw,role='teacher');check('homework saves as draft',status==200 and not out['result']['published']);hid=out['result']['id']
  _,current=api(a);check('homework draft hidden from parents',all(x['id']!=hid for x in current['homework']))
  status,_=api(a,{'action':'publish','teacherId':teacher,'kind':'homework','id':hid},role='teacher');check('teacher explicitly publishes homework',status==200)
  _,current=api(a);check('published homework reaches parents',any(x['id']==hid for x in current['homework']))
  status,out=api(a,{'action':'submission','studentId':st['id'],'assignmentId':hid,'text':'Sample answer'});check('parent submits linked child homework',status==200);sid=out['result']['id']
  status,_=api(a,{'action':'submission','teacherId':teacher,'studentId':st['id'],'assignmentId':hid,'feedback':'Sample teacher review'},role='teacher');check('teacher reviews response',status==200)
  _,current=api(a);check('review feedback reaches parent',next(x for x in current['submissions']if x['id']==sid)['feedback']=='Sample teacher review')
  status,_=api(a,{'action':'submission','studentId':st['id'],'assignmentId':hid,'text':'Foreign family'},visitor='school-other-family');check('family cannot submit another child homework',status==404)
  assessment={'action':'assessment','teacherId':teacher,'classId':cl['id'],'title':'QA term assessment','subject':'Biology','total':50,'grades':{st['id']:45},'examDate':today,'comment':'Sample progress','requestId':'qa-assessment-first'}
  status,out=api(a,assessment,role='teacher');check('assessment saves as draft',status==200 and not out['result']['published']);aid=out['result']['id']
  _,current=api(a);check('assessment draft hidden from parents',all(x['id']!=aid for x in current['assessments']))
  status,_=api(a,{'action':'publish','teacherId':other_teacher,'kind':'assessment','id':aid},role='teacher');check('another teacher cannot publish results',status==404)
  status,_=api(a,{**assessment,'requestId':'qa-bad-grade','grades':{st['id']:51}},role='teacher');check('marks above total refused',status==400)
  status,_=api(a,{'action':'publish','teacherId':teacher,'kind':'assessment','id':aid},role='teacher');check('teacher publishes results',status==200)
  _,current=api(a);check('published marks reach linked parent',next(x for x in current['assessments']if x['id']==aid)['grades'][st['id']]==45)
  status,_=api(a,{**assessment,'id':aid,'requestId':'qa-edit-grade','grades':{}},role='teacher');check('editing results returns to draft and missing marks stay absent',status==200)
  _,current=api(a);check('edited draft disappears from parent',all(x['id']!=aid for x in current['assessments']))
  invoice=next(i for i in s['invoices']if i['student_id']==st['id'])
  claim={'action':'claim','id':invoice['id'],'reference':'QA-DEMO-REFERENCE','requestId':'qa-fee-claim-first'}
  with concurrent.futures.ThreadPoolExecutor(max_workers=2)as pool:results=list(pool.map(lambda _:api(a,claim),[1,2]))
  check('duplicate concurrent fee references create one claim',all(x[0]==200 for x in results)and results[0][1]['result']['id']==results[1][1]['result']['id']);cid=results[0][1]['result']['id']
  _,current=api(a);check('payment claim does not mark invoice paid',not next(i for i in current['invoices']if i['id']==invoice['id'])['paid'])
  status,_=api(a,{'action':'verify','id':cid,'status':'verified'});check('parent cannot verify payment',status==400)
  status,_=api(a,{**claim,'requestId':'qa-fee-other'});check('second pending payment refused',status==409)
  status,_=api(a,{'action':'verify','id':cid,'status':'verified','note':'Sample verified'},role='school');check('office verifies simulated payment',status==200)
  _,current=api(a);check('verified receipt and paid invoice reach parent',next(i for i in current['invoices']if i['id']==invoice['id'])['paid']and next(c for c in current['claims']if c['id']==cid)['verified_at'])
  status,_=api(a,{'action':'verify','id':cid,'status':'rejected'},role='school');check('verified claim cannot be re-reviewed',status==409)
  status,_=api(a,{'action':'void_invoice','id':invoice['id']},role='school');check('paid invoice cannot be voided',status==409)
  status,_=api(a,{**claim,'requestId':'qa-foreign-fee'},visitor='school-other-family');check('other family cannot pay invoice',status==404)
  date=(datetime.now(h.PKT)+timedelta(days=1)).date()
  for _ in range(7):
   _,avail=api(a,date=date.isoformat())
   if avail['slots']:break
   date+=timedelta(days=1)
  slots=avail['slots'];check('PKT availability supports split sessions',len(slots)>8 and datetime.fromisoformat(slots[0].replace('Z','+00:00')).astimezone(h.PKT).hour==8)
  def visit(key,start=slots[0]):return {'action':'visit','start':start,'requestId':key,'notes':'Sample campus visit'}
  with concurrent.futures.ThreadPoolExecutor(max_workers=2)as pool:results=list(pool.map(lambda n:api(a,visit('qa-visit-race-'+str(n))),[1,2]))
  check('simultaneous campus reservations one winner',sorted(x[0]for x in results)==[200,409]);visit_row=next(x[1]['result']for x in results if x[0]==200);vid=visit_row['id'];winner=next(n for n,x in zip([1,2],results)if x[0]==200)
  status,out=api(a,visit('qa-visit-race-'+str(winner)));check('booking retry returns same visit',status==200 and out['result']['id']==vid)
  status,_=api(a,visit('qa-visit-race-'+str(winner),slots[1]));check('changed retry refused',status==409)
  status,_=api(a,{'action':'block','start':slots[0],'end':slots[1],'reason':'Sample closure'},role='school');check('blocked times cannot invalidate a booking',status==409)
  status,_=api(a,{'action':'visit_status','id':vid,'start':slots[2]});check('atomic rescheduling moves visit',status==200)
  status,out=api(a,visit('qa-visit-released'));check('rescheduling releases old slot',status==200);new_vid=out['result']['id']
  status,_=api(a,{'action':'visit_status','id':vid,'start':slots[0]});check('reschedule conflict refused',status==409)
  _,current=api(a);check('failed reschedule retains previous time',datetime.fromisoformat(next(v for v in current['visits']if v['id']==vid)['starts_at'])==datetime.fromisoformat(slots[2].replace('Z','+00:00')))
  status,_=api(a,{'action':'visit_status','id':vid,'status':'cancelled'});check('parent cancels campus visit',status==200)
  status,_=api(a,visit('qa-visit-cancelled',slots[2]));check('cancellation releases slot',status==200)
  status,_=api(a,{'action':'block','start':slots[4],'end':slots[5],'reason':'Sample blocked office'},role='school');check('office blocks available time',status==200)
  status,_=api(a,visit('qa-visit-blocked',slots[4]));check('blocked slot refused',status==409)
  status,_=api(a,visit('qa-visit-past',(datetime.now(timezone.utc)-timedelta(days=1)).isoformat()));check('past slot refused',status==400)
  status,_=api(a,visit('qa-visit-beyond',(datetime.now(timezone.utc)+timedelta(days=20)).isoformat()));check('14-day horizon enforced',status==400)
  status,_=api(a,{'action':'visit_status','id':new_vid,'status':'completed'},role='school');check('visit cannot skip arrival',status==409)
  api(a,{'action':'visit_status','id':new_vid,'status':'arrived'},role='school');status,_=api(a,{'action':'visit_status','id':new_vid,'status':'completed'},role='school');check('office arrival and completion persist',status==200)
  status,_=api(a,{'action':'visit_status','id':vid,'status':'cancelled'},visitor='school-other-family');check('other family cannot change campus visit',status==404)
  leave={'action':'leave','studentId':st['id'],'from':date.isoformat(),'to':date.isoformat(),'reason':'Fictional family event','requestId':'qa-leave-first'}
  status,out=api(a,leave);check('parent requests sample leave',status==200);lid=out['result']['id']
  status,_=api(a,{'action':'leave_status','id':lid,'status':'approved'},role='school');check('office reviews leave',status==200)
  _,current=api(a);check('leave approval does not invent attendance',not any(x['day']==date.isoformat()and x['student_id']==st['id']for x in current['attendance']))
  status,out=api(a,{'action':'notice','title':'QA notice','body':'Fictional announcement','requestId':'qa-notice-first'},role='school');check('office saves announcement draft',status==200);nid=out['result']['id']
  _,current=api(a);check('notice draft hidden',all(n['id']!=nid for n in current['notices']))
  api(a,{'action':'publish','kind':'notice','id':nid},role='school');_,current=api(a);check('published notice reaches families',any(n['id']==nid for n in current['notices']))
  status,_=api(a,{'action':'lesson','classId':cl['id'],'lessonTeacherId':teacher,'day':1,'startMin':550,'endMin':580,'subject':'Conflict','room':'Sample room'},role='school');check('overlapping timetable lessons refused',status==409)
  status,out=chat(a,'Show sample fees');check('assistant offers own linked students',status==200 and all(c['kind']=='school_student'for c in out['cards']))
  choice=next(c for c in out['cards']if c['value']==st['id']);status,out=chat(a,choice['label'],choice);check('assistant fee answer uses stored invoice',status==200 and 'verified demo payment'in out['reply'])
  status,out=chat(a,'Admissions enquiry');check('chat collects fictional applicant',status==200 and 'name'in out['reply'])
  _,out=chat(a,'QA Applicant');choice=out['cards'][0];_,out=chat(a,choice['label'],choice);check('chat saves admissions enquiry',any(c['kind']=='school_visit'for c in out['cards']))
  choice=out['cards'][0];_,out=chat(a,choice['label'],choice);choice=out['cards'][0];_,out=chat(a,choice['label'],choice);choice=out['cards'][0];status,out=chat(a,choice['label'],choice);check('chat confirms only persisted campus reservation',status==200 and 'confirmed'in out['reply'])
  _,office=api(a,role='school');check('chat enquiry and visit reach office',any(v['source']=='chat'for v in office['visits'])and any(a['name']=='QA Applicant'for a in office['admissions']))
  conv=next(c for c in office['conversations']if c['visitor']==VISITOR);status,_=api(a,{'action':'conversation','id':conv['id'],'text':'Without takeover'},role='school');check('staff reply requires takeover',status==400)
  api(a,{'action':'conversation','id':conv['id'],'staffMode':True,'assignedTo':'Sample admissions desk'},role='school');status,out=chat(a,'Show my results');check('staff takeover pauses assistant',status==200 and out['reply']is None)
  status,_=api(a,{'action':'conversation','id':conv['id'],'text':'Sample office reply'},role='school');check('office replies in same transcript',status==200)
  api(a,{'action':'conversation','id':conv['id'],'staffMode':False},role='school');status,out=chat(a,'حاضری کا ریکارڈ');check('assistant resumes in Urdu',status==200 and any('\u0600'<=c<='\u06ff'for c in out['reply']))
  _,sb=api(b,role='school')
  for name,body,role in [('foreign student',{'action':'student','studentId':st['id'],'classId':sb['classes'][0]['id'],'name':'Foreign'},'school'),('foreign assessment',{'action':'publish','id':aid,'kind':'assessment'},'school'),('foreign payment',{'action':'verify','id':cid,'status':'verified'},'school'),('foreign visit',{'action':'visit_status','id':vid,'status':'cancelled'},'school'),('foreign conversation',{'action':'conversation','id':conv['id'],'staffMode':True},'school')]:
   status,_=api(b,body,role=role);check(name+' denied',status==404)
  status,_=api(a,t=b['token']);check('token cannot authorize other business',status==404)
  status,_=api(a,leave,t='invalid');check('invalid token cannot write',status==404)
  h.db('demo_businesses?slug=eq.'+b['slug'],'PATCH',{'expires_at':(datetime.now(timezone.utc)-timedelta(seconds=1)).isoformat()});status,_=api(b);check('expired token cannot read',status==410);status,_=api(b,{'action':'family'});check('expired token cannot write',status==410)
 finally:
  for biz in [a,b]:
   before=h.db('demo_events?slug=eq.'+biz['slug']+'&select=id');cleanup(biz);check('archive retains outreach analytics',bool(h.db('demo_school_archives?slug=eq.'+biz['slug']))and len(h.db('demo_events?slug=eq.'+biz['slug']+'&select=id'))==len(before))
 print(str(len(passed))+' school integration checks passed.',flush=True)
if __name__=='__main__':main()
