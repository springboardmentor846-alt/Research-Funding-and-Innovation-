import api from "./api";

export const getTechnologyDashboard = async () => {

    const response = await api.get(
        "/technology-ai/dashboard"
    );

    return response.data;

};

export const getForecast = async () => {

    const response = await api.get(
        "/technology-ai/forecast/trends"
    );

    return response.data;

};

export const getOrganizationRanking = async () => {

    const response = await api.get(
        "/technology-ai/organization/ranking"
    );

    return response.data;

};

export const getResearchProductivity = async () => {

    const response = await api.get(
        "/technology-ai/productivity"
    );

    return response.data;

};

export const getCollaborationNetwork = async () => {

    const response = await api.get(
        "/technology-ai/analytics/collaboration-network"
    );

    return response.data;

};