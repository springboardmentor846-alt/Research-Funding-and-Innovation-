import api from "./api";

export const getCommercializations = async () => {
    const res = await api.get("/commercialization");
    return res.data;
};

export const getDashboard = async () => {
    const res = await api.get("/commercialization/dashboard");
    return res.data;
};

export const getProductization = async () => {
    const res = await api.get("/commercialization/productization");
    return res.data;
};

export const getLicensing = async () => {
    const res = await api.get("/commercialization/licensing");
    return res.data;
};

export const getStartup = async () => {
    const res = await api.get("/commercialization/startup");
    return res.data;
};

export const getPartnership = async () => {
    const res = await api.get("/commercialization/partnership");
    return res.data;
};

export const addCommercialization = async (data) => {
    const res = await api.post("/commercialization", data);
    return res.data;
};