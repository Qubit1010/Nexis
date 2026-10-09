import { redirect } from "next/navigation";

// The root has nothing to show: demos live at /d/<slug>?t=<token>.
export default function Home() {
  redirect("https://nexuspoint-quetta.vercel.app/");
}
