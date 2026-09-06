import { useEffect, useState } from "react";
import AdminBilingualField from "../../components/AdminBilingualField";
import { fetchAllContent, updateContent } from "../../services/adminService";

export default function AdminContentPage() {
  const [content, setContent] = useState([]);
  const [savingKey, setSavingKey] = useState(null);

  const load = () => fetchAllContent().then(setContent);

  useEffect(() => {
    load();
  }, []);

  const handleChange = (key, field, value) => {
    setContent((prev) => prev.map((c) => (c.key === key ? { ...c, [field]: value } : c)));
  };

  const handleSave = async (item) => {
    setSavingKey(item.key);
    try {
      await updateContent(item.key, { value_en: item.value_en, value_de: item.value_de });
    } finally {
      setSavingKey(null);
    }
  };

  return (
    <div>
      <h1 className="text-xl font-semibold text-ink mb-4">UI Content</h1>
      <p className="text-sm text-slate-500 mb-6">
        Edit any patient-facing text here — one save updates both languages at once (Section 6.2).
      </p>

      <div className="flex flex-col gap-4">
        {content.map((item) => (
          <div key={item.key} className="bg-white border border-slate-200 rounded-xl p-4">
            <p className="text-xs font-mono text-slate-400 mb-2">{item.key}</p>
            <AdminBilingualField
              label="Value"
              valueEn={item.value_en}
              valueDe={item.value_de}
              onChangeEn={(v) => handleChange(item.key, "value_en", v)}
              onChangeDe={(v) => handleChange(item.key, "value_de", v)}
              multiline
            />
            <button
              onClick={() => handleSave(item)}
              disabled={savingKey === item.key}
              className="mt-2 text-sm bg-clinical-teal text-white rounded-lg px-3 py-1.5"
            >
              {savingKey === item.key ? "Saving..." : "Save"}
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}
