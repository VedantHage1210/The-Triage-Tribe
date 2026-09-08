import { useTranslation } from "react-i18next";
import { useLanguage } from "../context/LanguageContext";
import { reportDownloadUrl } from "../services/triageService";

const SEVERITY_STYLES = {
  EMERGENCY: "bg-severity-emergency",
  URGENT: "bg-severity-urgent",
  ROUTINE: "bg-severity-routine",
  SELF_CARE: "bg-severity-selfcare",
};

export default function TriageResultCard({ result }) {
  const { t } = useTranslation();
  const { language } = useLanguage();

  if (!result) return null;

  const badgeClass = SEVERITY_STYLES[result.severity] || "bg-slate-400";
  const nextStepKey = {
    EMERGENCY: "Emergency",
    URGENT: "Urgent",
    ROUTINE: "Routine",
    SELF_CARE: "SelfCare",
  }[result.severity] || "Routine";
  const confidence = Math.round((result.confidence || 0) * 100);
  const isGuardrail = result.triggered_by === "guardrail";

  return (
    <div className="w-full max-w-md mx-auto flex flex-col gap-4">
      <div className="bg-slate-950 text-white rounded-3xl p-6 shadow-xl relative overflow-hidden">
        <div className="absolute -right-12 -top-12 h-36 w-36 rounded-full border border-white/10" />
        <div className="relative flex items-start justify-between gap-4">
          <div>
            <p className="text-xs uppercase tracking-[0.2em] text-teal-300 mb-2">{t("result.assessmentLabel")}</p>
            <h2 className="text-2xl font-semibold tracking-tight">{t(`result.severity.${result.severity}`)}</h2>
          </div>
          <div className={`shrink-0 text-white text-xs font-semibold px-3 py-1.5 rounded-full ${badgeClass}`}>
            {t(`result.severity.${result.severity}`)}
          </div>
        </div>
        <div className="relative mt-6 grid grid-cols-2 gap-3">
          <div className="rounded-2xl bg-white/10 p-3">
            <p className="text-[11px] uppercase tracking-wide text-slate-300">{t("result.confidence")}</p>
            <p className="text-2xl font-semibold mt-1">{confidence}%</p>
          </div>
          <div className="rounded-2xl bg-white/10 p-3">
            <p className="text-[11px] uppercase tracking-wide text-slate-300">{t("result.decisionSource")}</p>
            <p className="text-sm font-semibold mt-2">{isGuardrail ? t("result.safetyGuardrail") : t("result.groundedAI")}</p>
          </div>
        </div>
      </div>

      <div className="bg-white rounded-2xl shadow-sm border border-slate-200 p-6 flex flex-col gap-4">
        <div>
          <p className="text-xs font-semibold uppercase tracking-wide text-clinical-teal mb-2">{t("result.reasoningLabel")}</p>
          <p className="text-ink leading-relaxed">{result.reasoning}</p>
        </div>

        <div className="rounded-xl bg-slate-50 border border-slate-100 p-4">
          <p className="text-xs font-semibold uppercase tracking-wide text-slate-500 mb-2">{t("result.nextSteps")}</p>
          <p className="text-sm text-ink leading-relaxed">{t(`result.nextSteps${nextStepKey}`)}</p>
        </div>

        {result.cited_conditions?.length > 0 && (
          <div>
            <p className="text-xs text-slate-500 mb-2">{t("result.matchedAgainst")}</p>
            <div className="flex flex-wrap gap-2">
              {result.cited_conditions.map((condition) => (
                <span key={condition} className="text-xs bg-teal-50 text-clinical-teal border border-teal-100 px-2.5 py-1.5 rounded-lg">
                  {condition}
                </span>
              ))}
            </div>
          </div>
        )}

        <div className="border-t border-slate-100 pt-4">
          <p className="text-xs text-slate-500 mb-1">{t("result.recommendedAction")}</p>
          <p className="font-medium text-ink">{result.recommended_action}</p>
        </div>

        <div className="pt-1">
          <p className="text-xs font-semibold uppercase tracking-wide text-slate-500 mb-3">{t("result.processTitle")}</p>
          <div className="grid grid-cols-3 gap-2 text-center">
            {["signal", "safety", "action"].map((step, index) => (
              <div key={step} className="relative">
                <div className="mx-auto h-8 w-8 rounded-full bg-clinical-teal text-white text-sm font-semibold flex items-center justify-center">{index + 1}</div>
                <p className="text-[11px] text-slate-600 mt-2 leading-tight">{t(`result.process.${step}`)}</p>
                {index < 2 && <span className="absolute top-4 left-[58%] w-[84%] border-t border-dashed border-slate-300" />}
              </div>
            ))}
          </div>
        </div>

        <a href={reportDownloadUrl(result.session_id, language, result.report_token)} className="text-center bg-clinical-teal text-white rounded-xl py-3 mt-2 hover:opacity-90 transition font-medium">
          {t("result.downloadReport")}
        </a>
      </div>
    </div>
  );
}
