import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Website Quality Scorer",
  description: "ML-driven website evaluation with SHAP-based explainability",
  icons: { icon: "/icon.svg" },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="h-full">
      <body className="min-h-full antialiased">
        {children}
      </body>
    </html>
  );
}
