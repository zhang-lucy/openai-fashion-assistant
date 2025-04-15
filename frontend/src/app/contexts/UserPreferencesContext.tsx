"use client";

import { createContext, useContext, useState, ReactNode } from "react";

export interface UserPreferences {
  onboardingComplete: boolean;
  userGender: string;
  userPrice: string;
  userStyles: string[];
}

const defaultPreferences: UserPreferences = {
  onboardingComplete: false,
  userGender: "",
  userPrice: "",
  userStyles: [],
};

interface UserPreferencesContextType {
  preferences: UserPreferences;
  updatePreferences: (prefs: Partial<UserPreferences>) => void;
}

const UserPreferencesContext = createContext<
  UserPreferencesContextType | undefined
>(undefined);

export function UserPreferencesProvider({ children }: { children: ReactNode }) {
  const [preferences, setPreferences] =
    useState<UserPreferences>(defaultPreferences);

  const updatePreferences = (prefs: Partial<UserPreferences>) => {
    setPreferences((current) => ({
      ...current,
      ...prefs,
    }));
  };

  return (
    <UserPreferencesContext.Provider value={{ preferences, updatePreferences }}>
      {children}
    </UserPreferencesContext.Provider>
  );
}

export function useUserPreferences() {
  const context = useContext(UserPreferencesContext);
  if (context === undefined) {
    throw new Error(
      "useUserPreferences must be used within a UserPreferencesProvider"
    );
  }
  return context;
}
