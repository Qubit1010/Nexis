"""Read-only live education UI, access, contrast and other-sector smoke checks."""
import json
import healthcare_eval as h
from private_fixtures import demo_token
from playwright.sync_api import sync_playwright
passed=[]
SLUG='tameer-e-nau-public-college-ac62';TOKEN=demo_token("tameer-e-nau-public-college-ac62")
def check(name,value):
 assert value,name
 passed.append(name);print('PASS',name,flush=True)
def main():
 status,hub=h.request(h.BASE+'/d/'+SLUG+'?t='+TOKEN);check('education hub exposes all workspaces',status==200 and all('/'+r+'?'in hub for r in ['parent','school','teacher']))
 with sync_playwright()as pw:
  browser=pw.chromium.launch();ctx=browser.new_context(viewport={'width':1440,'height':960});p=ctx.new_page();errors=[];p.on('pageerror',lambda e:errors.append(str(e)))
  for role in ['parent','school','teacher']:
   p.goto(h.BASE+'/d/'+SLUG+'/'+role+'?t='+TOKEN);p.wait_for_selector('.sc-content[aria-busy=false]',timeout=45000)
   check(role+' live loads',not p.locator('.sc-error').count())
   for theme in ['light','dark']:
    p.evaluate("(theme)=>localStorage.setItem('np-school-theme',theme)",theme);p.reload();p.wait_for_selector('.sc-content[aria-busy=false]',timeout=45000)
    contrast=p.evaluate("""()=>{
     const color=s=>s.match(/[\\d.]+/g).slice(0,3).map(Number).map(v=>{v/=255;return v<=.04045?v/12.92:Math.pow((v+.055)/1.055,2.4)});
     const lum=s=>{const c=color(s);return c[0]*.2126+c[1]*.7152+c[2]*.0722};
     return [...document.querySelectorAll('.sc-btn,.sc-btn.secondary')].map(el=>{const cs=getComputedStyle(el),a=lum(cs.color),b=lum(cs.backgroundColor);return (Math.max(a,b)+.05)/(Math.min(a,b)+.05)});
    }""")
    check(role+' '+theme+' button contrast',bool(contrast)and min(contrast)>=4.5)
   p.set_viewport_size({'width':390,'height':844});p.goto(h.BASE+'/d/'+SLUG+'/'+role+'?t='+TOKEN+'&lang=ur');p.wait_for_selector('.sc-content[aria-busy=false]',timeout=45000)
   check(role+' mobile Urdu',p.locator('.sc').get_attribute('dir')=='rtl'and p.evaluate('document.documentElement.scrollWidth<=innerWidth'))
   p.set_viewport_size({'width':1440,'height':960})
  for slug,token,role,selector in [('saleem-medical-complex-5702',demo_token("saleem-medical-complex-5702"),'patient','.hc'),('usmania-restaurant-69ac',demo_token("usmania-restaurant-69ac"),'customer','.rp')]:
   response=p.goto(h.BASE+'/d/'+slug+'/'+role+'?t='+token);p.wait_for_selector(selector,timeout=45000);check(role+' existing demo loads',response.status==200)
  check('live UI has no exceptions',not errors);browser.close()
 status,_=h.request(h.BASE+'/api/school?slug='+SLUG+'&t=invalid&visitor=school-smoke-test');check('invalid school token refused',status==404)
 status,_=h.request(h.BASE+'/api/school?slug=usmania-restaurant-69ac&t=' + demo_token("usmania-restaurant-69ac") + '&visitor=school-smoke-test');check('restaurant cannot expose education API',status==404)
 print(str(len(passed))+' live smoke checks passed.',flush=True)
if __name__=='__main__':main()
