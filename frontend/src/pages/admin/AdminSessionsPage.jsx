import { useEffect, useState } from "react";
import { fetchSessions } from "../../services/adminService";
import { reportDownloadUrl } from "../../services/triageService";

const SEVERITY_DOT = {
  EMERGENCY: "bg-severity-emergency",
  URGENT: "bg-severity-urgent",
  ROUTINE: "bg-severity-routine",
  SELF_CARE: "bg-severity-selfcare",
};
const SEVERITY_TEXT = {
  EMERGENCY: "text-severity-emergency",
  URGENT: "text-severity-urgent",
  ROUTINE: "text-severity-routine",
  SELF_CARE: "text-severity-selfcare",
};

function formatVitals(vitals) {
  if (!vitals || Object.keys(vitals).length === 0) return [];
  const parts = [];
  if (vitals.spo2_percent != null) parts.push(`SpO2 ${vitals.spo2_percent}%`);
  if (vitals.heart_rate_bpm != null) parts.push(`HR ${vitals.heart_rate_bpm} bpm`);
  if (vitals.bp_systolic != null) parts.push(`BP ${vitals.bp_systolic}${vitals.bp_diastolic ? `/${vitals.bp_diastolic}` : ""}`);
  if (vitals.temperature_c != null) parts.push(`Temp ${vitals.temperature_c}°C`);
  return parts;
}

function VitalsSummary({ vitals }) {
  const parts = formatVitals(vitals);
  if (parts.length === 0) return <span className="text-slate-300">—</span>;
  return <span className="font-mono text-xs">{parts.join(" · ")}</span>;
}

function PatientDetailPanel({ session, onClose }) {
  if (!session) return null;
  const vitalsParts = formatVitals(session.vitals);
  const severityText = SEVERITY_TEXT[session.severity_result] || "text-ink";

  return (
    <div className="fixed inset-0 z-40">
      <div className="absolute inset-0 bg-black/30" onClick={onClose} />
      <div className="absolute right-0 top-0 bottom-0 w-full sm:w-[440px] bg-white shadow-xl overflow-y-auto">
        <div className="flex items-center justify-between px-5 py-4 border-b border-slate-100">
          <p className="text-sm text-slate-500">Patient detail</p>
          <button onClick={onClose} className="text-slate-400 hover:text-slate-600 p-1" aria-label="Close">
            <svg width="18" height="18" viewBox="0 0 20 20" fill="none">
              <path d="M5 5L15 15M15 5L5 15" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" />
            </svg>
          </button>
        </div>

        <div className="p-5 flex flex-col gap-5">
          <div>
            <p className={`text-2xl font-semibold ${severityText}`}>{session.severity_result || "—"}</p>
            <p className="text-xs text-slate-500 mt-1">
              {new Date(session.created_at).toLocaleString()} · {session.category || "—"} ·{" "}
              {session.confidence_score != null ? `${Math.round(session.confidence_score * 100)}% confidence` : "—"} ·{" "}
              {session.triggered_by}
            </p>
          </div>

          {(session.patient_name || session.patient_age || session.patient_blood_group) && (
            <div className="grid grid-cols-3 gap-2 text-sm">
              <div>
                <p className="text-xs text-slate-400">Name</p>
                <p className="font-medium text-ink">{session.patient_name || "—"}</p>
              </div>
              <div>
                <p className="text-xs text-slate-400">Age</p>
                <p className="font-medium text-ink">{session.patient_age || "—"}</p>
              </div>
              <div>
                <p className="text-xs text-slate-400">Blood group</p>
                <p className="font-medium text-ink">{session.patient_blood_group || "—"}</p>
              </div>
            </div>
          )}

          {vitalsParts.length > 0 && (
            <div>
              <p className="text-xs text-slate-500 mb-1.5">Vital signs</p>
              <p className="font-mono text-sm text-ink">{vitalsParts.join(" · ")}</p>
            </div>
          )}

          <div>
            <p className="text-xs text-slate-500 mb-1.5">Reported symptoms</p>
            <p className="text-sm text-ink leading-relaxed">{session.input_text}</p>
          </div>

          {session.key_factors?.length > 0 && (
            <div>
              <p className="text-xs text-slate-500 mb-1.5">What drove this priority</p>
              <ul className="flex flex-col gap-1">
                {session.key_factors.map((f, i) => (
                  <li key={i} className="text-sm text-ink flex items-start gap-2">
                    <span className={severityText}>—</span>
                    {f}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {session.ai_reasoning && (
            <div>
              <p className="text-xs text-slate-500 mb-1.5">Reasoning</p>
              <p className="text-sm text-ink leading-relaxed border-l-2 border-slate-200 pl-3">{session.ai_reasoning}</p>
            </div>
          )}

          {session.cited_conditions?.length > 0 && (
            <div>
              <p className="text-xs text-slate-500 mb-1.5">Matched against</p>
              <p className="text-sm text-slate-600">{session.cited_conditions.join(" · ")}</p>
            </div>
          )}

          {session.recommended_action && (
            <div className="bg-bg-paper rounded-xl p-4">
              <p className="text-xs text-slate-500 mb-1">Recommended action</p>
              <p className="text-sm font-medium text-ink">{session.recommended_action}</p>
            </div>
          )}

          <a
            href={reportDownloadUrl(session.id, session.language, session.report_token)}
            className="text-center bg-clinical-teal text-white rounded-xl py-3 font-medium hover:opacity-90 transition"
          >
            Download Report (PDF)
          </a>
        </div>
      </div>
    </div>
  );
}

export default function AdminSessionsPage() {
  const [sessions, setSessions] = useState([]);
  const [selected, setSelected] = useState(null);

  useEffect(() => {
    fetchSessions().then(setSessions);
  }, []);

  return (
    <div>
      <h1 className="text-xl font-semibold text-ink mb-1">Nurse Triage Queue</h1>
      <p className="text-sm text-slate-500 mb-4">
        Ordered by priority — most urgent first, then longest-waiting within the same priority. Click a row for full detail.
      </p>

      <div className="bg-white border border-slate-200 rounded-xl overflow-hidden">
        <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead className="bg-slate-50 text-slate-500 text-left">
            <tr>
              <th className="p-3">Priority</th>
              <th className="p-3">Time</th>
              <th className="p-3">Category</th>
              <th className="p-3">Patient</th>
              <th className="p-3">Vitals</th>
              <th className="p-3">Key factors</th>
              <th className="p-3">Confidence</th>
              <th className="p-3">Source</th>
              <th className="p-3"></th>
            </tr>
          </thead>
          <tbody>
            {sessions.map((s) => (
              <tr
                key={s.id}
                onClick={() => setSelected(s)}
                className="border-t border-slate-100 align-top cursor-pointer hover:bg-slate-50"
              >
                <td className="p-3">
                  <span className="flex items-center gap-2">
                    <span className={`w-2 h-2 rounded-full ${SEVERITY_DOT[s.severity_result] || "bg-slate-300"}`} />
                    <span className="font-medium">{s.severity_result || "—"}</span>
                  </span>
                </td>
                <td className="p-3 text-xs font-mono">{new Date(s.created_at).toLocaleString()}</td>
                <td className="p-3">{s.category || "—"}</td>
                <td className="p-3">{s.patient_name || "—"}</td>
                <td className="p-3"><VitalsSummary vitals={s.vitals} /></td>
                <td className="p-3 text-xs text-slate-600 max-w-[220px]">
                  {s.key_factors?.length > 0
                    ? s.key_factors.map((f, i) => <div key={i}>— {f}</div>)
                    : "—"}
                </td>
                <td className="p-3 font-mono tabular-nums">
                  {s.confidence_score != null ? `${Math.round(s.confidence_score * 100)}%` : "—"}
                </td>
                <td className="p-3 text-xs">{s.triggered_by}</td>
                <td className="p-3">
                  <a
                    href={reportDownloadUrl(s.id, s.language, s.report_token)}
                    onClick={(e) => e.stopPropagation()}
                    className="text-clinical-teal text-xs"
                  >
                    PDF
                  </a>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        </div>
      </div>

      <PatientDetailPanel session={selected} onClose={() => setSelected(null)} />
    </div>
  );
}