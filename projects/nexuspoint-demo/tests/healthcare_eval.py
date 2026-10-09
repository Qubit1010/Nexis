"""Connected healthcare integration checks. Creates an isolated fictional clinic,
archives its activity afterwards and preserves the real prospect's records.
Usage: python tests/healthcare_eval.py [base_url] [--ui] [--vercel]
"""
import concurrent.futures
import json
import secrets
import shutil
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
BASE=sys.argv[1] if len(sys.argv)>1 and not sys.argv[1].startswith('--') else 'http://localhost:4400'
ENV={}
for line in (ROOT.parents[1]/'.env').read_text(encoding='utf-8').splitlines():
    if '=' in line and not line.strip().startswith('#'):
        k,v=line.strip().split('=',1); ENV[k]=v.strip().strip('\"').strip("'")
PKT=timezone(timedelta(hours=5))
SLUG='healthcare-quality-check'
TOKEN=secrets.token_urlsafe(24)
VISITOR='healthcare-evaluation-patient'
passed=[]

def request(url,method='GET',body=None,headers=None):
    if '--vercel' in sys.argv and url.startswith(BASE+'/'):
        cli=Path(shutil.which('vercel.cmd')).parent/'node_modules/vercel/dist/vc.js'
        parts=urllib.parse.urlsplit(url)
        path=parts.path+('?' + parts.query if parts.query else '')
        args=[shutil.which('node'),str(cli),'curl',path,'--deployment',BASE,'--',
              '--silent','--show-error','--write-out','\n%{http_code}','--request',method,
              '--header','Content-Type: application/json']
        if body is not None:args+=['--data-binary',json.dumps(body)]
        result=subprocess.run(args,cwd=ROOT,capture_output=True,text=True,encoding='utf-8',timeout=90)
        assert result.returncode==0,result.stderr[-500:]
        data,_,status=result.stdout.rstrip().rpartition('\n')
        assert status.isdigit(),result.stdout[:250]
        try:data=json.loads(data)
        except ValueError:pass
        return int(status),data
    req=urllib.request.Request(url,method=method,data=json.dumps(body).encode() if body is not None else None,headers={'Content-Type':'application/json',**(headers or {})})
    try:
        with urllib.request.urlopen(req,timeout=90) as r:
            data=r.read().decode('utf-8')
            try:data=json.loads(data or 'null')
            except ValueError:pass
            return r.status,data
    except urllib.error.HTTPError as e:
        data=e.read().decode()
        try:data=json.loads(data)
        except ValueError:pass
        return e.code,data

def db(path,method='GET',body=None):
    status,data=request(ENV['SUPABASE_URL'].rstrip('/')+'/rest/v1/'+path,method,body,{'apikey':ENV['SUPABASE_SERVICE_ROLE_KEY'],'Authorization':'Bearer '+ENV['SUPABASE_SERVICE_ROLE_KEY'],'Prefer':'resolution=merge-duplicates,return=representation'})
    assert status<300,(status,str(data)[:250])
    return data

def api(body=None,role='patient',visitor=VISITOR,**params):
    fields={'slug':SLUG,'t':TOKEN,'visitor':visitor,'role':role,**params}
    if body is not None:return request(BASE+'/api/healthcare','POST',{**fields,**body})
    return request(BASE+'/api/healthcare?'+urllib.parse.urlencode(fields))

def chat(text,choice=None):return request(BASE+'/api/chat','POST',{'slug':SLUG,'t':TOKEN,'visitor':VISITOR,'text':text,**({'choice':choice} if choice else {})})
def check(name,condition):
    assert condition,name
    passed.append(name);print('PASS',name,flush=True)

def main():
    template=json.loads((ROOT.parent/'quetta-local-market/data/demos/saleem-medical-complex-5702.json').read_text(encoding='utf-8'))
    business={k:template[k] for k in ['profile','xray','site','roi','health']}
    business.update(slug=SLUG,token=TOKEN,code='QA123',sector='healthcare',name='[QA] Fictional clinic',expires_at=(datetime.now(timezone.utc)+timedelta(days=14)).isoformat())
    db('demo_businesses?on_conflict=slug','POST',business)
    db('rpc/demo_reset_healthcare','POST',{'p_slug':SLUG})
    try:
        status,state=api();check('patient seed and published history',status==200 and len(state['doctors'])==4 and len(state['records'])==1 and len(state['patients'])==1)
        patient=state['patient']['id'];doctor=state['doctors'][0]['id']
        if '--ui-only' in sys.argv:
            chat('Book a doctor appointment')
            ui_checks(patient)
            print(f'{len(passed)} focused browser checks passed.',flush=True)
            return
        date=(datetime.now(PKT)+timedelta(days=1)).date()
        for _ in range(14):
            status,available=api(doctorId=doctor,date=date.isoformat())
            if available.get('slots'):break
            date+=timedelta(days=1)
        slots=available['slots'];assert len(slots)>=5,available
        def booking(slot,request_id):return {'action':'book','doctorId':doctor,'start':slot,'mode':'video','requestId':request_id,'reason':'Fictional workflow check'}
        first=booking(slots[0],'qa-book-one')
        status,result=api(first);check('portal reservation',status==200)
        appointment=result['result'];aid=appointment['id']
        status,retry=api(first);check('identical retry returns the same booking',status==200 and retry['result']['id']==aid)
        status,_=api(booking(slots[1],'qa-book-one'));check('retry identifier cannot change the booking',status==409)
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
            results=list(pool.map(lambda i:api(booking(slots[2],f'qa-race-{i}')),[1,2]))
        check('simultaneous reservations have one winner',[r[0] for r in results].count(200)==1 and [r[0] for r in results].count(409)==1)
        _,current=api(doctorId=doctor,date=date.isoformat());check('occupied slot disappears from availability',slots[0] not in current['slots'])
        status,_=api({'action':'appointment','id':aid,'start':slots[1],'doctorId':doctor,'mode':'video'});check('atomic rescheduling succeeds',status==200)
        race_id=next(r[1]['result']['id'] for r in results if r[0]==200)
        status,_=api({'action':'appointment','id':aid,'start':slots[2]});check('conflicting reschedule is rejected',status==409)
        _,current=api();check('failed rescheduling retains existing booking',datetime.fromisoformat(next(a for a in current['appointments'] if a['id']==aid)['starts_at'])==datetime.fromisoformat(slots[1].replace('Z','+00:00')))
        status,_=api({'action':'schedule','doctorId':doctor,'start':slots[1],'end':(datetime.fromisoformat(slots[1].replace('Z','+00:00'))+timedelta(minutes=30)).isoformat()},role='clinic');check('blocking a reserved time is rejected',status==409)
        status,_=api({'action':'schedule','doctorId':doctor,'schedule':[]},role='clinic');check('working-hour changes cannot invalidate appointments',status==409)
        status,_=api({'action':'appointment','id':race_id,'status':'cancelled'});check('patient cancellation succeeds',status==200)
        _,current=api(doctorId=doctor,date=date.isoformat());check('cancelled slot becomes available',slots[2] in current['slots'])
        status,_=api({'action':'schedule','doctorId':doctor,'start':slots[2],'end':(datetime.fromisoformat(slots[2].replace('Z','+00:00'))+timedelta(minutes=30)).isoformat()},role='clinic');check('blocking a free time succeeds',status==200)
        status,_=api(booking(slots[2],'qa-blocked'));check('blocked slot cannot be reserved',status==409)
        status,_=api(booking((datetime.now(timezone.utc)-timedelta(days=1)).isoformat(),'qa-past'));check('past reservations are rejected',status==400)
        status,_=api(booking((datetime.now(timezone.utc)+timedelta(days=20)).isoformat(),'qa-future'));check('reservations beyond the horizon are rejected',status==400)
        status,_=api(t='wrong-token');check('invalid tokens are rejected',status==404)
        status,other=api(visitor='healthcare-another-visitor');check('another visitor cannot see patient appointments',status==200 and len(other['appointments'])==0)
        status,_=api({'action':'appointment','id':aid,'status':'cancelled'},visitor='healthcare-another-visitor');check('another patient cannot change this booking',status==404)
        status,_=api({'action':'book','patientId':patient,'doctorId':'saleem-medical-complex-5702-doctor-1','start':slots[3],'mode':'video','requestId':'qa-cross-clinic'});check('cross-business doctor is rejected',status==400)
        _,staff=api(role='doctor')
        own=next(r for r in staff['records'] if r['patient_id']==patient)
        data={**own['data'],'title':'QA fictional visit','notes':'Published during the connected demonstration.'}
        status,draft=api({'action':'record','patientId':patient,'doctorId':doctor,'appointmentId':aid,'data':data,'published':False},role='doctor');check('doctor saves draft',status==200)
        rid=draft['result']['id']
        _,current=api();check('patient cannot see draft',all(r['id']!=rid for r in current['records']))
        status,_=api({'action':'record','id':rid,'patientId':patient,'doctorId':doctor,'appointmentId':aid,'data':data,'published':True},role='doctor');check('doctor publishes record',status==200)
        _,current=api();check('published record reaches patient portal',any(r['id']==rid for r in current['records']))
        status,_=api({'action':'record','patientId':patient,'doctorId':doctor,'data':data});check('patient cannot write clinical records',status==400)
        _,today_slots=api(doctorId=doctor,date=datetime.now(PKT).date().isoformat())
        requested_day=datetime.now(PKT).date() if today_slots['slots'] else date
        status,result=chat('Book a doctor phone appointment on '+requested_day.isoformat());check('chat offers real sample doctor choices',status==200 and any(c['kind']=='doctor' for c in result['cards']))
        choice=next(c for c in result['cards'] if c['kind']=='doctor')
        status,result=chat(choice['label'],choice);check('chat offers stored availability',status==200 and any(c['kind']=='slot' for c in result['cards']))
        slot_choice=next(c for c in result['cards'] if c['kind']=='slot')
        check('chat retains the requested Pakistan local day',datetime.fromisoformat(slot_choice['value'].replace('Z','+00:00')).astimezone(PKT).date()==requested_day)
        status,fee=chat('What is the consultation fee?');check('fees go to staff during a booking conversation',status==200 and fee['stage']=='needs_human' and not fee.get('cards'))
        choice=next(c for c in result['cards'] if c['kind']=='slot')
        status,result=chat(choice['label'],choice);check('chat confirmation is backed by a saved appointment',status==200 and 'confirmed' in result['reply'])
        _,current=api();check('chat and portal share appointments',any(a['source']=='chat' for a in current['appointments']))
        chat_booking=next(a for a in current['appointments'] if a['source']=='chat')
        check('chat retains the requested consultation mode',chat_booking['mode']=='phone')
        _,reception=api(role='clinic');check('chat reservation reaches reception calendar',any(a['id']==chat_booking['id'] for a in reception['appointments']))
        _,doctor_view=api(role='doctor');check('chat reservation reaches doctor schedule',any(a['id']==chat_booking['id'] for a in doctor_view['appointments']))
        status,_=api({'action':'appointment','id':chat_booking['id'],'status':'checked_in'},role='clinic')
        check('chat reservation check-in follows Pakistan appointment day',status==(200 if requested_day==datetime.now(PKT).date() else 400))
        status,_=api({'action':'appointment','id':chat_booking['id'],'status':'in_consultation'},role='doctor');check('doctor starts the chat-booked consultation',status==200)
        status,visit=api({'action':'record','patientId':patient,'doctorId':doctor,'appointmentId':chat_booking['id'],'data':data,'published':True},role='doctor')
        _,portal=api();check('chat-booked visit publishes a linked patient report',status==200 and any(r['id']==visit['result']['id'] and r['appointment_id']==chat_booking['id'] for r in portal['records']))
        status,_=api({'action':'appointment','id':chat_booking['id'],'status':'completed'},role='doctor');check('doctor completes the chat-booked consultation',status==200)
        _,staff=api(role='clinic');cid=staff['conversations'][0]['id']
        status,_=api({'action':'conversation','id':cid,'staffMode':True,'assignedTo':'Reception'},role='clinic');check('reception takes over',status==200)
        status,result=chat('Can staff help me?');check('assistant stays paused during takeover',status==200 and result['reply'] is None)
        status,_=api({'action':'conversation','id':cid,'text':'Sample reception reply.'},role='clinic');check('staff message is saved',status==200)
        status,history=request(BASE+'/api/chat?'+urllib.parse.urlencode({'slug':SLUG,'t':TOKEN,'visitor':VISITOR}));check('patient receives staff reply in original chat',status==200 and history['messages'][-1]['source']=='staff')
        api({'action':'conversation','id':cid,'staffMode':False},role='clinic')
        status,result=chat('Book a doctor appointment');check('assistant resumes after handback',status==200 and result['reply'] is not None)
        for action in ['in_consultation','completed']:
            status,_=api({'action':'appointment','id':aid,'status':action},role='doctor');check('appointment transition '+action,status==200)
        status,_=api({'action':'schedule','doctorId':doctor,'schedule':[{'day':1,'start':'08:00','end':'16:00'}]},role='clinic');check('doctor schedule stays inside clinic opening hours',status==400)
        current_day=datetime.now(PKT).date().isoformat()
        tokens=[]
        for i in range(2):
            start=f'{current_day}T11:{i*30:02d}:00+05:00'
            created=db('demo_appointments','POST',{'slug':SLUG,'patient_id':patient,'doctor_id':state['doctors'][3]['id'],'starts_at':start,'ends_at':(datetime.fromisoformat(start)+timedelta(minutes=30)).isoformat(),'mode':'in_person','status':'confirmed','source':'sample','request_id':f'qa-queue-{i}'})[0]
            status,result=api({'action':'appointment','id':created['id'],'status':'checked_in'},role='clinic')
            check(f'check-in allocates queue token {i+1}',status==200 and result['result']['queue_number'] is not None)
            tokens.append(result['result']['queue_number'])
        check('queue tokens increase without collision',tokens[1]==tokens[0]+1)
        status,result=chat('Dr Unknownname ki availability kya hai?');check('unknown doctors go to staff',status==200 and result['stage']=='needs_human')
        status,result=chat('ڈاکٹر کی اپائنٹمنٹ بک کرنی ہے')
        doctor_choice=next(c for c in result['cards'] if c['kind']=='doctor')
        status,result=chat(doctor_choice['label'],doctor_choice);check('Urdu persists after selecting an English doctor label',status==200 and any('\u0600'<=ch<='\u06ff' for ch in result['reply']))
        if '--ui' in sys.argv:ui_checks(patient)
        db('demo_businesses?slug=eq.'+SLUG,'PATCH',{'expires_at':(datetime.now(timezone.utc)-timedelta(seconds=1)).isoformat()})
        status,_=api();check('expired demo cannot read clinic data',status==400)
        status,_=api(booking(slots[4],'qa-expired'));check('expired demo cannot write clinic data',status==400)
        status,_=request(BASE+'/api/event','POST',{'slug':SLUG,'t':TOKEN,'kind':'view'});check('expired demo cannot write outreach events',status==410)
        print(f'{len(passed)} integration checks passed.',flush=True)
    finally:
        db('rpc/demo_reset_healthcare','POST',{'p_slug':SLUG})
        db('demo_businesses?slug=eq.'+SLUG,'PATCH',{'expires_at':(datetime.now(timezone.utc)-timedelta(seconds=1)).isoformat()})
        print('QA activity archived. Prospect data untouched.',flush=True)

def ui_checks(patient):
    from playwright.sync_api import sync_playwright
    out=ROOT/'tests'/'qa'/'healthcare';out.mkdir(parents=True,exist_ok=True)
    with sync_playwright() as p:
        browser=p.chromium.launch()
        for size,(w,h) in {'desktop':(1440,1000),'mobile':(390,844)}.items():
            context=browser.new_context(viewport={'width':w,'height':h})
            context.add_init_script(f"localStorage.setItem('np-visitor-{SLUG}', '{VISITOR}');")
            page=context.new_page()
            errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
            for role,tab in [('patient','overview'),('patient','doctors'),('patient','records'),('clinic','calendar'),('clinic','inbox'),('doctor','overview')]:
                page.goto(BASE+f'/d/{SLUG}/{role}?t={TOKEN}&tab={tab}',wait_until='domcontentloaded')
                page.locator('.hc-loading').wait_for(state='hidden',timeout=60000)
                page.locator('.hc-error').count()==0 or (_ for _ in ()).throw(AssertionError('UI data error'))
                page.screenshot(path=str(out/f'{size}-{role}-{tab}.png'),full_page=True)
                overflow=page.evaluate('document.documentElement.scrollWidth > document.documentElement.clientWidth + 1')
                check(f'{size} {role}/{tab} fits viewport',not overflow)
            page.goto(BASE+f'/d/{SLUG}/patient?t={TOKEN}&lang=ur',wait_until='domcontentloaded')
            page.locator('.hc-loading').wait_for(state='hidden',timeout=60000)
            check(f'{size} Urdu layout is RTL',page.locator('.hc').get_attribute('dir')=='rtl')
            page.screenshot(path=str(out/f'{size}-urdu.png'),full_page=True)
            page.get_by_role('button',name='تھیم بدلیں').click()
            check(f'{size} dark theme switches',page.locator('.hc').get_attribute('data-clinic-theme')=='dark')
            page.screenshot(path=str(out/f'{size}-dark.png'),full_page=True)
            check(f'{size} has no browser runtime errors',not errors)
            context.close()
        browser_flow(browser,out)
        browser.close()

def browser_flow(browser,out):
    context=browser.new_context(viewport={'width':1440,'height':1000})
    context.add_init_script(f"localStorage.setItem('np-visitor-{SLUG}', '{VISITOR}');")
    page=context.new_page()
    def visit(role,tab):
        page.goto(BASE+f'/d/{SLUG}/{role}?t={TOKEN}&tab={tab}',wait_until='domcontentloaded')
        page.locator('.hc-loading').wait_for(state='hidden',timeout=60000)
    visit('patient','overview')
    page.locator('.hc-heading-actions .hc-btn').click()
    dialog=page.get_by_role('dialog')
    dialog.get_by_label('Consultation mode').select_option('video')
    page.locator('.hc-slots button').first.wait_for(timeout=30000)
    page.locator('.hc-slots button').last.click()
    dialog.get_by_role('button',name='Confirm demo booking',exact=True).click()
    dialog.wait_for(state='hidden',timeout=30000)
    check('browser booking saves and closes the dialog',True)
    visit('patient','appointments')
    page.locator('.hc-appointment').filter(has_text='Video call').get_by_role('button',name='Try demo call',exact=True).first.click()
    page.get_by_role('button',name='Start sample call',exact=True).click()
    page.get_by_role('button',name='Mute',exact=True).click()
    check('simulated microphone control changes state',page.get_by_role('button',name='Unmute',exact=True).get_attribute('aria-pressed')=='true')
    page.get_by_role('button',name='Camera off',exact=True).click()
    check('simulated camera control changes state',page.get_by_role('button',name='Camera on',exact=True).get_attribute('aria-pressed')=='true')
    page.screenshot(path=str(out/'desktop-simulated-call.png'))
    page.keyboard.press('Escape');check('Escape closes the call dialog',page.get_by_role('dialog').count()==0)
    visit('doctor','records')
    page.get_by_role('button',name='Create visit record',exact=True).click()
    page.get_by_label('Visit title',exact=True).fill('Browser published sample')
    page.get_by_label('Clinician notes',exact=True).fill('Fictional browser validation entry.')
    page.get_by_role('button',name='Save draft',exact=True).click()
    page.locator('.hc-success').wait_for(timeout=30000)
    page.keyboard.press('Escape')
    visit('patient','records')
    check('browser patient view hides an unpublished draft',page.get_by_role('heading',name='Browser published sample',exact=True).count()==0)
    visit('doctor','records')
    card=page.locator('.hc-record-card').filter(has=page.get_by_role('heading',name='Browser published sample',exact=True))
    card.get_by_role('button',name='Edit / publish',exact=True).click()
    page.get_by_role('button',name='Publish to patient',exact=True).click()
    page.get_by_role('dialog').wait_for(state='hidden',timeout=30000)
    visit('patient','records')
    page.get_by_role('heading',name='Browser published sample',exact=True).wait_for(timeout=30000)
    check('browser publication appears in patient history',True)
    card=page.locator('.hc-record-card').filter(has=page.get_by_role('heading',name='Browser published sample',exact=True))
    card.get_by_role('button',name='View report',exact=True).click()
    page.pdf(path=str(out/'sample-report.pdf'),format='A4',print_background=True)
    check('sample report exports as PDF',(out/'sample-report.pdf').read_bytes().startswith(b'%PDF'))
    page.keyboard.press('Escape')
    visit('clinic','inbox')
    page.get_by_role('button',name='Take over chat',exact=True).click()
    page.locator('.hc-inbox-composer input').wait_for(timeout=30000)
    page.locator('.hc-inbox-composer input').fill('Browser reception reply.')
    page.get_by_role('button',name='Send',exact=True).click()
    page.get_by_text('Browser reception reply.',exact=True).wait_for(timeout=30000)
    visit('patient','messages')
    page.get_by_text('Browser reception reply.',exact=True).wait_for(timeout=30000)
    check('browser staff takeover reply reaches patient messages',True)
    context.close()

if __name__=='__main__':main()
