import { useEffect, useState } from "react";
import AdminBilingualField from "../../components/AdminBilingualField";
import {
  createSymptom,
  deleteSymptom,
  fetchSymptoms,
  updateSymptom,
} from "../../services/adminService";

const EMPTY_FORM = { code: "", label_en: "", label_de: "", category: "general", red_flag: false };

export default function AdminSymptomsPage() {
  const [symptoms, setSymptoms] = useState([]);
  const [form, setForm] = useState(EMPTY_FORM);
  const [editingId, setEditingId] = useState(null);
  const [loading, setLoading] = useState(false);

  const load = () => fetchSymptoms().then(setSymptoms);

  useEffect(() => {
    load();
  }, []);

  const resetForm = () => {
    setForm(EMPTY_FORM);
    setEditingId(null);
  };

  const handleSave = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      if (editingId) {
        await updateSymptom(editingId, form);
      } else {
        await createSymptom(form);
      }
      resetForm();
      await load();
    } finally {
      setLoading(false);
    }
  };

  const handleEdit = (symptom) => {
    setForm({
      code: symptom.code,
      label_en: symptom.label_en,
      label_de: symptom.label_de || "",
      category: symptom.category,
      red_flag: symptom.red_flag,
    });
    setEditingId(symptom.id);
  };

  const handleDelete = async (id) => {
    await deleteSymptom(id);
    await load();
  };

  return (
    <div>
      <h1 className="text-xl font-semibold text-ink mb-4">Symptoms</h1>

      <form onSubmit={handleSave} className="bg-white border border-slate-200 rounded-xl p-5 mb-6 flex flex-col gap-3">
        <div className="grid grid-cols-2 gap-3">
          <input
            placeholder="code (e.g. chest_pain)"
            value={form.code}
            onChange={(e) => setForm({ ...form, code: e.target.value })}
            disabled={!!editingId}
            className="rounded-lg border border-slate-200 p-2 text-sm"
            required
          />
          <input
            placeholder="category (e.g. heart, eyes, skin)"
            value={form.category}
            onChange={(e) => setForm({ ...form, category: e.target.value })}
            className="rounded-lg border border-slate-200 p-2 text-sm"
            required
          />
        </div>

        <AdminBilingualField
          label="Label"
          valueEn={form.label_en}
          valueDe={form.label_de}
          onChangeEn={(v) => setForm({ ...form, label_en: v })}
          onChangeDe={(v) => setForm({ ...form, label_de: v })}
        />

        <label className="flex items-center gap-2 text-sm text-slate-600">
          <input
            type="checkbox"
            checked={form.red_flag}
            onChange={(e) => setForm({ ...form, red_flag: e.target.checked })}
          />
          Red flag (triggers instant EMERGENCY, Section 7.1)
        </label>

        <div className="flex gap-2">
          <button type="submit" disabled={loading} className="bg-clinical-teal text-white rounded-lg px-4 py-2 text-sm">
            {editingId ? "Update" : "Add"} Symptom
          </button>
          {editingId && (
            <button type="button" onClick={resetForm} className="text-sm text-slate-500">
              Cancel
            </button>
          )}
        </div>
      </form>

      <div className="bg-white border border-slate-200 rounded-xl overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-slate-50 text-slate-500 text-left">
            <tr>
              <th className="p-3">Code</th>
              <th className="p-3">EN</th>
              <th className="p-3">DE</th>
              <th className="p-3">Category</th>
              <th className="p-3">Red Flag</th>
              <th className="p-3"></th>
            </tr>
          </thead>
          <tbody>
            {symptoms.map((s) => (
              <tr key={s.id} className="border-t border-slate-100">
                <td className="p-3 font-mono text-xs">{s.code}</td>
                <td className="p-3">{s.label_en}</td>
                <td className="p-3">{s.label_de || "—"}</td>
                <td className="p-3">{s.category}</td>
                <td className="p-3">{s.red_flag ? "Yes" : "No"}</td>
                <td className="p-3 flex gap-3">
                  <button onClick={() => handleEdit(s)} className="text-clinical-teal">
                    Edit
                  </button>
                  <button onClick={() => handleDelete(s.id)} className="text-severity-emergency">
                    Delete
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
