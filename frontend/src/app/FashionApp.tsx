"use client";

import { ReactNode, useState } from "react";
import { searchProducts } from "./lib/api";
import { Product } from "./lib/types";
import PreferencesDropdown from "./components/PreferencesDropdown";
import { useUserPreferences } from "./contexts/UserPreferencesContext";

interface RequestBody {
  gender?: string;
  price?: string;
  styles?: string[];
}

export function Card({ children }: { children: ReactNode }) {
  return (
    <div className="w-full h-[500px] flex flex-col overflow-hidden rounded-2xl shadow border">
      {children}
    </div>
  );
}

export function CardContent({ children }: { children: ReactNode }) {
  return <div className="p-4 flex flex-col h-full">{children}</div>;
}

export function Button({
  onClick,
  children,
}: {
  onClick?: () => void;
  children: React.ReactNode;
}) {
  return (
    <button
      onClick={onClick}
      className="px-4 py-2 bg-black text-white rounded-xl hover:bg-gray-800 transition"
    >
      {children}
    </button>
  );
}

export default function FashionApp() {
  const [items, setItems] = useState<Product[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [usePreferences, setUsePreferences] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");

  const { preferences } = useUserPreferences();

  const handleSearch = async () => {
    console.log("User Preferences", preferences);
    console.log("Use Preferences?", usePreferences);
    if (searchQuery.length > 0) {
      setIsLoading(true);
      try {
        const requestBody: RequestBody = {};

        if (usePreferences) {
          requestBody.gender = preferences.userGender || undefined;
          requestBody.price = preferences.userPrice || undefined;
          requestBody.styles =
            preferences.userStyles.length > 0
              ? preferences.userStyles
              : undefined;
        }

        const results = await searchProducts(searchQuery, requestBody);
        setItems(results);
        console.log("Products", results);
      } catch (err) {
        console.error("Failed to load products:", err);
      } finally {
        setIsLoading(false);
      }
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter") {
      handleSearch();
    }
  };

  return (
    <div className="p-4 max-w-6xl mx-auto">
      <div className="flex justify-between items-center mb-4">
        <h1 className="text-2xl font-bold">Fashion Assistant</h1>
        <PreferencesDropdown
          usePreferences={usePreferences}
          onToggleUsePreferences={setUsePreferences}
        />
      </div>
      <div className="mb-4 flex flex-row gap-2">
        <input
          type="text"
          placeholder="Search for a product, style, vibe"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="border rounded px-3 py-2 text-sm w-full"
          onKeyDown={handleKeyDown}
          disabled={isLoading}
        />
        <button
          onClick={handleSearch}
          disabled={isLoading || searchQuery.length === 0}
          className={`px-4 py-2 rounded flex items-center gap-2 min-w-[100px] justify-center
            ${
              isLoading || searchQuery.length === 0
                ? "bg-gray-200 text-gray-500 cursor-not-allowed opacity-75"
                : "bg-blue-500 text-white hover:bg-blue-600"
            } transition-all duration-200`}
        >
          {isLoading ? (
            <>
              <svg
                className="animate-spin h-4 w-4 text-current"
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
              >
                <circle
                  className="opacity-25"
                  cx="12"
                  cy="12"
                  r="10"
                  stroke="currentColor"
                  strokeWidth="4"
                ></circle>
                <path
                  className="opacity-75"
                  fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                ></path>
              </svg>
              <span>Searching</span>
            </>
          ) : (
            "Search"
          )}
        </button>
      </div>

      {isLoading ? (
        <div className="flex justify-center items-center h-64">
          <div className="flex flex-col items-center gap-4">
            <svg
              className="animate-spin h-8 w-8 text-blue-500"
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
            >
              <circle
                className="opacity-25"
                cx="12"
                cy="12"
                r="10"
                stroke="currentColor"
                strokeWidth="4"
              ></circle>
              <path
                className="opacity-75"
                fill="currentColor"
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
              ></path>
            </svg>
            <p className="text-gray-500">Loading products...</p>
          </div>
        </div>
      ) : (
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
          {items.map((item, index) => (
            <Card key={index}>
              <CardContent className="p-4 flex flex-col h-full overflow-hidden">
                <div className="h-60 w-full mb-2 overflow-hidden rounded-xl shrink-0">
                  <img
                    src={item.imageUrls[0]}
                    alt={item.title}
                    className="w-full h-full object-cover"
                  />
                </div>

                <div className="flex-1 overflow-auto">
                  <h2 className="font-semibold text-lg mb-1 line-clamp-2">
                    {item.title}
                  </h2>
                  <p className="text-sm  mb-1">Store: {item.store}</p>
                  <p className="text-sm  mb-1">
                    Rating: {item.average_rating} ⭐ ({item.rating_number})
                  </p>
                  {item.price && (
                    <p className="text-sm font-medium text-green-700">
                      Price: {item.price}
                    </p>
                  )}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
