import { useState } from "react";
import { useTranslation } from "react-i18next";

const SCENARIOS = ["cardiac", "stroke", "allergy"];

export default function EmergencySafetySimulator() {
  const { t } = useTranslation();
  const [selectedScenario, setSelectedScenario] = useState(null);

  return (
    <section className="w-full max-w-2xl mt-12 rounded-3xl bg-slate-950 p-6 sm:p-8 text-white shadow-xl overflow-hidden relative">
      <div className="absolute -right-16 -top-16 h-44 w-44 rounded-full border border-white/10" />
      <div className="relative">
        <div className="flex items-start justify-between gap-4 mb-6">
          <div>
            <p className="text-xs uppercase tracking-[0.2em] text-teal-300 mb-2">{t("landing.safetySimulator.eyebrow")}</p>
            <h2 className="text-2xl font-semibold tracking-tight">{t("landing.safetySimulator.title")}</h2>
            <p className="text-sm text-slate-300 mt-2 max-w-lg">{t("landing.safetySimulator.subtitle")}</p>
          </div>
          <span className="shrink-0 h-10 w-10 rounded-2xl bg-red-500/20 text-red-300 flex items-center justify-center text-lg">!</span>
        </div>

        <div className="grid gap-2 sm:grid-cols-3">
          {SCENARIOS.map((scenario) => (
            <button
              key={scenario}
              type="button"
              onClick={() => setSelectedScenario(scenario)}
              className={`text-left rounded-2xl border p-3 transition ${selectedScenario === scenario ? "border-teal-300 bg-teal-300/15" : "border-white/10 bg-white/5 hover:bg-white/10"}`}
            >
              <span className="block text-sm font-semibold">{t(`landing.safetySimulator.scenarios.${scenario}.title`)}</span>
              <span className="block text-xs text-slate-400 mt-1">{t(`landing.safetySimulator.scenarios.${scenario}.symptoms`)}</span>
            </button>
          ))}
        </div>

        {selectedScenario ? (
          <div className="mt-6 rounded-2xl bg-white text-slate-900 p-5">
            <div className="flex items-center gap-2 text-red-600 font-semibold text-sm">
              <span className="h-2.5 w-2.5 rounded-full bg-red-600 animate-pulse" />
              {t("landing.safetySimulator.detected")}
            </div>
            <p className="text-lg font-semibold mt-2">{t(`landing.safetySimulator.scenarios.${selectedScenario}.result`)}</p>
            <div className="grid grid-cols-3 gap-2 mt-5 text-center">
              {["input", "guardrail", "action"].map((step, index) => (
                <div key={step} className="relative">
                  <div className="mx-auto h-8 w-8 rounded-full bg-clinical-teal text-white text-sm font-semibold flex items-center justify-center">{index + 1}</div>
                  <p className="text-[11px] text-slate-500 mt-2 leading-tight">{t(`landing.safetySimulator.steps.${step}`)}</p>
                  {index < 2 && <span className="absolute top-4 left-[58%] w-[84%] border-t border-dashed border-slate-300" />}
                </div>
              ))}
            </div>
            <p className="text-xs text-slate-500 mt-5 border-t border-slate-100 pt-4">{t("landing.safetySimulator.note")}</p>
          </div>
        ) : (
          <p className="text-xs text-slate-400 mt-5">{t("landing.safetySimulator.prompt")}</p>
        )}
      </div>
    </section>
  );
}
