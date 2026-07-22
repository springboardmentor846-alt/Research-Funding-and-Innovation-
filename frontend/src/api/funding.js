import api from "./axios";


// ============================================================
// GET ALL FUNDING
// ============================================================

export async function getFundingOpportunities() {

  const response = await api.get(
    "/funding"
  );

  return response.data;
}


// ============================================================
// AI PERSONALIZED RECOMMENDATIONS
// ============================================================

export async function getFundingRecommendations() {

  const response = await api.get(
    "/funding/recommendations/ai"
  );

  return response.data;
}


// ============================================================
// SEARCH FUNDING
// ============================================================

export async function searchFunding(
  params = {}
) {

  const response = await api.get(
    "/funding/search",
    {
      params: params,
    }
  );

  return response.data;
}


// ============================================================
// FUNDING ALERTS
// ============================================================

export async function getFundingAlerts(
  days = 30
) {

  const response = await api.get(
    "/funding/alerts",
    {
      params: {
        days: days,
      },
    }
  );

  return response.data;
}


// ============================================================
// COLLECT FUNDING
// ADMIN FUNCTION - NOT NEEDED ON RESEARCHER PAGE
// ============================================================

export async function collectFunding() {

  const response = await api.post(
    "/funding/collect"
  );

  return response.data;
}