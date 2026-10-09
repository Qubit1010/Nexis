import HealthcarePage from "@/components/HealthcarePage";
export const dynamic="force-dynamic";
export default function Page(p:{params:Promise<{slug:string}>;searchParams:Promise<Record<string,string|undefined>>}) {return <HealthcarePage {...p} role="patient"/>;}
