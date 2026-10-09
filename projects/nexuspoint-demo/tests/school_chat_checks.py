"""Focused hosted checks for language memory and shared assistant handoff priority."""
import school_eval as s
def main():
 b=s.fixture()
 try:
  status,out=s.chat(b,'نمونہ فیس دیکھیں');s.check('Urdu offers linked student cards',status==200 and out['cards'][0]['kind']=='school_student')
  choice=out['cards'][0];status,out=s.chat(b,choice['label'],choice);s.check('English student card preserves Urdu answer',status==200 and 'یہ فرضی فیس ہے'in out['reply'])
  status,out=s.chat(b,'meri beti ki fee kya hai');choice=out['cards'][0];status,out=s.chat(b,choice['label'],choice);s.check('student card preserves Roman Urdu',status==200 and 'farzi fees'in out['reply']and not any('\u0600'<=c<='\u06ff'for c in out['reply']))
  s.chat(b,'Book a campus visit');status,out=s.chat(b,'I want to talk to a staff person');s.check('staff request interrupts campus flow',status==200 and out['stage']=='needs_human'and not out.get('cards'))
  s.chat(b,'Show sample fees');status,out=s.chat(b,'My child is unconscious, attendance update');s.check('urgent message overrides active school flow',status==200 and out['stage']=='needs_human'and '1122'in out['reply']and not out.get('cards'))
  _,office=s.api(b,role='school');c=next(c for c in office['conversations']if c['visitor']==s.VISITOR);s.check('handoff flag reaches office',c['handoff']and not c.get('booking_context'))
 finally:s.cleanup(b)
 print(str(len(s.passed))+' focused school assistant checks passed.',flush=True)
if __name__=='__main__':main()
