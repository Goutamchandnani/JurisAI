import type { Metadata } from "next";
import { Inter, Cormorant_Garamond } from "next/font/google";
import "./globals.css";

const inter = Inter({ subsets: ["latin"], variable: "--font-inter" });
const cormorant = Cormorant_Garamond({ 
  subsets: ["latin"], 
  weight: ["400", "600", "700"], 
  variable: "--font-cormorant" 
});

export const metadata: Metadata = {
  title: "JurisAI - Legal Document Intelligence",
  description: "Advanced RAG systems for legal analysis",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={`${inter.variable} ${cormorant.variable} font-sans`}>
        {children}
      </body>
    </html>
  );
}
