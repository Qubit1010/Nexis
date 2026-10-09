import { notFound } from 'next/navigation';
import { authorised,expired,getBusiness } from '@/lib/db';
import type { RestaurantRole } from '@/lib/restaurant-types';
import Restaurant from './Restaurant';
export default async function RestaurantPage({params,searchParams,role}:{params:Promise<{slug:string}>;searchParams:Promise<Record<string,string|undefined>>;role:RestaurantRole}){
 const {slug}=await params,sp=await searchParams,b=await getBusiness(slug);
 if(!authorised(b,sp.t??null)||b.sector!=='food')notFound();
 if(expired(b))return <div className="hub gone"><div><h1>This restaurant preview has ended</h1><p>Contact NexusPoint for a fresh demo.</p><a href="https://wa.me/923118340514">Contact NexusPoint</a></div></div>;
 return <Restaurant slug={slug} token={b.token} name={b.name} role={role} initialLang={sp.lang==='ur'?'ur':'en'} initialTab={sp.tab} initialReservation={role==='customer'&&sp.reserve==='1'} initialItem={role==='customer'?sp.item:undefined}/>;
}
