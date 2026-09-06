import { useEffect, useState } from "react";
import { useLanguage } from "../context/LanguageContext";
import { fetchContent } from "../services/triageService";

export default function DisclaimerBanner() {
  const { language } = useLanguage();
  const [text, setText] = useState("");

  useEffect(() => {
    fetchContent("disclaimer_banner", language)
      .then(setText)
      .catch(() =>
        setText(
          "This tool provides decision support and is not a medical diagnosis."
        )
      );
  }, [language]);

  return (
    <div className="w-full bg-slate-100 border-b border-slate-200 text-slate-700 text-sm px-4 py-2 text-center">
      {text}
    </div>
  );
}
