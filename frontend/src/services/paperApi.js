import api from "./api";

export const getPapers = async () => {

    const response = await api.get(
        "/technology-ai/papers"
    );

    return response.data;

};