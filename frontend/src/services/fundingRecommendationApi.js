import api from "./api";

export const getFundingRecommendations = async () => {
    const res = await api.get("/funding/recommendations");
    return res.data;
};

export const getGrantMatching = async () => {
    const res = await api.get("/funding/grant-matching");
    return res.data;
};

export const getEligibility = async () => {
    const res = await api.get("/funding/eligibility");
    return res.data;
};

export const getFundingDashboard = async () => {
    const res = await api.get("/funding/dashboard");
    return res.data;
};