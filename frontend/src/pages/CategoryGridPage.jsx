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
import CategoryIcon from "../components/CategoryIcon";

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
        <section className="w-full max-w-5xl rounded-2xl bg-white border border-slate-200 px-6 py-8 sm:px-10 sm:py-10 grid md:grid-cols-[1.05fr_0.95fr] items-center gap-6">
          <div className="order-2 md:order-1">
            <p className="text-[13px] text-clinical-teal font-medium mb-3">{t("landing.heroEyebrow")}</p>
            <h1 className="text-3xl sm:text-5xl font-semibold tracking-tight text-ink max-w-xl">{t("landing.heroTitle")}</h1>
            <p className="text-slate-600 leading-relaxed mt-4 max-w-lg">{t("landing.heroBody")}</p>
            {/* Concrete mechanics, not vague trust badges — each line names
                an actual thing this system does, not a marketing word. */}
            <ul className="mt-6 flex flex-col gap-2 text-sm text-slate-600">
              <li className="flex items-start gap-2">
                <span className="text-clinical-teal mt-0.5">—</span>
                {t("landing.trust.safety")}
              </li>
              <li className="flex items-start gap-2">
                <span className="text-clinical-teal mt-0.5">—</span>
                {t("landing.trust.evidence")}
              </li>
              <li className="flex items-start gap-2">
                <span className="text-clinical-teal mt-0.5">—</span>
                {t("landing.trust.privacy")}
              </li>
            </ul>
          </div>
          <div className="order-1 md:order-2 min-h-[220px] flex items-center justify-center">
            <Hero3D height={260} />
          </div>
        </section>

        <div className="w-full max-w-2xl mt-12 mb-6">
          <p className="text-[13px] text-clinical-teal font-medium mb-2">{t("landing.categoryEyebrow")}</p>
          <h2 className="text-2xl sm:text-3xl font-semibold tracking-tight text-ink">{t("landing.chooseCategory")}</h2>
          <p className="text-sm text-slate-500 mt-2">{t("landing.categorySubtitle")}</p>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 max-w-2xl w-full">
          {categories.map((cat) => (
            <button
              key={cat.code}
              onClick={() => navigate(`/triage/${cat.code}`)}
              className="bg-white border border-slate-200 rounded-xl p-5 flex flex-col items-center gap-2.5 hover:border-clinical-teal transition-colors"
            >
              <CategoryIcon code={cat.code} className="w-6 h-6 text-clinical-teal" />
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
