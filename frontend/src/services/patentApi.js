import api from "./api";

// Analytics
export const getPatentAnalytics = async () => {
    const token = localStorage.getItem("token");

    const res = await api.get("/patents/analytics", {
        headers: {
            Authorization: `Bearer ${token}`,
        },
    });

    return res.data;
};

// All patents
export const getPatents = async () => {
    const token = localStorage.getItem("token");

    const res = await api.get("/patents", {
        headers: {
            Authorization: `Bearer ${token}`,
        },
    });

    return res.data;
};

// Patent trends
export const getPatentTrends = async () => {
    const token = localStorage.getItem("token");

    const res = await api.get("/patents/trends", {
        headers: {
            Authorization: `Bearer ${token}`,
        },
    });

    return res.data;
};

// Patent clusters
export const getPatentClusters = async () => {
    const token = localStorage.getItem("token");

    const res = await api.get("/patents/clusters", {
        headers: {
            Authorization: `Bearer ${token}`,
        },
    });

    return res.data;
};

// Innovation map
export const getInnovationMap = async () => {
    const token = localStorage.getItem("token");

    const res = await api.get("/patents/innovation-map", {
        headers: {
            Authorization: `Bearer ${token}`,
        },
    });

    return res.data;
};

// Search patents
export const searchPatent = async (domain) => {
    const token = localStorage.getItem("token");

    const res = await api.get(`/patents/search/${domain}`, {
        headers: {
            Authorization: `Bearer ${token}`,
        },
    });

    return res.data;
};

// Competitor patents
export const competitorPatent = async (assignee) => {
    const token = localStorage.getItem("token");

    const res = await api.get(`/patents/competitor/${assignee}`, {
        headers: {
            Authorization: `Bearer ${token}`,
        },
    });

    return res.data;
};

// Add patent
export const addPatent = async (data) => {
    const token = localStorage.getItem("token");

    const res = await api.post("/patents", data, {
        headers: {
            Authorization: `Bearer ${token}`,
        },
    });

    return res.data;
};