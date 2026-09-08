import api from "./api";

export async function fetchCategories() {
  const { data } = await api.get("/categories");
  return data;
}

export async function submitTriage({ text, language, category, sessionId, patientInfo }) {
  const { data } = await api.post("/triage", {
    text,
    language,
    category,
    session_id: sessionId || null,
    patient_name: patientInfo?.name || null,
    patient_age: patientInfo?.age || null,
    patient_blood_group: patientInfo?.bloodGroup || null,
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
