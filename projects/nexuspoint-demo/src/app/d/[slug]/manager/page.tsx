import RealEstatePage from "@/components/RealEstatePage";
export default function Page(p: Parameters<typeof RealEstatePage>[0]) { return <RealEstatePage {...p} role="manager" />; }
