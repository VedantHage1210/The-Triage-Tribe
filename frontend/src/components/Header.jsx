import { useTranslation } from "react-i18next";
import { Link } from "react-router-dom";
import LanguageSwitcher from "./LanguageSwitcher";

/**
 * Section 12.2 — clean medical-appropriate icon (pulse-line), no generic
 * tech icons. Pure inline SVG, no image asset needed.
 */
function LogoMark() {
  return (
    <svg width="30" height="30" viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg">
      <circle cx="20" cy="20" r="19" stroke="#0F766E" strokeWidth="2" />
      <path
        d="M6 20H14L17 12L22 28L25 20H34"
        stroke="#0F766E"
        strokeWidth="2.5"
        strokeLinecap="round"
        strokeLinejoin="round"
        fill="none"
      />
    </svg>
  );
}

export default function Header() {
  const { t } = useTranslation();

  return (
    <header className="flex items-center justify-between gap-2 px-4 sm:px-6 py-4 border-b border-slate-100 bg-white/60 backdrop-blur-sm sticky top-0 z-10">
      <Link to="/" className="flex items-center gap-2 min-w-0 shrink">
        <LogoMark />
        <span className="text-base sm:text-lg font-semibold text-ink truncate">{t("nav.appName")}</span>
      </Link>

      <nav className="hidden sm:flex items-center gap-5 text-sm text-slate-500 shrink-0">
        <Link to="/how-it-works" className="hover:text-clinical-teal transition">
          {t("nav.howItWorks", "How it works")}
        </Link>
      </nav>

      <div className="shrink-0">
        <LanguageSwitcher />
      </div>
    </header>
  );
}
