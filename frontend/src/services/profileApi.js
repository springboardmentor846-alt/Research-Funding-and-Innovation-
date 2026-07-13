import api from "./api";

export const getProfile = async () => {

    const response = await api.get(
        "/research-profile"
    );

    return response.data;

};