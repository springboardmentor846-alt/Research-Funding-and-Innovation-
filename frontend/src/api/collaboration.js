import api from "./axios";

export async function getCollaborationRequests() {
  const response = await api.get("/collaboration/requests");
  return response.data;
}

export async function sendCollaborationRequest(recipientUserId, message = "") {
  const response = await api.post("/collaboration/requests", {
    recipient_user_id: recipientUserId,
    message,
  });
  return response.data;
}

export async function updateCollaborationRequest(id, status) {
  const response = await api.patch(`/collaboration/requests/${id}`, { status });
  return response.data;
}
