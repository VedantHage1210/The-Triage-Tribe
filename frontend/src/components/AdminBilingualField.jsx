/**
 * Section 6.2 — every admin add/edit form uses this: one field pair,
 * English required, German optional (falls back to English if left blank).
 * One save writes both languages in a single submit, never a separate
 * "switch to German mode" flow.
 */
export default function AdminBilingualField({ label, valueEn, valueDe, onChangeEn, onChangeDe, multiline }) {
  const InputTag = multiline ? "textarea" : "input";

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
      <div>
        <label className="text-xs text-slate-500 mb-1 block">{label} (EN)</label>
        <InputTag
          value={valueEn}
          onChange={(e) => onChangeEn(e.target.value)}
          rows={multiline ? 3 : undefined}
          className="w-full rounded-lg border border-slate-200 p-2 text-sm focus:outline-none focus:ring-2 focus:ring-clinical-teal"
        />
      </div>
      <div>
        <label className="text-xs text-slate-500 mb-1 block">{label} (DE) — optional</label>
        <InputTag
          value={valueDe || ""}
          onChange={(e) => onChangeDe(e.target.value)}
          rows={multiline ? 3 : undefined}
          className="w-full rounded-lg border border-slate-200 p-2 text-sm focus:outline-none focus:ring-2 focus:ring-clinical-teal"
        />
      </div>
    </div>
  );
}
