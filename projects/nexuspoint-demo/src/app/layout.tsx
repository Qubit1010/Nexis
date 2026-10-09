import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "NexusPoint demo",
  robots: { index: false, follow: false },
  icons: {
    icon: [
      { url: "/favicon.ico", sizes: "any" },
      { url: "/favicon.svg", type: "image/svg+xml" },
      { url: "/favicon-32.png", sizes: "32x32", type: "image/png" },
    ],
    apple: "/apple-touch-icon.png",
  },
};

const themeScript = `try{var t=localStorage.getItem("np-theme");if(t==="light"||t==="dark")document.documentElement.dataset.theme=t}catch(e){}`;

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        <script dangerouslySetInnerHTML={{ __html: themeScript }} />
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="" />
        <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Urbanist:wght@400;500;600;700;800&family=JetBrains+Mono:wght@500;700;800&family=Noto+Nastaliq+Urdu:wght@400;600;700&display=swap" />
        <meta name="theme-color" content="#02040A" />
      </head>
      <body>{children}</body>
    </html>
  );
}
