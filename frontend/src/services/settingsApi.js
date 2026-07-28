import api from "./api";

export const getProfile = async () => {
    const response = await api.get("/profile");
    return response.data;
};

export const updateProfile = async (data) => {
    const response = await api.put("/profile", data);
    return response.data;
};

export const changePassword = async (data) => {
    const response = await api.put("/profile/password", data);
    return response.data;
};

export const getDashboardStats = async () => {
    const response = await api.get("/dashboard");
    return response.data;
};