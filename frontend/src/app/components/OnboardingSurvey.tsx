import { useState } from "react";
import {
  UserPreferences,
  useUserPreferences,
} from "../contexts/UserPreferencesContext";

interface OnboardingSurveyProps {
  onComplete: () => void;
}

export default function OnboardingSurvey({
  onComplete,
}: OnboardingSurveyProps) {
  const [step, setStep] = useState(1);
  const [selectedStyles, setSelectedStyles] = useState<string[]>([]);
  const { updatePreferences } = useUserPreferences();

  const handleSubmit = (
    field: keyof UserPreferences,
    value: string | string[] | boolean
  ) => {
    updatePreferences({ [field]: value });
    if (step < 3) {
      setStep(step + 1);
    } else {
      updatePreferences({ onboardingComplete: true });
      onComplete();
    }
  };

  const handleSkip = () => {
    if (step < 3) {
      setStep(step + 1);
    } else {
      updatePreferences({ onboardingComplete: true });
      onComplete();
    }
  };

  const handleStyleToggle = (style: string) => {
    setSelectedStyles((current) => {
      if (current.includes(style)) {
        return current.filter((s) => s !== style);
      }
      return [...current, style];
    });
  };

  const handleStylesSubmit = () => {
    updatePreferences({ userStyles: selectedStyles });
    updatePreferences({ onboardingComplete: true });
    onComplete();
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="max-w-md w-full space-y-8 p-8 bg-white rounded-lg shadow">
        <h2 className="text-2xl font-bold text-center text-gray-900">
          Welcome to your new AI Fashion Assistant!
        </h2>
        {step === 1 && (
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <h3 className="text-lg font-medium">
                What gender of apparel are you looking for?
              </h3>
              <button
                onClick={handleSkip}
                className="text-sm text-gray-500 hover:text-gray-700"
              >
                Skip
              </button>
            </div>
            <div className="space-y-2">
              {["Men", "Women", "Unisex"].map((gender) => (
                <button
                  key={gender}
                  onClick={() => handleSubmit("userGender", gender)}
                  className="w-full p-2 text-left border rounded hover:bg-gray-50"
                >
                  {gender}
                </button>
              ))}
            </div>
          </div>
        )}

        {step === 2 && (
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <h3 className="text-lg font-medium">
                What&apos;s your preferred price range?
              </h3>
              <button
                onClick={handleSkip}
                className="text-sm text-gray-500 hover:text-gray-700"
              >
                Skip
              </button>
            </div>
            <div className="space-y-2">
              {["Budget", "Mid-range", "Luxury", "No preference"].map(
                (price) => (
                  <button
                    key={price}
                    onClick={() => handleSubmit("userPrice", price)}
                    className="w-full p-2 text-left border rounded hover:bg-gray-50"
                  >
                    {price}
                  </button>
                )
              )}
            </div>
          </div>
        )}

        {step === 3 && (
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <h3 className="text-lg font-medium">
                What are your preferred styles?
              </h3>
              <button
                onClick={handleSkip}
                className="text-sm text-gray-500 hover:text-gray-700"
              >
                Skip
              </button>
            </div>
            <div className="space-y-2">
              {["Casual", "Formal", "Streetwear", "Vintage", "Minimalist"].map(
                (style) => (
                  <button
                    key={style}
                    onClick={() => handleStyleToggle(style)}
                    className={`w-full p-2 text-left border rounded 
                      ${
                        selectedStyles.includes(style)
                          ? "bg-blue-50 border-blue-500"
                          : "hover:bg-gray-50"
                      }`}
                  >
                    {style}
                    {selectedStyles.includes(style) && (
                      <span className="float-right text-blue-500">✓</span>
                    )}
                  </button>
                )
              )}
            </div>
            <button
              onClick={handleStylesSubmit}
              className={`w-full mt-4 p-2 rounded transition-all duration-200
                ${
                  selectedStyles.length === 0
                    ? "bg-gray-200 text-gray-500 cursor-not-allowed opacity-75"
                    : "bg-blue-500 text-white hover:bg-blue-600"
                }`}
              disabled={selectedStyles.length === 0}
            >
              Let's get started!
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
