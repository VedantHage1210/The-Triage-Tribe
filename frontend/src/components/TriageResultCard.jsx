import { useTranslation } from "react-i18next";
import { useLanguage } from "../context/LanguageContext";
import { reportDownloadUrl } from "../services/triageService";

// Severity drives the one moment of color boldness on this card — the
// reading itself. Everything else stays quiet so that signal doesn't
// compete with it. Text + border share the same hue; background is a
// low-opacity tint of it, so the whole strip reads as "this reading,
// lit up" rather than a badge glued onto a black panel.
// Fully literal per-severity class strings — required so Tailwind's
// build-time content scanner can see every class name statically
// (interpolating `text-${accent}` would get purged from the prod build).
const SEVERITY_STYLES = {
  EMERGENCY: {
    band: "border-severity-emergency/25 bg-severity-emergency/[0.06]",
    text: "text-severity-emergency",
    bar: "bg-severity-emergency",
    rule: "border-severity-emergency/40",
    button: "bg-severity-emergency",
  },
  URGENT: {
    band: "border-severity-urgent/25 bg-severity-urgent/[0.06]",
    text: "text-severity-urgent",
    bar: "bg-severity-urgent",
    rule: "border-severity-urgent/40",
    button: "bg-severity-urgent",
  },
  ROUTINE: {
    band: "border-severity-routine/25 bg-severity-routine/[0.06]",
    text: "text-severity-routine",
    bar: "bg-severity-routine",
    rule: "border-severity-routine/40",
    button: "bg-severity-routine",
  },
  SELF_CARE: {
    band: "border-severity-selfcare/25 bg-severity-selfcare/[0.06]",
    text: "text-severity-selfcare",
    bar: "bg-severity-selfcare",
    rule: "border-severity-selfcare/40",
    button: "bg-severity-selfcare",
  },
};

export default function TriageResultCard({ result }) {
  const { t } = useTranslation();
  const { language } = useLanguage();

  if (!result) return null;

  const s = SEVERITY_STYLES[result.severity] || SEVERITY_STYLES.ROUTINE;
  const nextStepKey = {
    EMERGENCY: "Emergency",
    URGENT: "Urgent",
    ROUTINE: "Routine",
    SELF_CARE: "SelfCare",
  }[result.severity] || "Routine";
  const confidence = Math.round((result.confidence || 0) * 100);
  const isGuardrail = result.triggered_by === "guardrail";
  const isFallback = result.triggered_by === "fallback";
  const sourceLabel = isGuardrail
    ? t("result.safetyGuardrail")
    : isFallback
    ? t("result.fallbackSource")
    : t("result.groundedAI");

  return (
    <div className="w-full max-w-md mx-auto flex flex-col">
      {/* The reading — one decisive statement, not a heading + a badge
          repeating the same word. Confidence renders as an actual meter,
          since it's the single most decision-relevant number here. */}
      <div className={`rounded-t-2xl border border-b-0 px-6 pt-6 pb-5 ${s.band}`}>
        <p className="text-[13px] text-ink/60 mb-1">{t("result.assessmentLabel")}</p>
        <h2 className={`text-4xl font-semibold tracking-tight leading-none ${s.text}`}>
          {t(`result.severity.${result.severity}`)}
        </h2>

        <div className="mt-5 flex items-end justify-between gap-4">
          <div className="flex-1">
            <div className="flex items-baseline justify-between mb-1.5">
              <span className="text-[13px] text-ink/60">{t("result.confidence")}</span>
              <span className={`font-mono text-sm tabular-nums ${s.text}`}>{confidence}%</span>
            </div>
            <div className="h-1.5 rounded-full bg-ink/10 overflow-hidden">
              <div
                className={`h-full rounded-full ${s.bar}`}
                style={{ width: `${Math.max(confidence, 4)}%` }}
              />
            </div>
          </div>
        </div>

        <p className="mt-4 text-[13px] text-ink/60">
          {t("result.decisionSource")} — <span className="text-ink font-medium">{sourceLabel}</span>
        </p>
      </div>

      {/* Reasoning — an editorial paragraph, not a label-capped box. A
          single accent-colored rule on the left marks it as the model's
          own account, doing the job an eyebrow label would otherwise do. */}
      <div className="bg-white border border-ink/10 rounded-b-2xl px-6 py-6 flex flex-col gap-6">
        <p className={`text-ink leading-relaxed border-l-2 pl-4 ${s.rule}`}>
          {result.reasoning}
        </p>

        {result.cited_conditions?.length > 0 && (
          <div className="text-sm text-ink/70">
            <span className="text-ink/50">{t("result.matchedAgainst")}: </span>
            {result.cited_conditions.map((condition, i) => (
              <span key={condition}>
                <span className="text-ink">{condition}</span>
                {i < result.cited_conditions.length - 1 ? <span className="text-ink/30"> · </span> : null}
              </span>
            ))}
          </div>
        )}

        <div className="rounded-xl bg-bg-paper px-4 py-4">
          <p className="text-[13px] text-ink/60 mb-1">{t("result.recommendedAction")}</p>
          <p className="font-medium text-ink leading-snug">{result.recommended_action}</p>
        </div>

        <div className="rounded-xl bg-bg-paper px-4 py-4">
          <p className="text-[13px] text-ink/60 mb-1">{t("result.nextSteps")}</p>
          <p className="text-sm text-ink leading-relaxed">{t(`result.nextSteps${nextStepKey}`)}</p>
        </div>

        {/* Process trail — this genuinely is a sequence, so a counted
            list is appropriate here, just not the circle+dashed-line
            template version of it. */}
        <div className="flex flex-wrap items-center gap-x-3 gap-y-1.5 text-[13px] text-ink/50 font-mono">
          {["signal", "safety", "action"].map((step, index) => (
            <span key={step} className="flex items-center gap-1.5">
              <span className="text-ink/30">{String(index + 1).padStart(2, "0")}</span>
              <span>{t(`result.process.${step}`)}</span>
              {index < 2 && <span className="text-ink/20 hidden sm:inline mx-1">/</span>}
            </span>
          ))}
        </div>

        <a
          href={reportDownloadUrl(result.session_id, language, result.report_token)}
          className={`text-center text-white rounded-xl py-3 hover:opacity-90 transition font-medium ${s.button}`}
        >
          {t("result.downloadReport")}
        </a>
      </div>
    </div>
  );
}
