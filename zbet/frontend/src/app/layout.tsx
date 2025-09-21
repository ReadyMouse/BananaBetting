import type { Metadata } from "next";
import "./globals.css";
import { AuthProvider } from "@/hooks/useAuth";
import Navigation from "@/components/Navigation";
import Disclaimer from "@/components/Disclaimer";

export const metadata: Metadata = {
  title: "Banana Betting - Savannah Bananas Style Sports Betting",
  description: "The most fun and entertaining sports betting experience, inspired by the Savannah Bananas!",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="font-fun antialiased">
        <AuthProvider>
          <Navigation />
          <main className="min-h-screen">
            {children}
          </main>
          <footer className="bg-white/50 backdrop-blur-sm border-t border-banana-200">
            <div className="max-w-6xl mx-auto px-4 py-4">
              <Disclaimer />
            </div>
          </footer>
        </AuthProvider>
      </body>
    </html>
  );
}
