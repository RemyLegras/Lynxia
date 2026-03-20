import axios from "axios";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

const api = axios.create({
  baseURL: `${API_URL}/api`,
  headers: { "Content-Type": "application/json" },
});

// Automatically inject the Bearer token on every request
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Auth API
export const authApi = {
  login: (email, password) => api.post("/auth/login", { email, password }),
  register: (email, password) => api.post("/auth/register", { email, password }),
  me: () => api.get("/auth/me"),
  stats: () => api.get("/auth/stats"),
  updateMe: (payload) => api.patch("/auth/me", payload),
};

// Documents API
export const documentsApi = {
  list: (limit = 50, offset = 0) => api.get(`/documents/?limit=${limit}&offset=${offset}`),
  get: (id) => api.get(`/documents/${id}`),
  download: (id) => api.get(`/documents/${id}/download`, { responseType: 'blob' }),
  create: (document) => api.post("/documents/", document),
  updateCuratedData: (id, curatedData) => api.post(`/documents/${id}/curated-data`, curatedData),
  updateStatus: (id, status) => api.patch(`/documents/${id}/status`, { status }),
  upload: (file, type = "unknown") => {
    const formData = new FormData();
    formData.append("file", file);
    formData.append("document_type", type);
    return api.post("/documents/upload", formData, {
      headers: { "Content-Type": "multipart/form-data" }
    });
  },
};

export default api;
