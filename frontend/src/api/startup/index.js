import api from "../axios";

export async function getStartupProfile() {
  const response = await api.get("/startup/profile");
  return response.data;
}

export async function createStartupProfile(data) {
  const response = await api.post("/startup/profile", data);
  return response.data;
}

export async function updateStartupProfile(data) {
  const response = await api.put("/startup/profile", data);
  return response.data;
}

export async function searchResearchers(query = "") {
  const response = await api.get("/startup/researchers", {
    params: query.trim() ? { query: query.trim() } : {},
  });
  return response.data;
}

export async function searchStartups(query = "") {
  const response = await api.get("/startup/startups", {
    params: query.trim() ? { query: query.trim() } : {},
  });
  return response.data;
}

export async function getCollaborationRequests() {
  const response = await api.get("/startup/collaboration-requests");
  return response.data;
}

export async function sendCollaborationRequest(recipientUserId, message) {
  const response = await api.post("/startup/collaboration-requests", {
    recipient_user_id: recipientUserId,
    message,
  });
  return response.data;
}

export async function updateCollaborationRequest(id, status) {
  const response = await api.patch(`/startup/collaboration-requests/${id}`, {
    status,
  });
  return response.data;
}

export async function getStartupFunding(query = "") {
  const response = await api.get("/startup/funding", {
    params: query.trim() ? { query: query.trim() } : {},
  });
  return response.data;
}

export async function getStartupFundingDetail(fundingId) {
  const response = await api.get(`/startup/funding/${fundingId}`);
  return response.data;
}

export async function predictStartupSuccess(fundingId) {
  const encodedFundingId = encodeURIComponent(fundingId);
  const response = await api.get(`/startup/predict-success/${encodedFundingId}`);
  return response.data;
}
