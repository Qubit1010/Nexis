import type { Metadata } from "next";
import { GeistSans } from "geist/font/sans";
import { GeistMono } from "geist/font/mono";
import "./globals.css";

export const metadata: Metadata = {
  title: "Weekly Business Review — NexusPoint",
  description:
    "Weekly stats across Upwork, LinkedIn, Instagram, Facebook, content, and productivity.",
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en" className={`dark ${GeistSans.variable} ${GeistMono.variable}`} suppressHydrationWarning>
      <body className="antialiased">
        <main className="relative min-h-screen">{children}</main>
      </body>
    </html>
  );
}
