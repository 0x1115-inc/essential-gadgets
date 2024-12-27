"use client";

import React, { useState } from "react";
import { ClipboardIcon } from "@heroicons/react/24/outline";
import { ToastContainer, toast } from "react-toastify";

const apiUrl = process.env.NEXT_PUBLIC_BACKEND_API_URL;

const InputForm = () => {
  const [originalLink, setOriginalLink] = useState("");
  const [shortenedLink, setShortenedLink] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const isValidUrl = (url: string) => {
    try {
      new URL(url);
      return true;
    } catch (_) {
      return false;
    }
  };

  const handleGenerate = async () => {
    if (!originalLink || !isValidUrl(originalLink)) {
      toast.error("Please enter a valid URL.");
      return;
    }
    setLoading(true);
    setError("");

    console.log(apiUrl);
    try {
      const response = await fetch(`${apiUrl}`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ url: originalLink }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        setError(errorData.message || "Failed to generate shortened link");
        return;
      }

      const responseData = await response.json();
      setShortenedLink(responseData.data.shortened_url);
    } catch (error: any) {
      setError(error.message || "Something went wrong.");
    } finally {
      setLoading(false);
    }
  };

  const handleCopy = () => {
    if (shortenedLink) {
      navigator.clipboard.writeText(shortenedLink);
      toast.success("Copied to clipboard!");
    }
  };

  return (
    <div className="bg-gray-100 w-full max-w-3xl mx-auto p-6 rounded-lg shadow-lg">
      <ToastContainer position="top-right" autoClose={3000} hideProgressBar />
      <h2 className="text-2xl font-semibold text-gray-800 text-left mb-6">
        Generate Shortened Link
      </h2>

      {/* Original Link */}
      <div className="flex items-center gap-4 mb-6 flex-wrap">
        <label
          htmlFor="original-link"
          className="text-gray-700 font-medium whitespace-nowrap w-full sm:w-1/6"
        >
          Original Link:
        </label>
        <input
          id="original-link"
          type="text"
          value={originalLink}
          onChange={(e) => setOriginalLink(e.target.value)}
          placeholder="Enter the original link"
          className="flex-grow px-4 py-2 text-gray-800 rounded-md border border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
        <button
          onClick={handleGenerate}
          className="bg-blue-500 text-white font-bold py-2 px-4 rounded-md hover:bg-blue-600 transition"
        >
          {loading ? (
            <span>
              <span className="animate-spin mr-2">🔄</span> Generating...
            </span>
          ) : (
            "Generate"
          )}
        </button>
      </div>

      {/* Error Message */}
      {error && (
        <p className="text-red-500 text-sm font-medium mb-6">{error}</p>
      )}

      {/* Final URL */}
      <div className="flex items-center gap-4 mb-6 flex-wrap">
        <label
          htmlFor="final-url"
          className="text-gray-700 font-medium whitespace-nowrap w-full sm:w-1/6"
        >
          Final URL:
        </label>
        <div className="relative flex-grow">
          <input
            id="final-url"
            type="text"
            readOnly
            value={shortenedLink}
            placeholder="Your shortened URL will appear here"
            className="w-full px-4 py-2 text-gray-800 bg-gray-100 rounded-md border border-gray-300 focus:outline-none cursor-not-allowed"
          />
          <button
            onClick={handleCopy}
            disabled={!shortenedLink}
            className={`absolute inset-y-0 right-2 flex items-center ${
              shortenedLink
                ? "text-gray-500 hover:text-gray-700"
                : "text-gray-300 cursor-not-allowed"
            }`}
          >
            <ClipboardIcon className="h-5 w-5" />
          </button>
        </div>
      </div>
    </div>
  );
};

export default InputForm;
