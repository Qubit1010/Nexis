"""Isolated synthetic restaurant checks. Archive fixtures and retain analytics.
python tests/restaurant_eval.py [base_url] [--vercel] [--ui]
"""
import concurrent.futures,json,secrets,sys,urllib.parse
from datetime import datetime,timedelta,timezone
import healthcare_eval as h
ROOT=h.ROOT;BASE=h.BASE;TOKEN=secrets.token_urlsafe(20);SLUG='restaurant-qa-'+secrets.token_hex(4);VISITOR='restaurant-test-guest';passed=[]
def check(name,value):
 assert value,name
 passed.append(name);print('PASS',name,flush=True)
def api(body=None,role='customer',visitor=VISITOR,**params):
 fields={'slug':SLUG,'t':TOKEN,'visitor':visitor,'role':role,**params}
 return h.request(BASE+'/api/restaurant','POST',{**fields,**body}) if body is not None else h.request(BASE+'/api/restaurant?'+urllib.parse.urlencode(fields))
def chat(text,choice=None):return h.request(BASE+'/api/chat','POST',{'slug':SLUG,'t':TOKEN,'visitor':VISITOR,'text':text,**({'choice':choice}if choice else {})})
def main():
 template=json.loads((ROOT.parent/'quetta-local-market/data/demos/usmania-restaurant-69ac.json').read_text(encoding='utf-8'))
 b={k:template[k]for k in ['profile','xray','site','roi','health']};b.update(slug=SLUG,token=TOKEN,code='R'+secrets.token_hex(3).upper(),sector='food',name='[QA] Fictional restaurant',expires_at=(datetime.now(timezone.utc)+timedelta(days=14)).isoformat())
 h.db('demo_businesses','POST',b)
 try:
  status,s=api();check('seeded menu, tables and persistent guest',status==200 and len(s['menu'])==9 and len(s['tables'])==6 and not s['orders'])
  _,s2=api();check('guest remains connected after refresh',s['customer']['id']==s2['customer']['id'])
  item=s['menu'][0];table=s['tables'][-1]
  def order(rid='qa-order-first',**values):return {'action':'order','items':[{'itemId':item['id'],'quantity':2,'spice':'hot','notes':'Fictional preference'}],'mode':'pickup','notes':'Fictional test order','requestId':rid,**values}
  first=order(total=1);status,out=api(first);check('authoritative price and preferences',status==200 and out['result']['total']==item['price']*2 and out['result']['items'][0]['spice']=='hot');oid=out['result']['id']
  status,out=api(first);check('duplicate order returns same ticket',status==200 and out['result']['id']==oid)
  status,_=api(order('qa-order-first',mode='delivery',address='Sample Quetta Street'));check('retry key cannot change order',status==409)
  with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:results=list(pool.map(lambda _:api(order('qa-order-concurrent')),[1,2]))
  check('concurrent identical submissions create one ticket',all(x[0]==200 for x in results) and results[0][1]['result']['id']==results[1][1]['result']['id'])
  _,manager=api(role='restaurant');check('order reaches manager',any(o['id']==oid for o in manager['orders']))
  _,kitchen=api(role='kitchen');check('kitchen gets tickets without addresses or guest list',any(o['id']==oid for o in kitchen['orders']) and not kitchen['customers'] and all(not o['address'] for o in kitchen['orders']))
  status,_=api({'action':'order_status','id':oid,'status':'ready'},role='restaurant');check('status cannot skip preparation',status==409)
  status,_=api({'action':'order_status','id':oid,'status':'accepted'},role='restaurant');check('manager accepts ticket',status==200)
  status,_=api({'action':'order_status','id':oid,'status':'cancelled'});check('guest cannot cancel accepted order',status==409)
  status,_=api({'action':'order_status','id':oid,'status':'preparing'},role='kitchen');check('kitchen starts preparing',status==200)
  status,_=api({'action':'order_status','id':oid,'status':'ready'},role='kitchen');check('kitchen marks ready',status==200)
  status,_=api({'action':'order_status','id':oid,'status':'completed'},role='kitchen');check('kitchen cannot complete handoff',status==400)
  status,_=api({'action':'order_status','id':oid,'status':'completed'},role='restaurant');check('manager completes pickup',status==200)
  status,_=api({'action':'payment','id':oid},role='restaurant');check('simulated payment recorded',status==200)
  _,current=api();saved=next(o for o in current['orders']if o['id']==oid);check('customer gets full timeline',len(saved['timeline'])==5 and saved['payment']=='paid_demo')
  status,_=api({'action':'menu','id':item['id'],'price':item['price']+50},role='restaurant');check('manager edits sample price',status==200)
  _,current=api();check('receipt retains original price',next(o for o in current['orders']if o['id']==oid)['total']==item['price']*2)
  status,_=api({'action':'menu','id':item['id'],'available':False},role='restaurant');check('manager marks sold out',status==200)
  status,_=api(order('qa-sold-out'));check('sold out items refused',status==409)
  api({'action':'menu','id':item['id'],'available':True},role='restaurant')
  status,_=api({'action':'settings','accepting':False},role='restaurant');check('manager pauses orders',status==200)
  status,_=api(order('qa-paused'));check('paused ordering refuses checkout',status==409)
  api({'action':'settings','accepting':True},role='restaurant')
  _,out=api(order('qa-cancel'));status,_=api({'action':'order_status','id':out['result']['id'],'status':'cancelled'});check('guest cancels newly placed order',status==200)
  status,_=api(order('qa-no-address',mode='delivery'));check('delivery requires address',status==400)
  status,out=api(order('qa-delivery',mode='delivery',address='Sample House 12, Quetta'));delivery_id=out['result']['id']
  for st,role in [('accepted','restaurant'),('preparing','kitchen'),('ready','kitchen'),('out_for_delivery','restaurant'),('completed','restaurant')]:
   status,out=api({'action':'order_status','id':delivery_id,'status':st},role=role);assert status==200,(st,status,out)
  check('delivery has separate handoff sequence',status==200)
  date=(datetime.now(h.PKT)+timedelta(days=1)).date().isoformat();status,a=api(date=date,party=8);check('PKT availability next 14 days',status==200 and a['slots'] and datetime.fromisoformat(a['slots'][0].replace('Z','+00:00')).astimezone(h.PKT).hour==12);slots=a['slots']
  def reserve(rid,start=slots[0]):return {'action':'reserve','start':start,'party':8,'tableId':table['id'],'requestId':rid}
  with concurrent.futures.ThreadPoolExecutor(max_workers=2)as pool:results=list(pool.map(lambda i:api(reserve('qa-table-race-'+str(i))),[1,2]))
  check('simultaneous reservations one winner',sorted(x[0]for x in results)==[200,409]);reservation=next(x[1]['result']for x in results if x[0]==200);rid=reservation['id'];winner=next(i for i,x in zip([1,2],results)if x[0]==200)
  status,out=api(reserve('qa-table-race-'+str(winner)));check('table retry returns same booking',status==200 and out['result']['id']==rid)
  status,_=api(reserve('qa-table-overlap',slots[1]));check('90 minute overlap refused',status==409)
  status,_=api({'action':'table','id':table['id'],'active':False},role='restaurant');check('cannot block reserved table',status==409)
  status,_=api({'action':'settings','openMin':900,'closeMin':1440},role='restaurant');check('hours cannot invalidate reservation',status==409)
  status,_=api({'action':'reservation','id':rid,'start':slots[4]});check('atomic table reschedule',status==200)
  status,_=api(reserve('qa-released'));check('reschedule releases old time',status==200)
  status,_=api({'action':'reservation','id':rid,'start':slots[0]});check('conflicting move refused',status==409)
  _,current=api();check('failed move retains booking',datetime.fromisoformat(next(r for r in current['reservations']if r['id']==rid)['starts_at'])==datetime.fromisoformat(slots[4].replace('Z','+00:00')))
  status,_=api({'action':'reservation','id':rid,'status':'seated'},role='restaurant');check('future booking cannot seat today',status==400)
  status,_=api({'action':'reservation','id':rid,'status':'cancelled'});check('guest cancels table',status==200)
  status,_=api(reserve('qa-after-cancel',slots[4]));check('cancellation releases space',status==200)
  status,_=api(reserve('qa-past',(datetime.now(timezone.utc)-timedelta(days=1)).isoformat()));check('past time refused',status==400)
  status,_=api(reserve('qa-beyond',(datetime.now(timezone.utc)+timedelta(days=20)).isoformat()));check('horizon enforced',status==400)
  status,_=api(order('qa-cross-menu',items=[{'itemId':'00000000-0000-0000-0000-000000000001','quantity':1,'spice':'medium','notes':''}]));check('unknown menu item refused',status==400)
  status,_=api(t='invalid');check('invalid token refused',status==404)
  _,other=api(visitor='restaurant-other-visitor');check('other guest cannot read history',not other['orders']and not other['reservations'])
  status,_=api({'action':'order_status','id':oid,'status':'cancelled'},visitor='restaurant-other-visitor');check('other guest cannot change order',status==404)
  status,_=api({'action':'reservation','id':rid,'status':'cancelled'},visitor='restaurant-other-visitor');check('other guest cannot change table',status==404)
  status,_=api({'action':'menu','id':item['id'],'available':False});check('guest cannot modify menu',status==400)
  status,out=chat('2 chicken karahi and 4 naan');check('chat uses quantities and sample menu',status==200 and any(c['kind']=='food_mode'for c in out['cards']));mode=next(c for c in out['cards']if c['value']=='pickup');_,out=chat(mode['label'],mode);confirm=next(c for c in out['cards']if c['kind']=='food_confirm');status,out=chat(confirm['label'],confirm);check('chat confirms persisted order',status==200 and 'saved' in out['reply'])
  _,current=api();co=next(o for o in current['orders']if o['source']=='chat');check('chat order reaches portal',sum(x['quantity']for x in co['items'])==6)
  status,out=chat('Reserve a table for 4 on '+date);check('chat offers stored table availability',status==200 and any(c['kind']=='table_time'for c in out['cards']));choice=out['cards'][0];_,out=chat(choice['label'],choice);status,out=chat(out['cards'][0]['label'],out['cards'][0]);check('chat table booking saved',status==200 and 'confirmed' in out['reply'])
  status,out=chat('I have a dairy allergy');check('allergy questions handed to staff',status==200 and out['stage']=='needs_human')
  _,manager=api(role='restaurant');cid=next(c for c in manager['conversations']if c['visitor']==VISITOR)['id'];api({'action':'conversation','id':cid,'staffMode':True,'assignedTo':'Front desk'},role='restaurant');status,out=chat('Show the menu');check('takeover pauses assistant',status==200 and out['reply']is None)
  status,_=api({'action':'conversation','id':cid,'text':'Sample staff response'},role='restaurant');check('staff replies after takeover',status==200)
  api({'action':'conversation','id':cid,'staffMode':False},role='restaurant');status,out=chat('مینو دکھائیں');check('assistant resumes in Urdu',status==200 and any('\u0600'<=c<='\u06ff'for c in out['reply']))
  if '--ui'in sys.argv:ui()
  h.db('demo_businesses?slug=eq.'+SLUG,'PATCH',{'expires_at':(datetime.now(timezone.utc)-timedelta(minutes=1)).isoformat()});status,_=api();check('expired access refused',status==410)
 finally:
  events=h.db('demo_events?slug=eq.'+SLUG+'&select=id')
  h.db('rpc/demo_restaurant_action','POST',{'p_slug':SLUG,'p_visitor':'system-reset','p_role':'system','p_action':'reset','p_data':{}})
  check('reset archives and preserves analytics',bool(h.db('demo_restaurant_archives?slug=eq.'+SLUG))and len(h.db('demo_events?slug=eq.'+SLUG+'&select=id'))==len(events))
  h.db('demo_businesses?slug=eq.'+SLUG,'PATCH',{'expires_at':(datetime.now(timezone.utc)-timedelta(minutes=1)).isoformat()})
 print(str(len(passed))+' restaurant checks passed.',flush=True)
def ui():
 from playwright.sync_api import sync_playwright
 with sync_playwright()as pw:
  browser=pw.chromium.launch();context=browser.new_context(viewport={'width':1440,'height':1000});context.add_init_script("localStorage.setItem('np-visitor-"+SLUG+"','"+VISITOR+"')");page=context.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
  for role,tabs in [('customer',['overview','menu','orders','reservations','messages']),('restaurant',['overview','orders','tables','reservations','inbox','menu','customers','settings']),('kitchen',['tickets','completed','notes'])]:
   for theme in ['light','dark']:
    page.add_init_script("localStorage.setItem('np-restaurant-theme','"+theme+"')")
    for tab in tabs:
     page.goto(BASE+'/d/'+SLUG+'/'+role+'?'+urllib.parse.urlencode({'t':TOKEN,'tab':tab}));page.wait_for_selector('.rp-foot');page.wait_for_function("document.querySelector('.rp-main').innerText.indexOf('Preparing your sample')<0");check(role+' '+tab+' '+theme+' no overflow',page.evaluate('document.documentElement.scrollWidth<=innerWidth'))
  page.goto(BASE+'/d/'+SLUG+'/customer?t='+TOKEN);page.wait_for_selector('.rp-hero');page.get_by_role('button',name='Reserve a table',exact=True).first.click();page.wait_for_selector('[role=dialog]');check('booking modal focus inside',page.evaluate("document.querySelector('[role=dialog]').contains(document.activeElement)"));page.keyboard.press('Escape');check('Escape closes booking',page.locator('[role=dialog]').count()==0)
  page.set_viewport_size({'width':390,'height':844})
  for role in ['customer','restaurant','kitchen']:
   page.goto(BASE+'/d/'+SLUG+'/'+role+'?t='+TOKEN+'&lang=ur');page.wait_for_selector('.rp-foot');check(role+' mobile Urdu RTL',page.locator('.rp').get_attribute('dir')=='rtl'and page.evaluate('document.documentElement.scrollWidth<=innerWidth'))
  check('no browser exceptions',not errors);browser.close()
if __name__=='__main__':main()
