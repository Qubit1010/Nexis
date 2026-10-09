"""Explicit cross-business access checks with two isolated fictional restaurants."""
import json,secrets,urllib.parse,sys
from datetime import datetime,timedelta,timezone
import healthcare_eval as h
def main():
 template=json.loads((h.ROOT.parent/'quetta-local-market/data/demos/usmania-restaurant-69ac.json').read_text(encoding='utf-8'));fixtures=[];passed=0
 def call(b,body=None,role='customer',**extra):
  p={'slug':b['slug'],'t':b['token'],'visitor':'restaurant-scope-visitor','role':role,**extra}
  return h.request(h.BASE+'/api/restaurant','POST',{**p,**body})if body else h.request(h.BASE+'/api/restaurant?'+urllib.parse.urlencode(p))
 def check(name,result):
  nonlocal passed
  assert result,name;passed+=1;print('PASS',name,flush=True)
 try:
  for _ in range(2):
   b={k:template[k]for k in ['profile','xray','site','roi','health']};b.update(slug='restaurant-scope-'+secrets.token_hex(4),token=secrets.token_urlsafe(20),code='S'+secrets.token_hex(4),sector='food',name='[QA] Scope restaurant',expires_at=(datetime.now(timezone.utc)+timedelta(days=14)).isoformat());h.db('demo_businesses','POST',b);fixtures.append(b)
  a,b=fixtures;_,sa=call(a);_,sb=call(b)
  item=sa['menu'][0];order={'action':'order','items':[{'itemId':item['id'],'quantity':1,'spice':'medium','notes':''}],'mode':'pickup','requestId':'scope-order-one'}
  status,out=call(a,order);assert status==200;oid=out['result']['id']
  status,_=call(b,order);check('foreign menu cannot be ordered',status==400)
  status,_=call(b,{'action':'menu','id':item['id'],'available':False},role='restaurant');check('foreign menu cannot be edited',status==404)
  status,_=call(b,{'action':'order_status','id':oid,'status':'accepted'},role='restaurant');check('foreign order cannot change',status==404)
  status,_=call(b,{'action':'payment','id':oid},role='restaurant');check('foreign order cannot receive demo payment',status==404)
  date=(datetime.now(h.PKT)+timedelta(days=1)).date().isoformat();_,avail=call(b,date=date,party=2)
  status,_=call(b,{'action':'reserve','party':2,'start':avail['slots'][0],'tableId':sa['tables'][0]['id'],'requestId':'scope-table-one'});check('foreign table cannot be reserved',status==409)
  status,_=call(b,{'action':'table','id':sa['tables'][0]['id'],'active':False},role='restaurant');check('foreign table cannot be blocked',status==404)
  _,own=call(b,role='restaurant');check('manager feed excludes other business records',all(o['id']!=oid for o in own['orders'])and all(c['id']!=sa['customer']['id']for c in own['customers']))
  status,_=call(b,slug=a['slug']);check('token cannot authorize another business',status==404)
  status,_=call(a,order,t='invalid');check('invalid token cannot write',status==404)
  h.db('demo_businesses?slug=eq.'+b['slug'],'PATCH',{'expires_at':(datetime.now(timezone.utc)-timedelta(seconds=1)).isoformat()});status,_=call(b,{**order,'items':[{'itemId':sb['menu'][0]['id'],'quantity':1,'spice':'medium','notes':''}]});check('expired token cannot write',status==410)
 finally:
  for b in fixtures:
   h.db('rpc/demo_restaurant_action','POST',{'p_slug':b['slug'],'p_visitor':'system-reset','p_role':'system','p_action':'reset','p_data':{}});h.db('demo_businesses?slug=eq.'+b['slug'],'PATCH',{'expires_at':(datetime.now(timezone.utc)-timedelta(seconds=1)).isoformat()})
 print(str(passed)+' business scope checks passed.')
if __name__=='__main__':main()
