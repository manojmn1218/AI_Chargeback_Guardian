import axios from 'axios';

/**
 * Centralized Axios instance for API calls.
 * Uses the Vite proxy in development (same-origin /api requests).
 */
const api = axios.create({
  baseURL: '/api/v1',
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Response interceptor for centralized error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    const message = error.response?.data?.detail || error.message || 'An unexpected error occurred';
    console.error(`[API Error] ${error.config?.method?.toUpperCase()} ${error.config?.url}: ${message}`);
    return Promise.reject(error);
  }
);

// Helper Service Functions for Evidence Intelligence & Dispute APIs
export const getDisputeInvestigation = async (disputeId) => {
  const response = await api.get(`/disputes/${disputeId}/investigation`);
  return response.data;
};

export const getDisputeTimeline = async (disputeId) => {
  const response = await api.get(`/disputes/${disputeId}/timeline`);
  return response.data;
};

export const getEvidenceSummary = async (disputeId) => {
  const response = await api.get(`/disputes/${disputeId}/evidence-summary`);
  return response.data;
};

export const getDisputeDetail = async (disputeId) => {
  const response = await api.get(`/disputes/${disputeId}`);
  return response.data;
};

export const getDisputesList = async (params = {}) => {
  const response = await api.get('/disputes', { params });
  return response.data;
};

export const generateAIResponse = async (disputeId, payload = {}) => {
  const response = await api.post(`/disputes/${disputeId}/ai-response`, payload);
  return response.data;
};

export const getAIResponse = async (disputeId) => {
  const response = await api.get(`/disputes/${disputeId}/ai-response`);
  return response.data;
};

export const getDisputeExplanation = async (disputeId) => {
  const response = await api.get(`/disputes/${disputeId}/explanation`);
  return response.data;
};

export const getDisputeReviewStatus = async (disputeId) => {
  const response = await api.get(`/disputes/${disputeId}/review`);
  return response.data;
};

export const submitDisputeReview = async (disputeId, payload) => {
  const response = await api.post(`/disputes/${disputeId}/review`, payload);
  return response.data;
};

export const getDisputeAuditTrail = async (disputeId) => {
  const response = await api.get(`/disputes/${disputeId}/audit`);
  return response.data;
};

export const getAnalyticsOverview = async () => {
  const response = await api.get('/analytics/overview');
  return response.data;
};

export const getAnalyticsTrends = async () => {
  const response = await api.get('/analytics/trends');
  return response.data;
};

export const getAnalyticsModel = async () => {
  const response = await api.get('/analytics/model');
  return response.data;
};

export const getExportEvidencePacketUrl = (disputeId, reviewerName = 'Alex Vance') => {
  return `/api/v1/export/${disputeId}/packet?reviewer=${encodeURIComponent(reviewerName)}`;
};

export const submitBatchReview = async (disputeIds, decision = 'APPROVE', reviewerReference = 'REV-00892', notes = '') => {
  const response = await api.post('/disputes/batch-review', {
    dispute_ids: disputeIds,
    decision,
    reviewer_reference: reviewerReference,
    notes,
  });
  return response.data;
};

export const simulateStripeWebhook = async (payload = {}) => {
  const response = await api.post('/webhooks/stripe', payload);
  return response.data;
};

export default api;





