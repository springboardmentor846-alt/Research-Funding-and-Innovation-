import api from "./api";

// Dashboard
export const getDashboard = async () => {
    const res = await api.get("/innovation-score/dashboard");
    return res.data;
};

// Research Impact
export const getResearchImpact = async () => {
    const res = await api.get("/innovation-score/research-impact");
    return res.data;
};

// Technology Readiness
export const getTechnologyReadiness = async () => {
    const res = await api.get("/innovation-score/technology-readiness");
    return res.data;
};

// Commercial Viability
export const getCommercialViability = async () => {
    const res = await api.get("/innovation-score/commercial-viability");
    return res.data;
};

// Funding Attractiveness
export const getFundingAttractiveness = async () => {
    const res = await api.get("/innovation-score/funding-attractiveness");
    return res.data;
};

// ⭐ NEW - Research Intelligence
export const getResearchIntelligence = async () => {
    const res = await api.get("/research-intelligence");
    return res.data;
};