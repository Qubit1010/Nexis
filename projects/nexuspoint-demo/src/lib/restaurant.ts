import { rest, transcript, type Business, type Conversation } from './db.ts';
import { rpc } from './healthcare.ts';
import { tableSlots, type Customer, type DiningTable, type MenuItem, type Order, type Reservation, type RestaurantRole, type RestaurantState, type Settings } from './restaurant-types.ts';
const q=(slug:string)=>`slug=eq.${encodeURIComponent(slug)}`;
const sampleMenu=[
 {name:'Chicken karahi',name_ur:'چکن کڑاہی',category:'Karahi',description:'A sample sharing portion with tomato, ginger and green chilli.',price:1450,allergens:['Dairy'],art:'karahi'},
 {name:'Mutton karahi',name_ur:'مٹن کڑاہی',category:'Karahi',description:'Slow cooked mutton, finished in a traditional karahi.',price:2400,allergens:['Dairy'],art:'karahi'},
 {name:'Chicken sajji',name_ur:'چکن سجی',category:'Grill',description:'Balochistan inspired roast chicken with fragrant rice.',price:1600,allergens:[],art:'sajji'},
 {name:'BBQ platter',name_ur:'باربی کیو پلیٹر',category:'Grill',description:'A sample selection of grilled tikka and seekh kebab.',price:1850,allergens:['Dairy'],art:'grill'},
 {name:'Vegetable rice',name_ur:'سبزی پلاؤ',category:'Sides',description:'Rice with seasonal vegetables. A vegetarian sample option.',price:550,allergens:[],art:'rice'},
 {name:'Butter naan',name_ur:'بٹر نان',category:'Sides',description:'Fresh flatbread with a little butter.',price:120,allergens:['Wheat','Dairy'],art:'naan'},
 {name:'Raita',name_ur:'رائتہ',category:'Sides',description:'A refreshing yogurt side with cucumber and herbs.',price:180,allergens:['Dairy'],art:'raita'},
 {name:'Karak tea',name_ur:'کڑک چائے',category:'Drinks',description:'A warming cup of strong milk tea.',price:180,allergens:['Dairy'],art:'tea'},
 {name:'Fresh lime',name_ur:'لیموں پانی',category:'Drinks',description:'Lime, chilled water and a refreshing citrus finish.',price:250,allergens:[],art:'lime'}
];
export async function ensureRestaurant(b:Business){
 const s=(await rest<Settings>('GET',`demo_restaurant_settings?${q(b.slug)}&seeded=eq.true&limit=1`))[0];
 if(!s)await rpc('demo_restaurant_action',{p_slug:b.slug,p_visitor:'system-seed',p_role:'system',p_action:'seed',p_data:{menu:sampleMenu,tables:[{name:'T01',seats:2,area:'Main hall'},{name:'T02',seats:2,area:'Main hall'},{name:'T03',seats:4,area:'Family section'},{name:'T04',seats:4,area:'Family section'},{name:'T05',seats:6,area:'Family section'},{name:'T06',seats:8,area:'Garden'}]}});
}
export async function restaurantAction<T=unknown>(b:Business,visitor:string,role:RestaurantRole,action:string,data:Record<string,unknown>):Promise<T>{
 await ensureRestaurant(b);
 return rpc<T>('demo_restaurant_action',{p_slug:b.slug,p_visitor:visitor,p_role:role,p_action:action,p_data:data});
}
export async function restaurantState(b:Business,visitor:string,role:RestaurantRole):Promise<RestaurantState>{
 await ensureRestaurant(b);
 const customer=await restaurantAction<Customer>(b,visitor,role,'customer',{});
 const scope=q(b.slug),staff=role==='restaurant',kitchen=role==='kitchen';
 const [menu,tables,settings,customers,orders,allReservations,waitlist,conversations,activity]=await Promise.all([
  rest<MenuItem>('GET',`demo_menu_items?${scope}&order=category,name`),rest<DiningTable>('GET',`demo_restaurant_tables?${scope}&order=name`),
  rest<Settings>('GET',`demo_restaurant_settings?${scope}`),staff?rest<Customer>('GET',`demo_customers?${scope}&order=created_at.desc`):Promise.resolve([customer]),
  rest<Order>('GET',`demo_orders?${scope}${!staff&&!kitchen?`&customer_id=eq.${customer.id}`:''}&order=created_at.desc&limit=200`),
  rest<Reservation>('GET',`demo_reservations?${scope}&order=starts_at&limit=1000`),
  staff?rest<RestaurantState['waitlist'][number]>('GET',`demo_restaurant_waitlist?${scope}&order=created_at`):Promise.resolve([]),
  staff?rest<Conversation>('GET',`demo_conversations?${scope}&order=last_at.desc&limit=50`):Promise.resolve([]),
  staff?rest<RestaurantState['activity'][number]>('GET',`demo_events?${scope}&kind=in.(restaurant_order,table_booking,order_accepted,order_preparing,order_ready,order_completed,order_cancelled,restaurant_notice)&order=at.desc&limit=30`):Promise.resolve([])
 ]);
 return {menu,tables,settings:settings[0],customer,customers:kitchen?[]:customers,
  orders:orders.map(o=>kitchen?{...o,address:'',customer_id:''}:o),reservations:kitchen?[]:staff?allReservations:allReservations.filter(r=>r.customer_id===customer.id),
  busy:allReservations.map(({table_id,starts_at,ends_at,status})=>({table_id,starts_at,ends_at,status})),waitlist,
  conversations:await Promise.all(conversations.map(async c=>({...c,staff_mode:!!c.staff_mode,assigned_to:c.assigned_to??null,messages:await transcript(c.id)}))),activity,server_time:new Date().toISOString(),expires_at:b.expires_at};
}
export async function restaurantAvailability(b:Business,date:string,party:number){
 await ensureRestaurant(b);const scope=q(b.slug);
 const [tables,busy,settings]=await Promise.all([rest<DiningTable>('GET',`demo_restaurant_tables?${scope}`),rest<Reservation>('GET',`demo_reservations?${scope}&status=in.(confirmed,seated)`),rest<Settings>('GET',`demo_restaurant_settings?${scope}`)]);
 return tableSlots(date,party,tables,busy,settings[0],b.expires_at);
}
