import { useEffect, useState } from "react";
import { fetchStats } from "../../services/adminService";

const SEVERITY_ORDER = ["EMERGENCY", "URGENT", "ROUTINE", "SELF_CARE"];
const SEVERITY_STYLE = {
  EMERGENCY: "bg-severity-emergency",
  URGENT: "bg-severity-urgent",
  ROUTINE: "bg-severity-routine",
  SELF_CARE: "bg-severity-selfcare",
};

function StatCard({ label, value, sub }) {
  return (
    <div className="bg-white border border-slate-200 rounded-xl p-4">
      <p className="text-xs text-slate-500 mb-1">{label}</p>
      <p className="text-2xl font-semibold text-ink font-mono tabular-nums">{value}</p>
      {sub && <p className="text-xs text-slate-400 mt-1">{sub}</p>}
    </div>
  );
}

function BarRow({ label, count, total, colorClass }) {
  const pct = total > 0 ? Math.round((count / total) * 100) : 0;
  return (
    <div className="mb-3 last:mb-0">
      <div className="flex justify-between text-sm mb-1">
        <span className="text-ink">{label}</span>
        <span className="font-mono tabular-nums text-slate-500">{count}</span>
      </div>
      <div className="h-1.5 bg-slate-100 rounded-full overflow-hidden">
        <div className={`h-full rounded-full ${colorClass}`} style={{ width: `${pct}%` }} />
      </div>
    </div>
  );
}

export default function AdminDashboardPage() {
  const [stats, setStats] = useState(null);
  const [error, setError] = useState(false);

  useEffect(() => {
    fetchStats().then(setStats).catch(() => setError(true));
  }, []);

  if (error) {
    return <p className="text-sm text-severity-urgent">Unable to load dashboard stats.</p>;
  }
  if (!stats) {
    return <p className="text-sm text-slate-400">Loading…</p>;
  }

  const total = stats.total_sessions || 0;
  const guardrailPct = total > 0 ? Math.round((stats.by_source.guardrail / total) * 100) : 0;
  const topCategory = stats.by_category[0]?.category || "—";

  return (
    <div>
      <h1 className="text-xl font-semibold text-ink mb-1">Dashboard</h1>
      <p className="text-sm text-slate-500 mb-6">
        Manage symptoms, bilingual UI content, the RAG knowledge base, and view the triage
        session log from the sidebar.
      </p>

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-8">
        <StatCard label="Total sessions" value={total} />
        <StatCard
          label="Caught by safety guardrail"
          value={`${guardrailPct}%`}
          sub={`${stats.by_source.guardrail} of ${total} — before any LLM call`}
        />
        <StatCard label="Most common category" value={topCategory} />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="bg-white border border-slate-200 rounded-xl p-4">
          <p className="text-sm font-medium text-ink mb-3">Severity breakdown</p>
          {SEVERITY_ORDER.map((sev) => (
            <BarRow
              key={sev}
              label={sev}
              count={stats.by_severity[sev] || 0}
              total={total}
              colorClass={SEVERITY_STYLE[sev]}
            />
          ))}
        </div>

        <div className="bg-white border border-slate-200 rounded-xl p-4">
          <p className="text-sm font-medium text-ink mb-3">Top categories</p>
          {stats.by_category.length === 0 && <p className="text-sm text-slate-400">No sessions yet.</p>}
          {stats.by_category.map((c) => (
            <BarRow
              key={c.category}
              label={c.category}
              count={c.count}
              total={stats.by_category[0]?.count || 1}
              colorClass="bg-clinical-teal"
            />
          ))}
        </div>
      </div>

      <div className="mt-4 bg-bg-paper rounded-xl p-4 text-sm text-slate-600">
        <span className="font-medium text-ink">{stats.by_source.llm || 0}</span> sessions were classified by
        the LLM, <span className="font-medium text-ink">{stats.by_source.guardrail || 0}</span> by the
        deterministic safety guardrail, and{" "}
        <span className="font-medium text-ink">{stats.by_source.fallback || 0}</span> fell back to the safe
        default (LLM unavailable).
      </div>
    </div>
  );
}
