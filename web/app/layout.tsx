import type { Metadata } from "next";
import "./styles/globals.css";
import Header from "@/components/Header/Header";
import Footer from "@/components/Footer/Footer";

export const metadata: Metadata = {
  title: "Link Shortener",
  description: "Shorten your links quickly and efficiently.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  // console.log(children);
  return (
    <html lang="en">
      <body className="flex flex-col min-h-screen bg-gray-100">
        <Header />
        {/* Main Content */}
        <main className="flex-grow">
          <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-8">
            {children}
          </div>
        </main>

        {/* Full-Width Footer */}
        <Footer />
      </body>
    </html>
  );
}
