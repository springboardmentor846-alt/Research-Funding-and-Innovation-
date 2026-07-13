import api from "./api";

export const getDashboard = async () => {
    const res = await api.get("/innovation/dashboard");
    return res.data;
};

export const getInnovations = async () => {
    const res = await api.get("/innovation");
    return res.data;
};

export const createInnovation = async (data) => {
    const token = localStorage.getItem("token");

    const res = await api.post(
        "/innovation",
        data,
        {
            headers: {
                Authorization: `Bearer ${token}`
            }
        }
    );

    return res.data;
};