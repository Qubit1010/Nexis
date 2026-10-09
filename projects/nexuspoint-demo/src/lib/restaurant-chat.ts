import { randomUUID } from 'node:crypto';
import { updateConversation,type Business,type Conversation } from './db.ts';
import { restaurantAction,restaurantAvailability,restaurantState } from './restaurant.ts';
import { money,type BasketLine,type Order,type Reservation } from './restaurant-types.ts';
import { dayAfter,localDate,timeLabel,dateLabel,type Choice } from './healthcare-types.ts';
import { detectLang } from './scripted.ts';
export async function restaurantChat(b:Business,c:Conversation,text:string,choice?:Choice){
 const lang=detectLang(text),say=(en:string,ur:string,roman?:string)=>lang==='ur'?ur:lang==='roman'?(roman??en):en;
 let ctx={...(c.booking_context??{})};
 const intent=/menu|order|karahi|sajji|naan|tea|platter|rice|raita|lime|pickup|delivery|takeaway|reserve|reservation|table|book|basket|status|allerg|sick|complaint|آرڈر|مینو|کڑاہی|سجی|نان|چائے|بکنگ|میز|ڈیلیوری|الرج|شکایت|بیمار/i.test(text);
 if(!choice&&!intent&&!ctx.flow)return null;
 const state=await restaurantState(b,c.visitor,'customer');
 const card=(kind:Choice['kind'],value:string,label:string):Choice=>({kind,value,label});
 const finish=async(reply:string,cards:Choice[]=[],stage='collecting')=>{await updateConversation(c.id,{booking_context:ctx});return {reply,cards,stage,summary:ctx.flow==='table'?'Sample table booking':'Sample restaurant order'};};
 const menuCards=()=>state.menu.filter(m=>m.available).map(m=>card('food_item',m.id,`${lang==='ur'?m.name_ur:m.name} · ${money(m.price)}`));
 const modeCards=()=>['pickup','delivery'].map(m=>card('food_mode',m,say(m==='pickup'?'Pickup':'Delivery',m==='pickup'?'پک اپ':'ڈیلیوری')));
 if(/sick|poison|complaint|شکایت|بیمار/i.test(text))return finish(say('I am flagging this concern for restaurant staff. Please share what happened so they can follow up. This demo does not send real notifications.','یہ شکایت عملے کے لیے نشان لگائی گئی ہے۔ تفصیل بتائیں تاکہ عملہ مدد کرے۔ ڈیمو حقیقی اطلاع نہیں بھیجتا۔'),[],'needs_human');
 if(/are you.*(?:bot|real|human)|کیا آپ.*(?:بوٹ|انسان)/i.test(text))return finish(say('I am the restaurant demo assistant. I can save fictional orders and table bookings. A staff member can take over this conversation.','میں ریسٹورنٹ کا ڈیمو اسسٹنٹ ہوں۔ نمونہ آرڈر اور میز بکنگ محفوظ کر سکتا ہوں۔ عملہ گفتگو سنبھال سکتا ہے۔'));
 if(/allerg|allergy|safe|حساس|الرج/i.test(text))return finish(say('Sample allergen labels are illustrative. Staff must verify ingredients and cross-contact before serving. I have flagged this conversation for staff.','الرجی کی معلومات صرف نمونہ ہیں۔ عملہ اجزاء کی تصدیق کرے گا۔ یہ گفتگو عملے کو بھیج دی گئی ہے۔'),[],'needs_human');
 if(/status|where.*order|کہاں|آرڈر کی حالت/i.test(text)&&state.orders.length)return finish(say(`Your latest sample order #${state.orders[0].number} is ${state.orders[0].status.replaceAll('_',' ')}. Track it in your customer portal.`,`آپ کا تازہ نمونہ آرڈر #${state.orders[0].number} کی حالت: ${state.orders[0].status}۔`),[],'warm');
 if(choice?.kind==='food_clear'){ctx={flow:'order',requestId:randomUUID()};return finish(say('Basket cleared. Choose from this fictional sample menu.','باسکٹ خالی ہے۔ نمونہ مینو سے منتخب کریں۔'),menuCards());}
 if(choice?.kind==='table_party'||/reserve|reservation|table|میز|بکنگ/i.test(text)&&!choice){
  ctx={flow:'table',requestId:randomUUID(),date:choice?.kind==='table_party'?(ctx.date??localDate()):text.match(/\d{4}-\d{2}-\d{2}/)?.[0]??(/tomorrow|kal|کل/i.test(text)?dayAfter(localDate()):localDate())};
  if(choice?.kind==='table_party')ctx.party=choice.value;
  else {const n=text.match(/(?:for|party of|کے لیے)\s*(\d{1,2})/i)?.[1];if(n)ctx.party=n;}
  if(!ctx.party)return finish(say('How many guests? Tables and availability are fictional samples, reserved for 90 minutes.','کتنے مہمان؟ میزیں اور اوقات فرضی نمونے ہیں، بکنگ ۹۰ منٹ کے لیے ہے۔'),[2,4,6,8].map(n=>card('table_party',String(n),say(`${n} guests`,`${n} مہمان`))));
 }
 if(ctx.flow==='table'){
  if(choice?.kind==='table_time')ctx.start=choice.value;
  if(choice?.kind==='table_confirm'){
   if(!ctx.start||!ctx.party)return finish(say('Choose a party size and time first.','پہلے مہمانوں کی تعداد اور وقت منتخب کریں۔'));
   try{const r=await restaurantAction<Reservation>(b,c.visitor,'customer','reserve',{party:Number(ctx.party),start:ctx.start,requestId:ctx.requestId,source:'chat',notes:'Fictional chat reservation'});await updateConversation(c.id,{action:{type:'booking',details:[{key:'Sample reservation',value:r.id},{key:'Guests',value:String(r.party)},{key:'Time (PKT)',value:`${dateLabel(r.starts_at)} ${timeLabel(r.starts_at)}`}]}});ctx={};return finish(say(`Sample table booking confirmed for ${r.party} guests, ${dateLabel(r.starts_at)} at ${timeLabel(r.starts_at)} PKT. Saved in your portal and the manager calendar.`,`نمونہ میز بکنگ محفوظ ہو گئی، ${r.party} مہمان، ${dateLabel(r.starts_at,'ur')} ${timeLabel(r.starts_at,'ur')}۔`),[],'warm');}
   catch{return finish(say('That table time is no longer available. Please select a new time.','یہ وقت دستیاب نہیں رہا۔ نیا وقت منتخب کریں۔'));}
  }
  if(ctx.start)return finish(say(`Confirm a sample table for ${ctx.party} guests on ${dateLabel(ctx.start)} at ${timeLabel(ctx.start)} PKT?`,`کیا ${ctx.party} مہمانوں کے لیے ${dateLabel(ctx.start,'ur')} ${timeLabel(ctx.start,'ur')} پر نمونہ بکنگ محفوظ کریں؟`),[card('table_confirm','confirm',say('Confirm table booking','میز بکنگ کی تصدیق'))]);
  const day=text.match(/\d{4}-\d{2}-\d{2}/)?.[0];if(day)ctx.date=day;
  let slots=await restaurantAvailability(b,ctx.date??localDate(),Number(ctx.party));
  if(!slots.length&&ctx.date===localDate()){ctx.date=dayAfter(localDate());slots=await restaurantAvailability(b,ctx.date,Number(ctx.party));}
  return finish(say(`Available sample times for ${ctx.party} guests on ${ctx.date}. All times PKT. Send another YYYY-MM-DD date to change the day.`,`نمونہ دستیاب اوقات، ${ctx.party} مہمان، ${ctx.date}۔ دن بدلنے کے لیے YYYY-MM-DD لکھیں۔`),slots.slice(0,12).map(s=>card('table_time',s,timeLabel(s,lang))));
 }
 if(choice?.kind==='food_item'){
  if(ctx.completed)ctx={};ctx.flow='order';ctx.requestId??=randomUUID();
  const item=state.menu.find(m=>m.id===choice.value&&m.available);if(!item)return finish(say('That sample item is unavailable. Choose another.','یہ نمونہ آئٹم دستیاب نہیں۔ دوسرا منتخب کریں۔'),menuCards());
  const basket:BasketLine[]=JSON.parse(ctx.basket??'[]');const found=basket.find(x=>x.itemId===item.id);
  if(found)found.quantity=Math.min(found.quantity+1,20);else basket.push({itemId:item.id,quantity:1,spice:'medium',notes:''});ctx.basket=JSON.stringify(basket);
 }
 if(!choice&&/order|want|send|deliver|chahiye|\d+\s+(?:chicken|mutton|naan|tea|sajji|bbq|butter|karak)|آرڈر|چاہیے|[0-9]+\s+(?:چکن|مٹن|نان|چائے)/i.test(text)&&!ctx.completed){
  const basket:BasketLine[]=JSON.parse(ctx.basket??'[]');
  for(const m of state.menu){const aliases=m.name==='Butter naan'?['naan','نان']:m.name==='Karak tea'?['tea','چائے']:[m.name,m.name_ur];for(const alias of aliases){const escaped=alias.replace(/[.*+?^${}()|[\]\\]/g,'\\$&');const match=text.match(new RegExp(`(?:(\\d{1,2})\\s+)?${escaped}`,'i'));if(match&&m.available){const qty=Number(match[1]??1);if(qty<1||qty>20)continue;const old=basket.find(x=>x.itemId===m.id);if(old)old.quantity=Math.min(20,old.quantity+qty);else basket.push({itemId:m.id,quantity:qty,spice:'medium',notes:''});break;}}}
  if(basket.length){ctx.flow='order';ctx.requestId??=randomUUID();ctx.basket=JSON.stringify(basket);}
 }
 if(choice?.kind==='food_mode'){
  if(!['pickup','delivery'].includes(choice.value))return finish(say('Select pickup or delivery.','پک اپ یا ڈیلیوری منتخب کریں۔'),modeCards());ctx.mode=choice.value;
 }
 if(!choice&&ctx.flow==='order'){
  if(/delivery|ڈیلیوری/i.test(text))ctx.mode='delivery';else if(/pickup|takeaway|پک اپ/i.test(text))ctx.mode='pickup';
  if(ctx.mode==='delivery'&&/house|road|street|مکان|گلی|روڈ/i.test(text))ctx.address=text.slice(0,300);
 }
 if(!choice&&ctx.flow==='order'&&ctx.mode==='delivery'&&ctx.awaitingAddress){ctx.address=text.slice(0,300);delete ctx.awaitingAddress;}
 if(choice?.kind==='food_confirm'){
  try{const o=await restaurantAction<Order>(b,c.visitor,'customer','order',{items:JSON.parse(ctx.basket??'[]'),mode:ctx.mode,address:ctx.address??'',notes:'Fictional chat order',source:'chat',requestId:ctx.requestId});await updateConversation(c.id,{action:{type:'order',details:[{key:'Sample ticket',value:`#${o.number}`},{key:'Items',value:o.items.map(x=>`${x.quantity} × ${x.name}`).join(', ')},{key:'Fictional total',value:money(o.total)}]}});ctx.completed=o.id;delete ctx.flow;return finish(say(`Sample order #${o.number} saved: ${money(o.total)} (fictional menu prices, no payment taken). Staff can accept it and the kitchen can update its progress.`,`نمونہ آرڈر #${o.number} محفوظ: ${money(o.total)}۔ قیمتیں فرضی ہیں، کوئی ادائیگی نہیں لی گئی۔`),[card('food_clear','clear',say('Start another order','نیا آرڈر'))],'warm');}
  catch{return finish(say('The order could not be saved. Check item availability and details in your customer portal, or ask staff.','آرڈر محفوظ نہیں ہو سکا۔ پورٹل میں دستیابی اور تفصیلات دیکھیں یا عملے سے پوچھیں۔'),[],'needs_human');}
 }
 const basket:BasketLine[]=JSON.parse(ctx.basket??'[]');
 if(basket.length){
  const lines=basket.map(x=>{const m=state.menu.find(m=>m.id===x.itemId)!;return `${x.quantity} × ${lang==='ur'?m.name_ur:m.name}`;});
  const total=basket.reduce((n,x)=>n+(state.menu.find(m=>m.id===x.itemId)?.price??0)*x.quantity,0);
  if(!ctx.mode)return finish(say(`Sample basket: ${lines.join(', ')}. ${money(total)}, fictional prices. Choose pickup or delivery.`,`نمونہ باسکٹ: ${lines.join('، ')}۔ ${money(total)}، فرضی قیمتیں۔ پک اپ یا ڈیلیوری منتخب کریں۔`),[...modeCards(),...menuCards(),card('food_clear','clear',say('Clear basket','باسکٹ خالی کریں'))]);
  if(ctx.mode==='delivery'&&!ctx.address){ctx.awaitingAddress='yes';return finish(say('Please send a fictional delivery address for this demo. Delivery areas and fees require staff confirmation.','ڈیمو کے لیے فرضی پتہ لکھیں۔ ڈیلیوری علاقے اور فیس کی تصدیق عملہ کرے گا۔'));}
  return finish(say(`Review: ${lines.join(', ')} · ${ctx.mode} · ${money(total)}. All prices are fictional; no fees or payments are collected. Confirm to save the demo order.`,`جائزہ: ${lines.join('، ')} · ${ctx.mode} · ${money(total)}۔ قیمتیں فرضی ہیں۔ محفوظ کرنے کے لیے تصدیق کریں۔`),[card('food_confirm','confirm',say('Confirm sample order','نمونہ آرڈر کی تصدیق')),card('food_clear','clear',say('Clear basket','باسکٹ خالی کریں'))]);
 }
 return finish(say('Choose from the fictional sample menu. Prices and availability are for this outreach demo only. You can also ask to reserve a table.','فرضی نمونہ مینو سے منتخب کریں۔ قیمتیں اور دستیابی صرف ڈیمو کے لیے ہیں۔ میز بکنگ بھی کر سکتے ہیں۔','Fictional sample menu se chunein. Prices aur availability sirf demo ke liye hain. Table bhi reserve kar sakte hain.'),menuCards());
}
