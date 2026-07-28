import api from "./api";

export const getDashboard = async () => {
    const res = await api.get("/innovation-score/dashboard");
    return res.data;
};

export const getResearchImpact = async () => {
    const res = await api.get("/innovation-score/research-impact");
    return res.data;
};

export const getTechnologyReadiness = async () => {
    const res = await api.get("/innovation-score/technology-readiness");
    return res.data;
};

export const getCommercialViability = async () => {
    const res = await api.get("/innovation-score/commercial-viability");
    return res.data;
};

export const getFundingAttractiveness = async () => {
    const res = await api.get("/innovation-score/funding-attractiveness");
    return res.data;
};