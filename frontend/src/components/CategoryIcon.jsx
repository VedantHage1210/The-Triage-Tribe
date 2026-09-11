// Simple, consistent monoline icons — 24x24, stroke-based, matching the
// app's ink/teal palette. Replaces emoji (👁🦷❤ etc.), which render
// inconsistently across Windows/Mac/browsers and carry no unified visual
// language. Each icon is deliberately plain — a small mark, not
// illustration — so the category grid reads as a considered system,
// not a sticker sheet.

const common = {
  fill: "none",
  stroke: "currentColor",
  strokeWidth: 1.5,
  strokeLinecap: "round",
  strokeLinejoin: "round",
};

const ICONS = {
  eyes: (
    <svg viewBox="0 0 24 24" {...common}>
      <path d="M2 12C4.5 7.5 8 5.5 12 5.5S19.5 7.5 22 12c-2.5 4.5-6 6.5-10 6.5S4.5 16.5 2 12Z" />
      <circle cx="12" cy="12" r="2.75" />
    </svg>
  ),
  skin: (
    <svg viewBox="0 0 24 24" {...common}>
      <path d="M7 4.5c-2.5 1-4.5 4-4.5 7.5s2 6.5 4.5 7.5" />
      <path d="M17 4.5c2.5 1 4.5 4 4.5 7.5s-2 6.5-4.5 7.5" />
      <circle cx="9.5" cy="10.5" r="1" />
      <circle cx="14.5" cy="14" r="1" />
      <circle cx="12" cy="8" r="1" />
    </svg>
  ),
  teeth: (
    <svg viewBox="0 0 24 24" {...common}>
      <path d="M6 4c-2 0-3 2-3 4.5 0 3 1 9 2.5 11 .8 1 1.7.5 2-.5l1-4c.2-.8.8-1.3 1.5-1.3s1.3.5 1.5 1.3l1 4c.3 1 1.2 1.5 2 .5C16 17 17 11 17 8.5 17 6 16 4 14 4c-1.2 0-1.6.7-2 1.5C11.6 4.7 11.2 4 10 4H6Z" transform="translate(2.5 0)" />
    </svg>
  ),
  heart: (
    <svg viewBox="0 0 24 24" {...common}>
      <path d="M12 20.5s-7.5-4.7-9.8-9.4C.8 7.8 2.3 4.5 5.6 4c2-.3 3.7.7 4.7 2.2l1.7 2.5 1.7-2.5c1-1.5 2.7-2.5 4.7-2.2 3.3.5 4.8 3.8 3.4 7.1C19.5 15.8 12 20.5 12 20.5Z" />
      <path d="M6.5 12h2.3l1.5-2.5 2 5 1.3-2.5h3.4" />
    </svg>
  ),
  digestion: (
    <svg viewBox="0 0 24 24" {...common}>
      <path d="M9 3c0 2-2 2.5-2 5s2 3 2 5.5-2.5 3-2.5 5.5" />
      <path d="M15 3c1.5 1.5.5 3 2 5s2.5 2.5 2.5 5-1.5 3.5-1 6" />
      <path d="M12 8v9" />
      <circle cx="12" cy="19" r="1.4" />
    </svg>
  ),
  diabetes: (
    <svg viewBox="0 0 24 24" {...common}>
      <path d="M12 3c2.5 4 5 7.2 5 10.5a5 5 0 0 1-10 0C7 10.2 9.5 7 12 3Z" />
      <path d="M9.5 13.5h5" />
    </svg>
  ),
  weight: (
    <svg viewBox="0 0 24 24" {...common}>
      <circle cx="12" cy="12" r="9" />
      <path d="M12 12 8.5 9" />
      <path d="M7 12h1M16 12h1M12 5v1M12 18v1" />
    </svg>
  ),
  general: (
    <svg viewBox="0 0 24 24" {...common}>
      <circle cx="12" cy="12" r="9" />
      <path d="M12 8v8M8 12h8" />
    </svg>
  ),
};

export default function CategoryIcon({ code, className = "w-6 h-6" }) {
  return <span className={className}>{ICONS[code] || ICONS.general}</span>;
}
