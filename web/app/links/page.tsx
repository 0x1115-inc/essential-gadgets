"use client";

import React, { useState, useEffect } from "react";
import { useAuth } from "@/context/AuthContext";
import { useRouter } from "next/navigation";

interface Link {
  id: number;
  originalLink: string;
  shortenedLink: string;
  datetime: string;
  clicks: number;
  userId: string;
}

const mockData: Link[] = [
  {
    id: 1,
    originalLink: "https://example.com/1",
    shortenedLink: "https://short.ly/1",
    datetime: "2024-01-01 12:34:56",
    clicks: 25,
    userId: "user1",
  },
  {
    id: 2,
    originalLink: "https://example.com/2",
    shortenedLink: "https://short.ly/2",
    datetime: "2024-01-02 14:12:30",
    clicks: 10,
    userId: "user2",
  },
  {
    id: 3,
    originalLink: "https://example.com/3",
    shortenedLink: "https://short.ly/3",
    datetime: "2024-01-03 08:22:10",
    clicks: 5,
    userId: "user1",
  },
];

const Links = () => {
  const [links, setLinks] = useState<Link[]>([]);
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 5;
  const { user, loading: userLoading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    // Immediately redirect non-logged-in users
    if (!userLoading && !user) {
      router.push("/login");
    }
  }, [user, userLoading, router]);

  useEffect(() => {
    if (user && !userLoading) {
      setTimeout(() => {
        if (user.email) {
          setLinks(mockData); // Admin: show all links
        } else {
          setLinks(mockData.filter((link) => link.userId === user.uid)); // User: filter by userId
        }
      }, 500);
    }
  }, [user, userLoading]);

  if (userLoading || !user) {
    // Show nothing during the redirect or loading phase
    return null;
  }

  const totalPages = Math.ceil(links.length / itemsPerPage);
  const paginatedLinks = links.slice(
    (currentPage - 1) * itemsPerPage,
    currentPage * itemsPerPage
  );

  const handlePageChange = (page: number) => {
    if (page > 0 && page <= totalPages) {
      setCurrentPage(page);
    }
  };

  return (
    <div className="bg-gray-100 w-full max-w-5xl mx-auto p-6 rounded-lg shadow-lg">
      <h2 className="text-2xl font-semibold text-gray-800 text-left mb-6">
        Links Management
      </h2>
      {links.length > 0 ? (
        <>
          <div className="overflow-x-auto">
            <table className="table-auto w-full border-collapse border border-gray-300 bg-white">
              <thead>
                <tr className="bg-gray-200">
                  <th className="px-4 py-2 border border-gray-300 text-left">
                    No
                  </th>
                  <th className="px-4 py-2 border border-gray-300 text-left">
                    Original Link
                  </th>
                  <th className="px-4 py-2 border border-gray-300 text-left">
                    Shortened Link
                  </th>
                  <th className="px-4 py-2 border border-gray-300 text-left">
                    Created Date
                  </th>
                  <th className="px-4 py-2 border border-gray-300 text-left">
                    Clicks
                  </th>
                </tr>
              </thead>
              <tbody>
                {paginatedLinks.map((link, index) => (
                  <tr key={link.id} className="hover:bg-gray-100">
                    <td className="px-4 py-2 border border-gray-300">
                      {(currentPage - 1) * itemsPerPage + index + 1}
                    </td>
                    <td className="px-4 py-2 border border-gray-300 truncate max-w-xs">
                      <a
                        href={link.originalLink}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-blue-500 hover:underline"
                      >
                        {link.originalLink}
                      </a>
                    </td>
                    <td className="px-4 py-2 border border-gray-300 truncate max-w-xs">
                      <a
                        href={link.shortenedLink}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-blue-500 hover:underline"
                      >
                        {link.shortenedLink}
                      </a>
                    </td>
                    <td className="px-4 py-2 border border-gray-300">
                      {link.datetime}
                    </td>
                    <td className="px-4 py-2 border border-gray-300">
                      {link.clicks}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          {/* Pagination Controls */}
          <div className="flex justify-center items-center mt-6 space-x-2">
            {Array.from({ length: totalPages }, (_, index) => (
              <button
                key={index}
                onClick={() => handlePageChange(index + 1)}
                className={`px-3 py-1 rounded-md text-sm ${
                  currentPage === index + 1
                    ? "bg-blue-500 text-white"
                    : "bg-gray-200 text-gray-700 hover:bg-blue-500 hover:text-white"
                }`}
              >
                {index + 1}
              </button>
            ))}
          </div>
        </>
      ) : (
        <p className="text-center text-gray-500">No links found.</p>
      )}
    </div>
  );
};

export default Links;
