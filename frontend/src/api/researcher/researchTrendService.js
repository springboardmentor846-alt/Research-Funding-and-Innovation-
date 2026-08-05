import axiosInstance from "../axios";

export const getResearchTrends = async (query) => {

    const response = await axiosInstance.get(
        "/research-trends/",
        {
            params: {
                query
            }
        }
    );

    return response.data;
};