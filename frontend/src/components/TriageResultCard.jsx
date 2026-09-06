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

  return (
    <div className="w-full max-w-md mx-auto bg-white rounded-2xl shadow-sm border border-slate-200 p-6 flex flex-col gap-4">
      <div className={`self-start text-white text-sm font-medium px-3 py-1 rounded-full ${badgeClass}`}>
        {t(`result.severity.${result.severity}`)}
      </div>

      <p className="text-ink leading-relaxed">{result.reasoning}</p>

      <div className="rounded-xl bg-slate-50 border border-slate-100 p-4">
        <p className="text-xs font-semibold uppercase tracking-wide text-slate-500 mb-2">
          {t("result.nextSteps")}
        </p>
        <p className="text-sm text-ink leading-relaxed">
          {t(`result.nextSteps${nextStepKey}`)}
        </p>
      </div>

      {result.cited_conditions?.length > 0 && (
        <div>
          <p className="text-xs text-slate-500 mb-1">{t("result.matchedAgainst")}</p>
          <div className="flex flex-wrap gap-2">
            {result.cited_conditions.map((c) => (
              <span
                key={c}
                className="text-xs bg-slate-100 text-slate-700 px-2 py-1 rounded-full"
              >
                {c}
              </span>
            ))}
          </div>
        </div>
      )}

      <div className="border-t border-slate-100 pt-4">
        <p className="text-xs text-slate-500 mb-1">{t("result.recommendedAction")}</p>
        <p className="font-medium text-ink">{result.recommended_action}</p>
      </div>

      <a
        href={reportDownloadUrl(result.session_id, language)}
        className="text-center bg-clinical-teal text-white rounded-lg py-2 mt-2 hover:opacity-90 transition"
      >
        {t("result.downloadReport")}
      </a>
    </div>
  );
}
