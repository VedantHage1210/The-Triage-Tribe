import { useEffect, useState } from "react";
import { fetchSessions } from "../../services/adminService";
import { reportDownloadUrl } from "../../services/triageService";

export default function AdminSessionsPage() {
  const [sessions, setSessions] = useState([]);

  useEffect(() => {
    fetchSessions().then(setSessions);
  }, []);

  return (
    <div>
      <h1 className="text-xl font-semibold text-ink mb-4">Triage Sessions</h1>

      <div className="bg-white border border-slate-200 rounded-xl overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-slate-50 text-slate-500 text-left">
            <tr>
              <th className="p-3">Date</th>
              <th className="p-3">Category</th>
              <th className="p-3">Lang</th>
              <th className="p-3">Severity</th>
              <th className="p-3">Confidence</th>
              <th className="p-3">Source</th>
              <th className="p-3">Patient</th>
              <th className="p-3"></th>
            </tr>
          </thead>
          <tbody>
            {sessions.map((s) => (
              <tr key={s.id} className="border-t border-slate-100">
                <td className="p-3 text-xs">{new Date(s.created_at).toLocaleString()}</td>
                <td className="p-3">{s.category || "—"}</td>
                <td className="p-3 uppercase text-xs">{s.language}</td>
                <td className="p-3">{s.severity_result || "—"}</td>
                <td className="p-3">
                  {s.confidence_score != null ? `${Math.round(s.confidence_score * 100)}%` : "—"}
                </td>
                <td className="p-3 text-xs">{s.triggered_by}</td>
                <td className="p-3">{s.patient_name || "—"}</td>
                <td className="p-3">
                  <a
                    href={reportDownloadUrl(s.id, s.language, s.report_token)}
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
  );
}
