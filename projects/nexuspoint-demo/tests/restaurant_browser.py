"""Exercise customer checkout -> manager -> kitchen -> receipt in a real browser."""
import json,sys
from datetime import datetime,timedelta,timezone
import restaurant_eval as r
from playwright.sync_api import sync_playwright
def main():
 template=json.loads((r.ROOT.parent/'quetta-local-market/data/demos/usmania-restaurant-69ac.json').read_text(encoding='utf-8'))
 b={k:template[k]for k in ['profile','xray','site','roi','health']};b.update(slug=r.SLUG,token=r.TOKEN,code='B'+r.secrets.token_hex(3).upper(),sector='food',name='[QA] Browser restaurant',expires_at=(datetime.now(timezone.utc)+timedelta(days=14)).isoformat())
 r.h.db('demo_businesses','POST',b);r.api()
 out=r.ROOT/'tests/qa/restaurant';out.mkdir(parents=True,exist_ok=True)
 try:
  with sync_playwright() as pw:
   browser=pw.chromium.launch();ctx=browser.new_context(viewport={'width':1440,'height':1050})
   ctx.add_init_script("localStorage.setItem('np-visitor-"+r.SLUG+"','"+r.VISITOR+"')")
   page=ctx.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
   def goto(role,tab='',lang='en'):
    page.goto(r.BASE+'/d/'+r.SLUG+'/'+role+'?'+r.urllib.parse.urlencode({'t':r.TOKEN,'tab':tab,'lang':lang}));page.wait_for_selector('.rp-content[aria-busy=false]')
   goto('customer','menu');page.locator('.rp-menu-card').filter(has_text='Chicken karahi').get_by_role('button',name='+ Add',exact=True).click()
   page.locator('.rp-cart-line').first.locator('select').select_option('hot');page.locator('.rp-cart-line').first.locator('input').fill('Fictional extra ginger')
   page.get_by_role('button',name='Review & checkout',exact=True).click();modal=page.locator('[role=dialog]');modal.get_by_label('Order mode',exact=True).select_option('delivery');modal.get_by_label('Fictional delivery address',exact=True).fill('Sample House 12, Quetta');modal.get_by_role('button',name='Place sample order',exact=True).click();page.wait_for_selector('.rp-receipt')
   r.check('browser customer checkout persists',True)
   _,s=r.api();order=s['orders'][0];r.check('browser preferences saved to ticket',order['items'][0]['spice']=='hot'and order['items'][0]['notes']=='Fictional extra ginger')
   page.screenshot(path=str(out/'receipt.png'),full_page=True);page.emulate_media(media='print');r.check('print layout shows receipt',page.locator('.rp-receipt').is_visible());page.emulate_media(media='screen');page.locator('.rp-receipt').get_by_role('button',name='Close',exact=True).click()
   goto('restaurant','orders');row=page.locator('.rp-list-row').filter(has_text='#'+str(order['number'])).first;row.get_by_role('button',name='Mark Accepted',exact=True).click();page.wait_for_timeout(2500)
   goto('kitchen');ticket=page.locator('.rp-ticket').filter(has_text='#'+str(order['number']));ticket.get_by_role('button',name='Start preparing',exact=True).click();ticket.get_by_role('button',name='Mark ready',exact=True).wait_for(timeout=10000);ticket.get_by_role('button',name='Mark ready',exact=True).click();page.wait_for_timeout(2500)
   r.check('browser manager and kitchen share same order',ticket.get_by_text('Waiting for front-of-house handoff',exact=True).is_visible())
   page.screenshot(path=str(out/'kitchen-light.png'),full_page=True)
   goto('restaurant','orders');row=page.locator('.rp-list-row').filter(has_text='#'+str(order['number'])).first;row.get_by_role('button',name='Mark Out for delivery',exact=True).click();row.get_by_role('button',name='Mark Completed',exact=True).wait_for(timeout=10000);row.get_by_role('button',name='Mark Completed',exact=True).click();page.wait_for_timeout(2500)
   goto('customer','orders');page.get_by_role('button',name='Completed',exact=True).first.click();row=page.locator('.rp-list-row').filter(has_text='#'+str(order['number']));r.check('browser completion reaches customer history',row.locator('.rp-status').inner_text()=='Completed')
   page.get_by_role('button',name='Reorder with current menu prices',exact=True).first.click();r.check('reorder returns saved items to basket',page.locator('.rp-cart-line').count()>0)
   page.reload();page.wait_for_selector('.rp-cart-line');r.check('basket survives refresh',page.locator('.rp-cart-line').count()>0)
   goto('customer');page.screenshot(path=str(out/'customer-light.png'),full_page=True);page.get_by_role('button',name='Switch theme',exact=True).click();page.screenshot(path=str(out/'customer-dark.png'),full_page=True)
   page.get_by_role('button',name='Reserve a table',exact=True).first.click();modal=page.locator('[role=dialog]');day=(datetime.now(r.h.PKT)+timedelta(days=1)).date().isoformat();modal.get_by_label('Visit date',exact=True).fill(day);modal.locator('.rp-slot-grid button').first.click();modal.get_by_role('button',name='Confirm sample table',exact=True).click();page.wait_for_function("!document.querySelector('[role=dialog]')");_,s=r.api();r.check('browser table booking saved',len(s['reservations'])==1)
   goto('restaurant');page.screenshot(path=str(out/'manager-dark.png'),full_page=True);page.get_by_role('button',name='Switch theme',exact=True).click();page.screenshot(path=str(out/'manager-light.png'),full_page=True)
   goto('restaurant','customers');page.get_by_label('New fictional guest',exact=True).fill('Sample new guest');page.get_by_role('button',name='Add guest',exact=True).click();page.get_by_role('heading',name='Sample new guest',exact=True).wait_for(timeout=10000);r.check('manager can add fictional guest',True)
   ctx.set_offline(True);page.wait_for_selector('.rp-error',timeout=10000);r.check('offline shows connection error',True);ctx.set_offline(False);page.wait_for_function("!document.querySelector('.rp-error')",timeout=10000);r.check('connection recovery restores view',True)
   for role in ['customer','restaurant','kitchen']:
    page.set_viewport_size({'width':390,'height':844});goto(role,'','ur');page.wait_for_function("document.querySelector('.rp-main').innerText.indexOf('نمونہ ریسٹورنٹ لوڈ')<0");page.screenshot(path=str(out/(role+'-mobile-urdu.png')),full_page=True);r.check(role+' mobile overflow',page.evaluate('document.documentElement.scrollWidth<=innerWidth'))
   r.check('browser workflow no exceptions',not errors);browser.close()
 finally:
  r.h.db('rpc/demo_restaurant_action','POST',{'p_slug':r.SLUG,'p_visitor':'system-reset','p_role':'system','p_action':'reset','p_data':{}});r.h.db('demo_businesses?slug=eq.'+r.SLUG,'PATCH',{'expires_at':(datetime.now(timezone.utc)-timedelta(minutes=1)).isoformat()})
 print(str(len(r.passed))+' browser workflow checks passed.')
if __name__=='__main__':main()
