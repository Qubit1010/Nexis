import type { Metadata } from "next";
import { Inter, JetBrains_Mono } from "next/font/google";
import { Sidebar } from "@/components/sidebar";
import { BookmarkProvider } from "@/lib/hooks/bookmark-context";
import "./globals.css";

const inter = Inter({
  variable: "--font-sans",
  subsets: ["latin"],
});

const jetbrainsMono = JetBrains_Mono({
  variable: "--font-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Daily Brief — AI/Tech Intelligence",
  description:
    "Editorial intelligence terminal. AI-powered daily digest of the most important developments in AI, tech, and automation.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark" suppressHydrationWarning>
      <body
        className={`${inter.variable} ${jetbrainsMono.variable} font-sans antialiased`}
      >
        <BookmarkProvider>
          <div className="flex h-screen overflow-hidden relative">
            <Sidebar />
            <main className="flex-1 overflow-y-auto scroll-smooth">
              {children}
            </main>
          </div>
        </BookmarkProvider>
      </body>
    </html>
  );
}
