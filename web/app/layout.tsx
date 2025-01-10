import type { Metadata } from "next";
import "./styles/globals.css";
import Header from "@/components/Header/Header";
import Footer from "@/components/Footer/Footer";
import { AuthProvider } from "@/context/AuthContext";
import { ToastContainer } from "react-toastify";

export const metadata: Metadata = {
  title: "Link Shortener",
  description: "Shorten your links quickly and efficiently.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="flex flex-col min-h-screen bg-gray-100">
        <AuthProvider>
          <Header />
          <ToastContainer
            position="top-right"
            autoClose={3000}
            hideProgressBar
          />
          {/* Main Content */}
          <main className="flex-grow">
            <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-8">
              {children}
            </div>
          </main>
        </AuthProvider>

        {/* Full-Width Footer */}
        <Footer />
      </body>
    </html>
  );
}
