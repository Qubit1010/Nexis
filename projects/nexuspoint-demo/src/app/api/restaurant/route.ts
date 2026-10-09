import { NextResponse } from 'next/server';
import { authorised,expired,getBusiness,logEvent,rest,type Conversation } from '@/lib/db';
import { restaurantAction,restaurantAvailability,restaurantState } from '@/lib/restaurant';
import type { RestaurantRole } from '@/lib/restaurant-types';
export const dynamic='force-dynamic';
const json=(data:unknown,status=200)=>NextResponse.json(data,{status,headers:{'Cache-Control':'no-store'}});
const bad=(message:string):never=>{throw new Error(`INVALID: ${message}`)};
const id=(v:unknown)=>typeof v==='string'&&/^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$/i.test(v);
async function access(p:Record<string,unknown>){
 if(typeof p.slug!=='string'||typeof p.t!=='string')bad('Invalid link');
 const b=await getBusiness(p.slug as string);
 if(!authorised(b,p.t as string)||b.sector!=='food')throw new Error('NOT_FOUND: Restaurant not found');
 if(expired(b))throw new Error('EXPIRED: This preview has expired');
 if(typeof p.visitor!=='string'||!/^[a-zA-Z0-9_-]{8,64}$/.test(p.visitor)||!['customer','restaurant','kitchen'].includes(p.role as string))bad('Invalid demo session');
 return {b,visitor:p.visitor as string,role:p.role as RestaurantRole};
}
function error(e:unknown){const m=e instanceof Error?e.message:'';const match=m.match(/(INVALID|CONFLICT|NOT_FOUND|EXPIRED): ([^"\\]+)/);return json({error:match?.[2]??'Restaurant connection problem. Please try again.'},match?({INVALID:400,CONFLICT:409,NOT_FOUND:404,EXPIRED:410}[match[1]]??500):500)}
export async function GET(req:Request){try{
 const p=Object.fromEntries(new URL(req.url).searchParams),{b,visitor,role}=await access({...p,role:p.role??'customer'});
 if(p.date){const party=Number(p.party);if(!/^\d{4}-\d{2}-\d{2}$/.test(p.date)||!Number.isInteger(party)||party<1||party>20)bad('Choose a valid day and party size');return json({slots:await restaurantAvailability(b,p.date,party)});}
 return json(await restaurantState(b,visitor,role));
}catch(e){return error(e)}}
export async function POST(req:Request){try{
 const p=await req.json(),{b,visitor,role}=await access({...p,role:p.role??'customer'}),action=p.action;
 if(typeof action!=='string')bad('Choose an action');
 const data={...p};for(const k of ['slug','t','visitor','role','action'])delete data[k];
 if(['order_status','payment','reservation','menu','table'].includes(action)&&!id(data.id))bad('Invalid record identifier');
 if(data.customerId!==undefined&&!id(data.customerId))bad('Invalid guest');
 if(['order','reserve'].includes(action)&&(typeof data.requestId!=='string'||data.requestId.length<8||data.requestId.length>100))bad('Retry identifier required');
 for(const k of ['notes','address','name','text','assignedTo'])if(data[k]!==undefined&&(typeof data[k]!=='string'||data[k].length>({text:2000,assignedTo:80,name:80,address:300,notes:500}[k]??500)))bad('Invalid text field');
 if(action==='order'){
  if(!['pickup','delivery','dine_in'].includes(data.mode)||!Array.isArray(data.items)||!data.items.length||data.items.length>30)bad('Choose order mode and items');
  if(data.tableId!==undefined&&!id(data.tableId))bad('Invalid table');
  if(data.items.some((x:Record<string,unknown>)=>!x||!id(x.itemId)||!Number.isInteger(x.quantity)||Number(x.quantity)<1||Number(x.quantity)>20||!['mild','medium','hot'].includes(x.spice as string)||typeof x.notes!=='string'||x.notes.length>300))bad('Invalid basket line');
 }
 if(action==='reserve'||(action==='reservation'&&data.start!==undefined)){
  if(typeof data.start!=='string'||!Number.isFinite(Date.parse(data.start)))bad('Choose a valid time');
  if(action==='reserve'&&(!Number.isInteger(data.party)||data.party<1||data.party>20))bad('Party size must be 1 to 20');
  if(data.tableId!==undefined&&!id(data.tableId))bad('Invalid table');
 }
 if(action==='order_status'&&!['accepted','preparing','ready','out_for_delivery','completed','cancelled'].includes(data.status))bad('Invalid order status');
 if(action==='reservation'&&data.start===undefined&&!['seated','completed','cancelled','no_show'].includes(data.status))bad('Invalid booking status');
 if(action==='menu'&&((data.available!==undefined&&typeof data.available!=='boolean')||(data.price!==undefined&&(!Number.isInteger(data.price)||data.price<1||data.price>100000))))bad('Invalid menu settings');
 if(action==='table'&&typeof data.active!=='boolean')bad('Choose table availability');
 if(action==='settings'){
  if(data.accepting!==undefined&&typeof data.accepting!=='boolean')bad('Invalid ordering setting');
  if(data.prepMinutes!==undefined&&(!Number.isInteger(data.prepMinutes)||data.prepMinutes<10||data.prepMinutes>120))bad('Preparation estimate must be 10 to 120 minutes');
  if(data.openMin!==undefined||data.closeMin!==undefined)if(!Number.isInteger(data.openMin)||!Number.isInteger(data.closeMin)||data.openMin<0||data.closeMin>1440||data.closeMin-data.openMin<90||data.openMin%30||data.closeMin%30)bad('Use valid 30-minute aligned hours');
 }
 if(action==='waitlist'&&(!data.id&&(!Number.isInteger(data.party)||data.party<1||data.party>20)||data.id&&!id(data.id)))bad('Invalid waiting guest');
 if(action==='conversation'){
  if(role!=='restaurant'||!id(data.id))bad('Use the manager inbox');
  const scope=`slug=eq.${encodeURIComponent(b.slug)}&id=eq.${data.id}`;
  const c=(await rest<Conversation>('GET',`demo_conversations?${scope}&limit=1`))[0];if(!c)throw new Error('NOT_FOUND: Conversation not found');
  if(data.text){if(!c.staff_mode)bad('Take over before replying');await rest('POST','demo_messages',{conversation_id:c.id,role:'business',content:data.text,source:'staff'},'return=minimal');}
  const patch:Record<string,unknown>={last_at:new Date().toISOString()};
  if(typeof data.staffMode==='boolean'){patch.staff_mode=data.staffMode;patch.handoff=data.staffMode;}
  if(data.assignedTo!==undefined)patch.assigned_to=data.assignedTo||null;
  await rest('PATCH',`demo_conversations?${scope}`,patch,'return=minimal');return json({result:{ok:true}});
 }
 if(action==='notice'){if(role!=='restaurant')bad('Use the manager workspace');await logEvent(b.slug,'restaurant_notice',{message:data.notes??'Sample follow-up',simulated:true});return json({result:{ok:true}});}
 if(!['customer','guest','order','order_status','payment','reserve','reservation','menu','table','settings','waitlist'].includes(action))bad('Unknown action');
 return json({result:await restaurantAction(b,visitor,role,action,data)});
}catch(e){return error(e)}}
