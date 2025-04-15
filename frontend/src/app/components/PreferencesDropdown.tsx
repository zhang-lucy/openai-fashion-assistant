"use client";

import { useState } from "react";
import { useUserPreferences } from "../contexts/UserPreferencesContext";

interface PreferencesDropdownProps {
  usePreferences: boolean;
  onToggleUsePreferences: (value: boolean) => void;
}

export default function PreferencesDropdown({
  usePreferences,
  onToggleUsePreferences,
}: PreferencesDropdownProps) {
  const { preferences } = useUserPreferences();
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 px-3 py-2 rounded-lg hover:bg-gray-100 transition-colors"
      >
        <svg
          className={`w-5 h-5 transition-transform ${
            isOpen ? "rotate-180" : ""
          }`}
          xmlns="http://www.w3.org/2000/svg"
          viewBox="0 0 20 20"
          fill="currentColor"
        >
          <path d="M10 12a2 2 0 100-4 2 2 0 000 4z" />
          <path
            fillRule="evenodd"
            d="M.458 10C1.732 5.943 5.522 3 10 3s8.268 2.943 9.542 7c-1.274 4.057-5.064 7-9.542 7S1.732 14.057.458 10zM14 10a4 4 0 11-8 0 4 4 0 018 0z"
            clipRule="evenodd"
          />
        </svg>
        Preferences
      </button>

      {isOpen && (
        <div className="absolute right-0 mt-2 w-64 bg-white rounded-lg shadow-lg border p-4 z-10">
          <div className="space-y-3">
            <div className="flex items-center gap-2 pb-2 border-b">
              <input
                type="checkbox"
                id="usePreferences"
                checked={usePreferences}
                onChange={(e) => onToggleUsePreferences(e.target.checked)}
                className="rounded text-blue-500 focus:ring-blue-500"
              />
              <label htmlFor="usePreferences" className="text-sm font-medium">
                Use preferences in search
              </label>
            </div>

            <div>
              <h3 className="text-sm font-semibold text-gray-500">Gender</h3>
              <p className="text-gray-700">
                {preferences.userGender || "Not specified"}
              </p>
            </div>
            <div>
              <h3 className="text-sm font-semibold text-gray-500">
                Price Range
              </h3>
              <p className="text-gray-700">
                {preferences.userPrice || "Not specified"}
              </p>
            </div>
            <div>
              <h3 className="text-sm font-semibold text-gray-500">
                Preferred Styles
              </h3>
              {preferences.userStyles && preferences.userStyles.length > 0 ? (
                <div className="flex flex-wrap gap-1 mt-1">
                  {preferences.userStyles.map((style) => (
                    <span
                      key={style}
                      className="text-xs bg-blue-100 text-blue-700 px-2 py-1 rounded-full"
                    >
                      {style}
                    </span>
                  ))}
                </div>
              ) : (
                <p className="text-gray-700">No styles selected</p>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
