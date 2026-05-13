import type { Metadata } from "next";
import { Inter } from "next/font/google";
import Link from "next/link";
import { Shield } from "lucide-react";
import { Toaster } from "@/components/ui/sonner";
import "./globals.css";

const inter = Inter({ subsets: ["latin"], variable: "--font-sans" });

export const metadata: Metadata = {
  title: "AI/GenAI Security Review",
  description: "AI/GenAI Security Review Application",
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body className={`${inter.variable} font-sans antialiased bg-gray-50 min-h-screen`}>
        <nav className="bg-white border-b shadow-sm">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex items-center justify-between h-16">
              <Link href="/" className="flex items-center gap-2">
                <Shield className="h-6 w-6 text-blue-600" />
                <span className="font-semibold text-lg text-gray-900">
                  AI/GenAI Security Review
                </span>
              </Link>
              <div className="flex items-center gap-6">
                <Link
                  href="/submit"
                  className="text-sm font-medium text-gray-600 hover:text-gray-900 transition-colors"
                >
                  Submit Infosec Request
                </Link>
                <Link
                  href="/my-submissions"
                  className="text-sm font-medium text-gray-600 hover:text-gray-900 transition-colors"
                >
                  My Submissions
                </Link>
                <Link
                  href="/admin"
                  className="text-sm font-medium text-gray-600 hover:text-gray-900 transition-colors"
                >
                  Admin
                </Link>
              </div>
            </div>
          </div>
        </nav>
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {children}
        </main>
        <Toaster />
      </body>
    </html>
  );
}
