"""Read-only checks of the existing outreach URLs and restaurant visual contrast."""
import json,sys,urllib.parse
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1];BASE=sys.argv[1]if len(sys.argv)>1 else 'http://localhost:4400'
def main():
 food=json.loads((ROOT.parent/'quetta-local-market/data/demos/usmania-restaurant-69ac.json').read_text(encoding='utf-8'))
 out=ROOT/'tests/qa/restaurant';out.mkdir(parents=True,exist_ok=True);checks=0
 with sync_playwright()as pw:
  browser=pw.chromium.launch();ctx=browser.new_context(viewport={'width':1440,'height':950})
  ctx.add_init_script("localStorage.setItem('np-visitor-"+food['slug']+"','sample-guest-1')")
  page=ctx.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
  for theme in ['light','dark']:
   ctx.add_init_script("localStorage.setItem('np-restaurant-theme','"+theme+"')")
   for role,tab in [('customer','overview'),('customer','menu'),('restaurant','overview'),('kitchen','tickets')]:
    page.goto(BASE+'/d/'+food['slug']+'/'+role+'?'+urllib.parse.urlencode({'t':food['token'],'tab':tab}));page.wait_for_selector('.rp-content[aria-busy=false]')
    assert page.locator('.rp').get_attribute('data-restaurant-theme')==theme
    assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
    if role=='customer'and tab=='overview':assert page.locator('.rp-hero>div').bounding_box()['width']>400
    page.screenshot(path=str(out/('smoke-'+role+'-'+tab+'-'+theme+'.png')),full_page=True)
    btn=page.locator('.rp-btn.secondary').first
    if btn.count():
     ratio=btn.evaluate("""e=>{
       const rgb=s=>s.match(/[\\d.]+/g).slice(0,3).map(Number),lum=c=>c.map(n=>{n/=255;return n<=.04045?n/12.92:Math.pow((n+.055)/1.055,2.4)}).reduce((n,v,i)=>n+v*[.2126,.7152,.0722][i],0);
       const st=getComputedStyle(e),a=lum(rgb(st.color)),b=lum(rgb(st.backgroundColor));return (Math.max(a,b)+.05)/(Math.min(a,b)+.05);
     }""")
     assert ratio>=4.5,(role,theme,ratio)
    checks+=1;print('PASS loaded',role,tab,theme,flush=True)
  page.set_viewport_size({'width':390,'height':844})
  for role in ['customer','restaurant','kitchen']:
   page.goto(BASE+'/d/'+food['slug']+'/'+role+'?'+urllib.parse.urlencode({'t':food['token'],'lang':'ur'}));page.wait_for_selector('.rp-content[aria-busy=false]');assert page.locator('.rp').get_attribute('dir')=='rtl';assert page.evaluate('document.documentElement.scrollWidth<=innerWidth');checks+=1;print('PASS mobile Urdu',role,flush=True)
  for slug,role in [('saleem-medical-complex-5702','patient'),('tameer-e-nau-public-college-ac62','')]:
   b=json.loads((ROOT.parent/'quetta-local-market/data/demos'/ (slug+'.json')).read_text(encoding='utf-8'));r=page.goto(BASE+'/d/'+slug+('/'+role if role else '')+'?t='+b['token']);assert r.status==200;checks+=1;print('PASS existing sector',b['sector'],flush=True)
  r=page.goto(BASE+'/d/'+food['slug']+'/customer?t=invalid');assert r.status==404;checks+=1;print('PASS invalid page token',flush=True)
  r=page.goto(BASE+'/d/'+food['slug']+'/patient?t='+food['token']);assert r.status==404;checks+=1;print('PASS wrong sector route',flush=True)
  assert not errors,errors
  browser.close()
 print(str(checks)+' read-only deployment checks passed.',flush=True)
if __name__=='__main__':main()
