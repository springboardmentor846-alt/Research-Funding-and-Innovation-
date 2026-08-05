import api from "../axios";

export async function getResearchTrends(query) {

    const response = await api.get(
        "/research-trends/",
        {
            params: {
                query
            }
        }
    );

    return response.data;
}