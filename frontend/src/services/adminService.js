import axios from "axios";

const adminApi = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "http://localhost:8000/api",
});

adminApi.interceptors.request.use((config) => {
  const token = localStorage.getItem("admin_token");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

export async function adminLogin(email, password) {
  const { data } = await adminApi.post("/admin/login", { email, password });
  return data.access_token;
}

export async function fetchSymptoms() {
  const { data } = await adminApi.get("/admin/symptoms");
  return data;
}

export async function createSymptom(payload) {
  const { data } = await adminApi.post("/admin/symptoms", payload);
  return data;
}

export async function updateSymptom(id, payload) {
  const { data } = await adminApi.put(`/admin/symptoms/${id}`, payload);
  return data;
}

export async function deleteSymptom(id) {
  await adminApi.delete(`/admin/symptoms/${id}`);
}

export async function fetchAllContent() {
  const { data } = await adminApi.get("/admin/content");
  return data;
}

export async function updateContent(key, payload) {
  const { data } = await adminApi.put(`/admin/content/${key}`, payload);
  return data;
}

export async function fetchSessions() {
  const { data } = await adminApi.get("/admin/sessions");
  return data;
}

export async function fetchKnowledgeBase() {
  const { data } = await adminApi.get("/admin/knowledge-base");
  return data;
}

export default adminApi;
