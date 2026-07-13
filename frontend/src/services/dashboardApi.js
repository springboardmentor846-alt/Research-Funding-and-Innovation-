import api from "./api";

export const getDashboard = async () => {
    const response = await api.get("/technology-ai/dashboard");
    return response.data;
};