import { dayAfter, localDate } from './healthcare-types.ts';
export type RestaurantRole = 'customer'|'restaurant'|'kitchen';
export type MenuItem = {id:string;name:string;name_ur:string;category:string;description:string;price:number;available:boolean;allergens:string[];art:string};
export type DiningTable = {id:string;name:string;seats:number;area:string;active:boolean};
export type Customer = {id:string;visitor:string;name:string};
export type BasketLine = {itemId:string;quantity:number;spice:'mild'|'medium'|'hot';notes:string};
export type OrderStatus = 'placed'|'accepted'|'preparing'|'ready'|'out_for_delivery'|'completed'|'cancelled';
export type Order = {id:string;customer_id:string;number:number;items:{item_id:string;name:string;name_ur:string;price:number;quantity:number;spice:string;notes:string}[];total:number;mode:'pickup'|'delivery'|'dine_in';address:string;table_id:string|null;notes:string;status:OrderStatus;payment:string;source:string;estimated_at:string;created_at:string;updated_at:string;timeline:{status:OrderStatus;at:string}[]};
export type Reservation = {id:string;customer_id:string;table_id:string;party:number;starts_at:string;ends_at:string;status:'confirmed'|'seated'|'completed'|'cancelled'|'no_show';notes:string;source:string};
export type Settings = {open_min:number;close_min:number;accepting:boolean;prep_minutes:number};
export type RestaurantState = {menu:MenuItem[];tables:DiningTable[];customer:Customer;customers:Customer[];orders:Order[];reservations:Reservation[];busy:Pick<Reservation,'table_id'|'starts_at'|'ends_at'|'status'>[];waitlist:{id:string;customer_id:string;party:number;status:string;notes:string;created_at:string}[];settings:Settings;conversations:import('./healthcare-types.ts').ClinicConversation[];activity:{kind:string;at:string;detail:Record<string,unknown>}[];server_time:string;expires_at:string};
export const money = (n:number)=>`PKR ${n.toLocaleString('en-US')}`;
export function tableSlots(date:string,party:number,tables:DiningTable[],busy:RestaurantState['busy'],settings:Settings,expires:string,now=new Date()) {
 if (!/^\d{4}-\d{2}-\d{2}$/.test(date)||date<localDate(now)||date>dayAfter(localDate(now),13)||!Number.isInteger(party)||party<1||party>20) return [];
 const midnight=new Date(`${date}T00:00:00+05:00`).getTime(); const slots:string[]=[];
 for(let m=settings.open_min;m+90<=settings.close_min;m+=30){
  const start=midnight+m*60000,end=start+90*60000;
  if(start<=now.getTime()||end>new Date(expires).getTime())continue;
  if(tables.some(t=>t.active&&t.seats>=party&&!busy.some(r=>r.table_id===t.id&&['confirmed','seated'].includes(r.status)&&new Date(r.starts_at).getTime()<end&&new Date(r.ends_at).getTime()>start)))slots.push(new Date(start).toISOString());
 }
 return slots;
}
export function nextOrderStatus(o:Order):OrderStatus|null {
 return ({placed:'accepted',accepted:'preparing',preparing:'ready',ready:o.mode==='delivery'?'out_for_delivery':'completed',out_for_delivery:'completed'} as Partial<Record<OrderStatus,OrderStatus>>)[o.status]??null;
}
