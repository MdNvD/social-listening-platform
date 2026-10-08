import axios from "axios";

const api = axios.create({
  baseURL:
    import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000",
  headers: {
    "Content-Type": "application/json",
  },
});

export const createSearch = async (keyword) => {
  const response = await api.post("/api/searches", {
    keyword,
  });

  return response.data;
};

export const getSearch = async (searchId) => {
  const response = await api.get(`/api/searches/${searchId}`);

  return response.data;
};

export const getAnalytics = async (searchId) => {
  const response = await api.get(`/api/searches/${searchId}/analytics`);

  return response.data;
};

export const getMentions = async (searchId, params = {}) => {
  const response = await api.get(`/api/searches/${searchId}/mentions`, {
    params,
  });

  return response.data;
};

export default api;