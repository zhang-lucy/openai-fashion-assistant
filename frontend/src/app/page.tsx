"use client";

import FashionApp from "./FashionApp";
import OnboardingSurvey from "./components/OnboardingSurvey";
import {
  UserPreferencesProvider,
  useUserPreferences,
} from "./contexts/UserPreferencesContext";

function HomeContent() {
  const { preferences, updatePreferences } = useUserPreferences();

  if (!preferences.onboardingComplete) {
    return (
      <OnboardingSurvey
        onComplete={() => updatePreferences({ onboardingComplete: true })}
      />
    );
  }

  return <FashionApp />;
}

export default function Home() {
  return (
    <UserPreferencesProvider>
      <HomeContent />
    </UserPreferencesProvider>
  );
}
