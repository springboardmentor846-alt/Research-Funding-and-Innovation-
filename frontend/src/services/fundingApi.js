import api from "./api";

export const getRecommendations = async () => {

    const response = await api.get(
        "/funding/recommendations"
    );

    return response.data;

};

export const searchFunding = async (domain) => {

    const response = await api.get(
        `/funding/search/${domain}`
    );

    return response.data;

};