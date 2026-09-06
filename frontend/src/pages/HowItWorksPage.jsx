import { useTranslation } from "react-i18next";
import Header from "../components/Header";
import Footer from "../components/Footer";

export default function HowItWorksPage() {
  const { t } = useTranslation();

  const steps = [
    {
      title: t("howItWorks.step1Title", "1. Symptom extraction"),
      body: t(
        "howItWorks.step1Body",
        "The AI reads your description and pulls out structured symptoms, duration, and severity cues — in English or German."
      ),
    },
    {
      title: t("howItWorks.step2Title", "2. Safety guardrail"),
      body: t(
        "howItWorks.step2Body",
        "A deterministic check runs first. If a known emergency keyword is detected, you get an instant Emergency result — no AI call, no delay."
      ),
    },
    {
      title: t("howItWorks.step3Title", "3. Grounded reasoning"),
      body: t(
        "howItWorks.step3Body",
        "For everything else, the AI retrieves relevant reference conditions from a real medical knowledge base before reasoning — so its answer is tied to actual data, not guesswork."
      ),
    },
    {
      title: t("howItWorks.step4Title", "4. Confidence & follow-up"),
      body: t(
        "howItWorks.step4Body",
        "If the AI isn't confident, it asks a clarifying question instead of guessing — a real back-and-forth, not a single-shot answer."
      ),
    },
  ];

  return (
    <div className="min-h-screen flex flex-col bg-bg-soft">
      <Header />
      <main className="flex-1 max-w-2xl mx-auto px-6 py-12 w-full">
        <h1 className="text-2xl font-semibold text-ink mb-3">
          {t("howItWorks.title", "How this assistant works")}
        </h1>
        <p className="text-slate-500 mb-10">
          {t(
            "howItWorks.subtitle",
            "This tool is built to be explainable, not a black box. Here's exactly what happens when you submit your symptoms."
          )}
        </p>

        <div className="flex flex-col gap-8">
          {steps.map((s, i) => (
            <div key={i} className="flex gap-4">
              <div className="w-8 h-8 rounded-full bg-clinical-teal/10 text-clinical-teal flex items-center justify-center font-semibold text-sm flex-shrink-0">
                {i + 1}
              </div>
              <div>
                <h2 className="font-medium text-ink mb-1">{s.title}</h2>
                <p className="text-sm text-slate-600 leading-relaxed">{s.body}</p>
              </div>
            </div>
          ))}
        </div>

        <div className="mt-12 bg-white border border-slate-200 rounded-xl p-5 text-sm text-slate-600">
          {t(
            "howItWorks.limitation",
            "No AI system can guarantee diagnostic accuracy. This tool is decision support, not a replacement for a licensed medical professional."
          )}
        </div>
      </main>
      <Footer />
    </div>
  );
}
