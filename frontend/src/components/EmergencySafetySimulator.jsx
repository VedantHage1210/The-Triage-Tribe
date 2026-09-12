import { useState } from "react";
import { useTranslation } from "react-i18next";

const SCENARIOS = ["cardiac", "stroke", "allergy"];

export default function EmergencySafetySimulator() {
  const { t } = useTranslation();
  const [selectedScenario, setSelectedScenario] = useState(null);

  return (
    <section className="w-full max-w-2xl mt-12 rounded-2xl bg-ink-deep p-6 sm:p-8 text-white">
      <p className="text-[13px] text-teal-300 font-medium mb-2">{t("landing.safetySimulator.eyebrow")}</p>
      <h2 className="text-2xl font-semibold tracking-tight">{t("landing.safetySimulator.title")}</h2>
      <p className="text-sm text-slate-300 mt-2 max-w-lg">{t("landing.safetySimulator.subtitle")}</p>

      <div className="grid gap-2 sm:grid-cols-3 mt-6">
        {SCENARIOS.map((scenario) => (
          <button
            key={scenario}
            type="button"
            onClick={() => setSelectedScenario(scenario)}
            className={`text-left rounded-xl border p-3 transition-colors ${selectedScenario === scenario ? "border-teal-300 bg-teal-300/15" : "border-white/10 bg-white/5 hover:bg-white/10"}`}
          >
            <span className="block text-sm font-semibold">{t(`landing.safetySimulator.scenarios.${scenario}.title`)}</span>
            <span className="block text-xs text-slate-400 mt-1">{t(`landing.safetySimulator.scenarios.${scenario}.symptoms`)}</span>
          </button>
        ))}
      </div>

      {selectedScenario ? (
        <div className="mt-6 rounded-xl bg-white text-slate-900 p-5">
          <div className="flex items-center gap-2 text-red-600 font-semibold text-sm">
            <span className="h-2.5 w-2.5 rounded-full bg-red-600 animate-pulse" />
            {t("landing.safetySimulator.detected")}
          </div>
          <p className="text-lg font-semibold mt-2">{t(`landing.safetySimulator.scenarios.${selectedScenario}.result`)}</p>

          <div className="flex flex-wrap items-center gap-x-3 gap-y-1.5 mt-5 text-[13px] text-slate-500 font-mono">
            {["input", "guardrail", "action"].map((step, index) => (
              <span key={step} className="flex items-center gap-1.5">
                <span className="text-slate-300">{String(index + 1).padStart(2, "0")}</span>
                <span>{t(`landing.safetySimulator.steps.${step}`)}</span>
                {index < 2 && <span className="text-slate-300 hidden sm:inline mx-1">/</span>}
              </span>
            ))}
          </div>

          <p className="text-xs text-slate-500 mt-5 border-t border-slate-100 pt-4">{t("landing.safetySimulator.note")}</p>
        </div>
      ) : (
        <p className="text-xs text-slate-400 mt-5">{t("landing.safetySimulator.prompt")}</p>
      )}
    </section>
  );
}
