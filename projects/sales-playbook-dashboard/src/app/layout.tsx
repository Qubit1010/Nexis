import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({
  variable: "--font-sans",
  subsets: ["latin"],
  weight: ["400", "500", "600", "700"],
});

export const metadata: Metadata = {
  title: "Sales Playbook Dashboard — NexusPoint",
  description:
    "Draft LinkedIn and Instagram DMs straight from the NexusPoint sales playbook — archetype openers, sequence follow-ups, and live replies that sound human.",
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
