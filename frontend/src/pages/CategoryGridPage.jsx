import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { useLanguage } from "../context/LanguageContext";
import { fetchCategories } from "../services/triageService";
import Header from "../components/Header";
import Footer from "../components/Footer";
import DisclaimerBanner from "../components/DisclaimerBanner";
import Hero3D from "../components/Hero3D";

// Section 12.2 — one small, medical-appropriate icon per category,
// no generic tech iconography.
const CATEGORY_ICONS = {
  eyes: "👁",
  skin: "🖐",
  teeth: "🦷",
  heart: "❤",
  digestion: "🫃",
  diabetes: "🩸",
  weight: "⚖",
  general: "＋",
};

export default function CategoryGridPage() {
  const { t } = useTranslation();
  const { language } = useLanguage();
  const navigate = useNavigate();
  const [categories, setCategories] = useState([]);

  useEffect(() => {
    fetchCategories().then(setCategories).catch(() => setCategories([]));
  }, []);

  return (
    <div className="min-h-screen flex flex-col bg-bg-soft">
      <DisclaimerBanner />
      <Header />

      <main className="flex-1 flex flex-col items-center px-6 py-8">
        <Hero3D height={260} />

        <h2 className="text-xl text-ink mb-8 -mt-2">{t("landing.chooseCategory")}</h2>

        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 max-w-2xl w-full">
          {categories.map((cat) => (
            <button
              key={cat.code}
              onClick={() => navigate(`/triage/${cat.code}`)}
              className="bg-white border border-slate-200 rounded-xl p-5 flex flex-col items-center gap-2 hover:border-clinical-teal hover:shadow-md hover:-translate-y-0.5 transition-all"
            >
              <span className="text-2xl">{CATEGORY_ICONS[cat.code] || "＋"}</span>
              <span className="text-ink font-medium text-center text-sm">
                {language === "de" ? cat.label_de : cat.label_en}
              </span>
            </button>
          ))}
        </div>
      </main>

      <Footer />
    </div>
  );
}
