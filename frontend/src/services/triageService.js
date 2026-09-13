import api from "./api";

export async function fetchCategories() {
  const { data } = await api.get("/categories");
  return data;
}

export async function submitTriage({ text, language, category, sessionId, patientInfo, vitals }) {
  const toNumber = (v) => (v === "" || v === undefined || v === null ? undefined : Number(v));
  const vitalsPayload = vitals
    ? {
        heart_rate_bpm: toNumber(vitals.heartRate),
        bp_systolic: toNumber(vitals.bpSystolic),
        bp_diastolic: toNumber(vitals.bpDiastolic),
        temperature_c: toNumber(vitals.temperature),
        spo2_percent: toNumber(vitals.spo2),
      }
    : undefined;
  const hasAnyVital = vitalsPayload && Object.values(vitalsPayload).some((v) => v !== undefined);

  const { data } = await api.post("/triage", {
    text,
    language,
    category,
    session_id: sessionId || null,
    patient_name: patientInfo?.name || null,
    patient_age: patientInfo?.age || null,
    patient_blood_group: patientInfo?.bloodGroup || null,
    vitals: hasAnyVital ? vitalsPayload : null,
  });
  return data;
}

export async function fetchContent(key, lang) {
  const { data } = await api.get(`/content/${key}`, { params: { lang } });
  return data.value;
}

export async function fetchSymptoms(category, lang) {
  const { data } = await api.get("/symptoms", { params: { category, lang } });
  return data;
}

export async function submitVisualCheck({ sessionId, category, language, file }) {
  const formData = new FormData();
  formData.append("session_id", sessionId);
  formData.append("category", category);
  formData.append("language", language);
  formData.append("image", file);

  const { data } = await api.post("/visual-check", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return data;
}

export function reportDownloadUrl(sessionId, lang, reportToken) {
  const base = import.meta.env.VITE_API_URL || "http://localhost:8000/api";
  return `${base}/triage/${sessionId}/report.pdf?lang=${lang}&token=${encodeURIComponent(reportToken)}`;
}