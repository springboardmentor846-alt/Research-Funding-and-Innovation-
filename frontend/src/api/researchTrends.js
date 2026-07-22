import api from "./axios";

export async function getResearchTrends() {
    const response = await api.get("/trends/publications");
    return response.data;
}