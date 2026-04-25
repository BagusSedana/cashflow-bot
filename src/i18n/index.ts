import en from "./en";
import id from "./id";

export type TranslationKey = keyof typeof en;

const translations: Record<string, Record<string, string>> = { en, id };

export function t(key: TranslationKey, language: string = "en"): string {
  const lang = translations[language] || translations["en"];
  return lang[key] || translations["en"][key] || key;
}

export function getSupportedLanguages(): { code: string; name: string }[] {
  return [
    { code: "en", name: "English" },
    { code: "id", name: "Bahasa Indonesia" },
  ];
}
