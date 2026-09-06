import { useTranslation } from "react-i18next";

export default function ObservationCard({ observation }) {
  const { t } = useTranslation();
  if (!observation) return null;

  return (
    <div className="w-full max-w-md mx-auto bg-slate-50 border border-slate-200 rounded-2xl p-5 flex flex-col gap-3 mt-4">
      <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">
        {t("visualCheck.observationTitle")}
      </p>

      {observation.visible_features?.length > 0 && (
        <div className="flex flex-wrap gap-2">
          {observation.visible_features.map((f, i) => (
            <span key={i} className="text-xs bg-white border border-slate-200 text-slate-600 px-2 py-1 rounded-full">
              {f}
            </span>
          ))}
        </div>
      )}

      <p className="text-sm text-ink leading-relaxed">{observation.general_note}</p>

      {observation.recommend_professional_check && (
        <p className="text-xs text-clinical-teal font-medium">{t("visualCheck.recommendCheck")}</p>
      )}
    </div>
  );
}
