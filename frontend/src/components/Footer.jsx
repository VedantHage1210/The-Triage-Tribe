import { useTranslation } from "react-i18next";
import { Link } from "react-router-dom";

/**
 * Section 12.4 — trust signals: transparency link, non-diagnostic
 * reminder, session/audit framing. Kept understated, not alarming.
 */
export default function Footer() {
  const { t } = useTranslation();

  return (
    <footer className="mt-auto border-t border-slate-100 px-6 py-6 text-xs text-slate-400 flex flex-col sm:flex-row items-center justify-between gap-2">
      <p>{t("footer.tagline", "Decision-support tool — not a substitute for professional medical advice.")}</p>
      <div className="flex items-center gap-4">
        <a
          href="https://github.com/VedantHage1210/The-Triage-Tribe"
          target="_blank"
          rel="noreferrer"
          className="text-clinical-teal hover:underline"
        >
          {t("footer.viewSource", "View source on GitHub")}
        </a>
        <Link to="/how-it-works" className="text-clinical-teal hover:underline">
          {t("nav.howItWorks", "How it works")}
        </Link>
      </div>
    </footer>
  );
}
