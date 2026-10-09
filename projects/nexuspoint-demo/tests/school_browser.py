"""Connected school browser loop plus responsive/theme/keyboard checks.
Creates a fictional fixture and archives it afterwards.
"""
import json,re
from datetime import datetime,timedelta
from pathlib import Path
import school_eval as s
from playwright.sync_api import sync_playwright
def main():
 b=s.fixture();out=s.ROOT/'tests/qa/school';out.mkdir(parents=True,exist_ok=True)
 try:
  status,state=s.api(b);assert status==200,state
  student=state['students'][0];cl=next(c for c in state['classes']if c['id']==student['class_id'])
  with sync_playwright()as pw:
   browser=pw.chromium.launch();ctx=browser.new_context(viewport={'width':1440,'height':1000});ctx.add_init_script("localStorage.setItem("+json.dumps('np-visitor-'+b['slug'])+","+json.dumps(s.VISITOR)+");")
   p=ctx.new_page();errors=[];p.on('pageerror',lambda e:errors.append(str(e)))
   def goto(role,tab='overview',lang='en'):
    p.goto(s.BASE+'/d/'+b['slug']+'/'+role+'?t='+b['token']+'&tab='+tab+'&lang='+lang)
    p.wait_for_selector('.sc-content[aria-busy=false]',timeout=45000)
    if role=='teacher':
     p.get_by_label('نمونہ استاد'if lang=='ur'else 'Sample teacher',exact=True).select_option(cl['teacher_id'])
     p.wait_for_selector('.sc-content[aria-busy=false]',timeout=45000)
   def tab(role,key,lang='en'):
    goto(role,key,lang)
   def modal():return p.locator('[role=dialog]')
   def save(name='Save sample'):
    modal().get_by_role('button',name=name,exact=True).click();p.wait_for_function("!document.querySelector('[role=dialog]')",timeout=20000)
   goto('parent');p.screenshot(path=str(out/'parent-light.png'),full_page=True)
   s.check('parent hero has readable width',p.locator('.sc-hero>div').bounding_box()['width']>350)
   p.get_by_role('button',name='Toggle theme',exact=True).click();p.screenshot(path=str(out/'parent-dark.png'),full_page=True)
   tab('parent','fees');p.get_by_role('button',name='Simulate fee payment',exact=True).first.click();modal().get_by_label('Fictional transaction reference',exact=True).fill('UI-DEMO-FEE');save('Submit for office review')
   s.check('browser fee stays pending verification',p.locator('.sc-list-row').filter(has_text='UI-DEMO-FEE').locator('.sc-badge.pending').count()>0)
   tab('school','fees');row=p.locator('.sc-list-row').filter(has_text='UI-DEMO-FEE').first;row.get_by_role('button',name='Verify demo payment',exact=True).click();p.wait_for_function("!document.querySelector('.sc-error')");p.wait_for_timeout(2400)
   tab('parent','fees');s.check('browser office verification reaches parent',p.locator('.sc-list-row').filter(has_text='UI-DEMO-FEE').locator('.sc-badge.paid').count()==1)
   tab('teacher','attendance');p.get_by_role('button',name='Mark all present',exact=True).click();p.get_by_role('button',name='Save attendance',exact=True).click();p.wait_for_timeout(2400)
   tab('parent','attendance');s.check('browser attendance reaches linked parent',p.get_by_role('cell',name=datetime.now(s.h.PKT).date().isoformat(),exact=True).count()>0)
   tab('teacher','homework');p.get_by_role('button',name='New homework',exact=True).click();modal().get_by_label('Title',exact=True).fill('UI sample worksheet');modal().get_by_label('Instructions',exact=True).fill('Fictional worksheet question.');save('Save draft')
   tab('parent','homework');s.check('browser homework draft hidden from parent',p.get_by_role('heading',name='UI sample worksheet',exact=True).count()==0)
   tab('teacher','homework');card=p.locator('article.sc-card').filter(has_text='UI sample worksheet');card.get_by_role('button',name='Publish homework',exact=True).click();p.wait_for_timeout(2400)
   tab('parent','homework');card=p.locator('article.sc-card').filter(has_text='UI sample worksheet');card.get_by_role('button',name='Submit response',exact=True).click();modal().get_by_label('Sample response',exact=True).fill('UI fictional answer');save('Submit response')
   tab('teacher','homework');card=p.locator('article.sc-card').filter(has_text='UI sample worksheet');card.locator('summary').click();card.get_by_role('button',name='Review response',exact=True).click();modal().get_by_label('Feedback',exact=True).fill('UI sample teacher feedback');save('Save feedback')
   tab('parent','homework');s.check('browser homework review reaches parent',p.get_by_text('Teacher feedback: UI sample teacher feedback',exact=True).is_visible())
   tab('teacher','results');p.get_by_role('button',name='New assessment',exact=True).click();modal().get_by_label('Title',exact=True).fill('UI term assessment');modal().get_by_label('Marks for '+student['roll'],exact=True).fill('44');save('Save draft')
   tab('parent','results');s.check('browser result draft hidden',p.get_by_role('heading',name='UI term assessment',exact=True).count()==0)
   tab('teacher','results');card=p.locator('article.sc-card').filter(has_text='UI term assessment');card.get_by_role('button',name='Publish results',exact=True).click();p.wait_for_timeout(2400)
   tab('parent','results');s.check('browser published marks reach parent',p.locator('article.sc-card').filter(has_text='UI term assessment').locator('.sc-mark').inner_text().strip()=='44 / 50')
   p.get_by_role('button',name='Print report card',exact=True).click();p.emulate_media(media='print');p.pdf(path=str(out/'report-card.pdf'));p.emulate_media(media='screen');s.check('print report contains published marks',modal().get_by_text('44 / 50',exact=True).is_visible())
   p.keyboard.press('Tab');s.check('modal keyboard focus stays inside',p.evaluate("!!document.activeElement.closest('[role=dialog]')"));p.keyboard.press('Escape');s.check('Escape closes report',modal().count()==0)
   tab('parent','admissions');p.get_by_role('button',name='Admissions enquiry',exact=True).click();modal().get_by_label('Fictional applicant name',exact=True).fill('UI sample applicant');save()
   p.get_by_role('button',name='Book campus visit',exact=True).click();date=(datetime.now(s.h.PKT)+timedelta(days=1)).date()
   for _ in range(7):
    _,slots=s.api(b,date=date.isoformat())
    if slots['slots']:break
    date+=timedelta(days=1)
   modal().get_by_label('Visit date',exact=True).fill(date.isoformat());modal().locator('.sc-slots button').first.click();save('Confirm campus visit')
   tab('school','admissions');s.check('browser admissions and campus visit reach office',p.get_by_text('UI sample applicant',exact=True).is_visible()and p.get_by_role('button',name='Check in',exact=True).count()>0)
   p.get_by_role('button',name='Check in',exact=True).first.click();p.get_by_role('button',name='Complete visit',exact=True).wait_for(timeout=15000);p.get_by_role('button',name='Complete visit',exact=True).click();p.wait_for_timeout(2400)
   tab('parent','admissions');s.check('browser office visit completion reaches parent',p.locator('.sc-badge.completed').count()>0)
   tab('school','overview');p.screenshot(path=str(out/'office-dark.png'),full_page=True);p.get_by_role('button',name='Toggle theme',exact=True).click();p.screenshot(path=str(out/'office-light.png'),full_page=True)
   for role,tabs in [('parent',['overview','attendance','homework','results','fees','timetable','admissions','leave','messages']),('school',['overview','students','attendance','fees','admissions','calendar','leave','timetable','notices','inbox']),('teacher',['overview','students','attendance','homework','results','timetable','leave'])]:
    for key in tabs:
     tab(role,key);s.check(role+' '+key+' desktop no overflow',p.evaluate('document.documentElement.scrollWidth<=innerWidth'))
   ctx.set_offline(True);p.wait_for_selector('.sc-error',timeout=15000);s.check('connection failure visible',True);ctx.set_offline(False);p.wait_for_function("!document.querySelector('.sc-error')",timeout=15000);s.check('connection recovers',True)
   for role in ['parent','school','teacher']:
    for theme in ['light','dark']:
     p.set_viewport_size({'width':390,'height':844});ctx.add_init_script("localStorage.setItem('np-school-theme',"+json.dumps(theme)+");");goto(role,'overview','ur');p.screenshot(path=str(out/(role+'-mobile-urdu-'+theme+'.png')),full_page=True);s.check(role+' '+theme+' mobile Urdu overflow',p.evaluate('document.documentElement.scrollWidth<=innerWidth'))
     s.check(role+' '+theme+' RTL',p.locator('.sc').get_attribute('dir')=='rtl')
   s.check('browser loop has no JavaScript exceptions',not errors);browser.close()
 finally:s.cleanup(b)
 print(str(len(s.passed))+' school browser checks passed.',flush=True)
if __name__=='__main__':main()
