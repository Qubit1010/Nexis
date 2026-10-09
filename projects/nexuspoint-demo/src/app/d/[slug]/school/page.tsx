import SchoolPage from '@/components/SchoolPage';
export default function Page(p:{params:Promise<{slug:string}>;searchParams:Promise<Record<string,string|undefined>>}){return <SchoolPage {...p} role="school"/>}
