import { useEffect, useState } from "react";
import {
  createKnowledgeBase,
  deleteKnowledgeBase,
  fetchKnowledgeBase,
  updateKnowledgeBase,
} from "../../services/adminService";

const EMPTY_FORM = {
  condition_name: "",
  icd_code: "",
  category: "general",
  associated_symptoms: "",
  typical_severity: "routine",
  guidance_text_en: "",
  guidance_text_de: "",
  source_dataset: "",
};

const toForm = (row) => ({
  ...row,
  associated_symptoms: (row.associated_symptoms || []).join(", "),
});

const toPayload = (form) => ({
  ...form,
  associated_symptoms: form.associated_symptoms.split(",").map((item) => item.trim()).filter(Boolean),
});

export default function AdminKnowledgeBasePage() {
  const [rows, setRows] = useState([]);
  const [form, setForm] = useState(EMPTY_FORM);
  const [editingId, setEditingId] = useState(null);
  const [error, setError] = useState("");

  const loadRows = () => fetchKnowledgeBase().then(setRows).catch(() => setError("Unable to load knowledge base."));

  useEffect(() => {
    loadRows();
  }, []);

  const submit = async (event) => {
    event.preventDefault();
    setError("");
    try {
      const payload = toPayload(form);
      if (editingId) await updateKnowledgeBase(editingId, payload);
      else await createKnowledgeBase(payload);
      setForm(EMPTY_FORM);
      setEditingId(null);
      loadRows();
    } catch {
      setError("Unable to save this entry.");
    }
  };

  const remove = async (id) => {
    if (!window.confirm("Delete this knowledge base entry?")) return;
    await deleteKnowledgeBase(id);
    loadRows();
  };

  return (
    <div>
      <h1 className="text-xl font-semibold text-ink mb-2">Knowledge Base (RAG source)</h1>
      <p className="text-sm text-slate-500 mb-6">Changes require re-running the embedding script before they affect retrieval.</p>

      <form onSubmit={submit} className="bg-white border border-slate-200 rounded-xl p-4 mb-6 grid gap-3 md:grid-cols-2">
        {[["condition_name", "Condition name"], ["icd_code", "ICD code"], ["category", "Category"], ["typical_severity", "Typical severity"], ["associated_symptoms", "Symptoms (comma separated)"], ["source_dataset", "Source"]].map(([name, label]) => (
          <label key={name} className="text-xs text-slate-500">{label}
            <input name={name} value={form[name]} onChange={(event) => setForm({ ...form, [name]: event.target.value })} required={name === "condition_name" || name === "category"} className="mt-1 w-full rounded-lg border border-slate-200 p-2 text-sm" />
          </label>
        ))}
        <label className="text-xs text-slate-500">Guidance (English)
          <textarea name="guidance_text_en" value={form.guidance_text_en} onChange={(event) => setForm({ ...form, guidance_text_en: event.target.value })} required rows={3} className="mt-1 w-full rounded-lg border border-slate-200 p-2 text-sm" />
        </label>
        <label className="text-xs text-slate-500">Guidance (German)
          <textarea name="guidance_text_de" value={form.guidance_text_de} onChange={(event) => setForm({ ...form, guidance_text_de: event.target.value })} rows={3} className="mt-1 w-full rounded-lg border border-slate-200 p-2 text-sm" />
        </label>
        {error && <p className="text-sm text-severity-urgent md:col-span-2">{error}</p>}
        <div className="flex gap-2 md:col-span-2">
          <button className="rounded-lg bg-clinical-teal px-4 py-2 text-sm font-medium text-white">{editingId ? "Update entry" : "Add entry"}</button>
          {editingId && <button type="button" onClick={() => { setEditingId(null); setForm(EMPTY_FORM); }} className="rounded-lg border px-4 py-2 text-sm">Cancel</button>}
        </div>
      </form>

      <div className="grid gap-3">
        {rows.map((row) => (
          <div key={row.id} className="bg-white border border-slate-200 rounded-xl p-4">
            <div className="flex justify-between items-start mb-1">
              <p className="font-medium text-ink">{row.condition_name}</p>
              <span className="text-xs bg-slate-100 text-slate-600 px-2 py-0.5 rounded-full">
                {row.category}
              </span>
            </div>
            <p className="text-xs text-slate-400 mb-2">
              {row.icd_code} · {row.source_dataset}
            </p>
            <p className="text-sm text-ink mb-3">{row.guidance_text_en}</p>
            <div className="flex gap-3 text-xs">
              <button onClick={() => { setEditingId(row.id); setForm(toForm(row)); }} className="text-clinical-teal">Edit</button>
              <button onClick={() => remove(row.id)} className="text-severity-urgent">Delete</button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
