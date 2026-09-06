import { useLanguage } from "../context/LanguageContext";

export default function LanguageSwitcher() {
  const { language, setLanguage } = useLanguage();

  return (
    <div className="flex gap-1 rounded-full bg-white border border-slate-200 p-1 text-sm">
      {["en", "de"].map((lang) => (
        <button
          key={lang}
          onClick={() => setLanguage(lang)}
          className={`px-3 py-1 rounded-full transition ${
            language === lang
              ? "bg-clinical-teal text-white"
              : "text-slate-500 hover:text-slate-800"
          }`}
        >
          {lang.toUpperCase()}
        </button>
      ))}
    </div>
  );
}
