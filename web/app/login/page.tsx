"use client";

import { signInWithPopup, signInWithRedirect, signOut } from "firebase/auth";
import { auth, googleProvider } from "@/lib/firebase";
import { useAuth } from "@/context/AuthContext";
import { useRouter } from "next/navigation";

const LoginPage = () => {
  const { user, loading, setUser } = useAuth();
  const router = useRouter();

  const handleLogin = async () => {
    try {
      await signInWithPopup(auth, googleProvider);
      router.push("/");
    } catch (error) {
      console.error("Login failed:", error);
    }
  };

  const handleLogout = async () => {
    try {
      await signOut(auth);
      setUser(null); // Clear the user state
      router.push("/");
    } catch (error) {
      console.error("Logout failed:", error);
    }
  };

  return (
    <div className="flex flex-col items-center justify-start min-h-screen bg-gray-100">
      <h1 className="text-3xl font-semibold mb-8">Login</h1>

      {user ? (
        <>
          <p className="mb-4">Logged in as: {user.email}</p>
          <button
            onClick={handleLogout}
            className="bg-red-500 text-white px-6 py-2 rounded-lg"
          >
            Logout
          </button>
        </>
      ) : (
        <button
          onClick={handleLogin}
          className="bg-blue-500 text-white px-6 py-2 rounded-lg"
        >
          Sign in with Google
        </button>
      )}
    </div>
  );
};

export default LoginPage;
