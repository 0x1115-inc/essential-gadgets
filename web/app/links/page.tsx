"use client";

import React, { useState, useEffect } from "react";

interface Link {
  id: number;
  originalLink: string;
  shortenedLink: string;
  datetime: string;
  clicks: number;
}

const mockData: Link[] = [
  {
    id: 1,
    originalLink: "https://example.com/1",
    shortenedLink: "https://short.ly/1",
    datetime: "2024-01-01 12:34:56",
    clicks: 25,
  },
  {
    id: 2,
    originalLink: "https://example.com/2",
    shortenedLink: "https://short.ly/2",
    datetime: "2024-01-02 14:12:30",
    clicks: 10,
  },
  {
    id: 3,
    originalLink: "https://example.com/3",
    shortenedLink: "https://short.ly/3",
    datetime: "2024-01-03 08:22:10",
    clicks: 5,
  },
  {
    id: 4,
    originalLink: "https://example.com/4",
    shortenedLink: "https://short.ly/4",
    datetime: "2024-01-04 09:45:20",
    clicks: 15,
  },
  {
    id: 5,
    originalLink: "https://example.com/5",
    shortenedLink: "https://short.ly/5",
    datetime: "2024-01-05 11:30:00",
    clicks: 20,
  },
  {
    id: 6,
    originalLink: "https://example.com/6",
    shortenedLink: "https://short.ly/6",
    datetime: "2024-01-06 07:10:15",
    clicks: 12,
  },
  // Add more mock data
];

const Links = () => {
  const [links, setLinks] = useState<Link[]>([]);
  const [currentPage, setCurrentPage] = useState(1);
  const [itemsPerPage] = useState(5);

  useEffect(() => {
    // Simulate fetching data (Replace with API call)
    setTimeout(() => {
      setLinks(mockData);
    }, 500);
  }, []);

  const totalPages = Math.ceil(links.length / itemsPerPage);
  const paginatedLinks = links.slice(
    (currentPage - 1) * itemsPerPage,
    currentPage * itemsPerPage
  );

  const handlePageChange = (page: number) => {
    setCurrentPage(page);
  };

  return (
    <div className="bg-gray-100 w-full max-w-5xl mx-auto p-6 rounded-lg shadow-lg">
      <h2 className="text-2xl font-semibold text-gray-800 text-left mb-6">
        Links Management
      </h2>

      <div className="overflow-x-auto">
        <table className="table-auto w-full border-collapse border border-gray-300 bg-white">
          <thead>
            <tr className="bg-gray-200">
              <th className="px-4 py-2 border border-gray-300 text-left">No</th>
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
            {paginatedLinks.length === 0 ? (
              <tr>
                <td
                  colSpan={5}
                  className="px-4 py-2 border border-gray-300 text-center text-gray-500"
                >
                  Loading...
                </td>
              </tr>
            ) : (
              paginatedLinks.map((link, index) => (
                <tr key={link.id} className="hover:bg-gray-100">
                  <td className="px-4 py-2 border border-gray-300">
                    {index + 1}
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
              ))
            )}
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
    </div>
  );
};

export default Links;
