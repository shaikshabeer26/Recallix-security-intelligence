
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://127.0.0.1:8000',
  timeout: 90000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Backend root endpoint — returns { success: true, ... }
export const getBackendHealth = async () =>
  (await api.get('/')).data;

export const getAllIncidents = async () =>
  (await api.get('/api/incidents/')).data;

export const getIncident = async (id) =>
  (await api.get(`/api/incidents/${id}`)).data;

export const analyzeIncident = async (incident) =>
  (await api.post('/api/incidents/analyze', incident)).data;

export const verifyIncident = async (id, verified, analyst_notes) =>
  (await api.post(`/api/incidents/${id}/verify`, {
    verified,
    analyst_notes,
  })).data;

export default api;
