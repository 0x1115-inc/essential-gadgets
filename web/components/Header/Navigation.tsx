"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useAuth } from "@/context/AuthContext";

const navigation = [
  { name: "Home", href: "/" },
  { name: "Links Management", href: "/links/" },
];

const Navigation = () => {
  const pathname = usePathname();
  const { user } = useAuth();

  return (
    <nav className="ml-6 flex space-x-4">
      {navigation
        .filter((item) => item.name !== "Links Management" || user)
        .map((item) => (
          <Link
            key={item.name}
            href={item.href}
            className={`rounded-md px-3 py-2 text-sm font-medium ${
              pathname === item.href
                ? "bg-blue-400 text-white"
                : "text-gray-600 hover:bg-blue-400 hover:text-white"
            }`}
          >
            {item.name}
          </Link>
        ))}
    </nav>
  );
};

export default Navigation;
