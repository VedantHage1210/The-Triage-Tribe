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
        <ul className="flex flex-col gap-1.5">
          {observation.visible_features.map((f, i) => (
            <li key={i} className="text-sm text-slate-600 flex items-start gap-2">
              <span className="text-clinical-teal mt-0.5">—</span>
              {f}
            </li>
          ))}
        </ul>
      )}

      <p className="text-sm text-ink leading-relaxed">{observation.general_note}</p>

      {observation.recommend_professional_check && (
        <p className="text-xs text-clinical-teal font-medium">{t("visualCheck.recommendCheck")}</p>
      )}
    </div>
  );
}
