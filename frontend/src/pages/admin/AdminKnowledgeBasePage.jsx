import { useEffect, useState } from "react";
import { fetchKnowledgeBase } from "../../services/adminService";

export default function AdminKnowledgeBasePage() {
  const [rows, setRows] = useState([]);

  useEffect(() => {
    fetchKnowledgeBase().then(setRows);
  }, []);

  return (
    <div>
      <h1 className="text-xl font-semibold text-ink mb-2">Knowledge Base (RAG source)</h1>
      <p className="text-sm text-slate-500 mb-6">
        Read-only for now (Section 18, Day 8). To add or edit entries, update{" "}
        <code className="font-mono text-xs">scripts/seed_data.py</code> and re-run{" "}
        <code className="font-mono text-xs">scripts/embed_knowledge_base.py</code>.
      </p>

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
            <p className="text-sm text-ink">{row.guidance_text_en}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
