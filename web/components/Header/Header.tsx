"use client";

import Logo from "./Logo";
import Navigation from "./Navigation";
import { useAuth } from "@/context/AuthContext";
import { signOut, signInWithPopup } from "firebase/auth";
import { auth, googleProvider } from "@/lib/firebase";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { toast } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";

const Header = () => {
  const { user, loading: userLoading, setUser } = useAuth();
  const [loading, setLoading] = useState(true);
  const [showConfirm, setShowConfirm] = useState(false);
  const router = useRouter();

  const handleLogin = async () => {
    try {
      const result = await signInWithPopup(auth, googleProvider);
      setUser(result.user);
      toast.success("Login successful!!");
      router.push("/");
    } catch (error) {
      toast.error("Login failed. Please try again.");
      console.error("Popup login failed:", error);
    }
  };

  const handleLogout = async () => {
    setLoading(true);
    try {
      await signOut(auth);
      setUser(null);
      toast.success("You have been logged out successfully!");
      router.push("/");
    } catch (error) {
      toast.error("Failed to log out. Please try again.");
      console.error("Logout failed:", error);
    }
  };

  const confirmLogout = async () => {
    setShowConfirm(false);
    await handleLogout();
  };

  const cancelLogout = () => setShowConfirm(false);

  return (
    <header className="w-full bg-gray-100 shadow">
      <div className="max-w-screen px-4 sm:px-6 lg:px-8">
        <div className="flex h-16 items-center justify-between">
          <div className="flex items-center">
            <Logo />
            <Navigation />
          </div>
          <div className="flex items-center">
            {userLoading ? (
              <p className="text-gray-800 text-sm font-medium">Loading...</p>
            ) : user ? (
              <>
                <button
                  onClick={() => setShowConfirm(true)}
                  className="ml-4 rounded-md bg-red-500 px-4 py-2 text-sm font-medium text-white hover:bg-red-600"
                >
                  Logout
                </button>
                {showConfirm && (
                  <div className="fixed inset-0 z-50 flex items-center justify-center bg-gray-800 bg-opacity-75">
                    <div className="bg-white p-6 rounded-lg shadow-lg max-w-sm w-full">
                      <p className="text-center text-gray-800 font-medium">
                        Are you sure you want to log out?
                      </p>
                      <div className="mt-4 flex justify-center">
                        <button
                          onClick={cancelLogout}
                          className="px-4 py-2 bg-gray-200 text-gray-800 rounded-md hover:bg-gray-300"
                        >
                          Cancel
                        </button>
                        <button
                          onClick={confirmLogout}
                          className="px-4 py-2 bg-red-500 text-white rounded-md hover:bg-red-600"
                        >
                          Logout
                        </button>
                      </div>
                    </div>
                  </div>
                )}
              </>
            ) : (
              <button
                onClick={handleLogin}
                className="ml-4 rounded-md bg-blue-500 px-4 py-2 text-sm font-medium text-white hover:bg-blue-600"
              >
                Login
              </button>
            )}
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;
