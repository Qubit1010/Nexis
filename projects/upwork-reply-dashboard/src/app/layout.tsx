import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({
  variable: "--font-sans",
  subsets: ["latin"],
  weight: ["400", "500", "600", "700"],
});

export const metadata: Metadata = {
  title: "Upwork Reply Drafter — NexusPoint",
  description:
    "Draft research-backed replies to Upwork client messages — pre-hire negotiation, active-project scope changes, the 5-star review ask, and reactivating past clients.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="dark" suppressHydrationWarning>
      <body className={`${inter.variable} font-sans antialiased bg-[--background] text-[--foreground]`}>
        {children}
      </body>
    </html>
  );
}
