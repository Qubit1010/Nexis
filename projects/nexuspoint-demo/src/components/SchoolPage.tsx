import { notFound } from 'next/navigation';
import { authorised,expired,getBusiness } from '@/lib/db';
import type { SchoolRole } from '@/lib/school-types';
import School from './School';
export default async function SchoolPage({params,searchParams,role}:{params:Promise<{slug:string}>;searchParams:Promise<Record<string,string|undefined>>;role:SchoolRole}){
 const {slug}=await params,sp=await searchParams,b=await getBusiness(slug);
 if(!authorised(b,sp.t??null)||b.sector!=='education')notFound();
 if(expired(b))return <div className="hub gone"><div><h1>This school preview has ended</h1><p>Contact NexusPoint for a fresh demo.</p><a href="https://wa.me/923118340514">Contact NexusPoint</a></div></div>;
 return <School slug={slug} token={b.token} name={b.name} role={role} initialLang={sp.lang==='ur'?'ur':'en'} initialTab={sp.tab} initialVisit={role==='parent'&&sp.visit==='1'} initialEnquiry={role==='parent'&&sp.enquire==='1'} initialProgram={role==='parent'?sp.program:undefined}/>;
}
