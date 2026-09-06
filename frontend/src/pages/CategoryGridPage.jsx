import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { useLanguage } from "../context/LanguageContext";
import { fetchCategories } from "../services/triageService";
import Header from "../components/Header";
import Footer from "../components/Footer";
import DisclaimerBanner from "../components/DisclaimerBanner";
import Hero3D from "../components/Hero3D";
import EmergencySafetySimulator from "../components/EmergencySafetySimulator";

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
        <section className="w-full max-w-5xl rounded-[2rem] bg-gradient-to-br from-teal-50 via-white to-blue-50 border border-white shadow-sm px-6 py-8 sm:px-10 sm:py-10 grid md:grid-cols-[1.05fr_0.95fr] items-center gap-6 overflow-hidden">
          <div className="order-2 md:order-1">
            <p className="text-xs uppercase tracking-[0.2em] text-clinical-teal font-semibold mb-3">{t("landing.heroEyebrow")}</p>
            <h1 className="text-3xl sm:text-5xl font-semibold tracking-tight text-ink max-w-xl">{t("landing.heroTitle")}</h1>
            <p className="text-slate-600 leading-relaxed mt-4 max-w-lg">{t("landing.heroBody")}</p>
            <div className="flex flex-wrap gap-2 mt-6">
              {["safety", "evidence", "privacy"].map((item) => (
                <span key={item} className="rounded-full bg-white/80 border border-slate-200 px-3 py-1.5 text-xs font-medium text-slate-700">
                  {t(`landing.trust.${item}`)}
                </span>
              ))}
            </div>
          </div>
          <div className="order-1 md:order-2 min-h-[220px] flex items-center justify-center">
            <Hero3D height={260} />
          </div>
        </section>

        <div className="w-full max-w-2xl mt-12 mb-6">
          <p className="text-xs uppercase tracking-[0.2em] text-clinical-teal font-semibold mb-2">{t("landing.categoryEyebrow")}</p>
          <h2 className="text-2xl sm:text-3xl font-semibold tracking-tight text-ink">{t("landing.chooseCategory")}</h2>
          <p className="text-sm text-slate-500 mt-2">{t("landing.categorySubtitle")}</p>
        </div>

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

        <EmergencySafetySimulator />
      </main>

      <Footer />
    </div>
  );
}
