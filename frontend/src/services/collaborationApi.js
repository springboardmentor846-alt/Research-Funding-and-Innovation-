import api from "./api";

export const getCollaborations = async (profileId) => {

    const response = await api.get(
        `/technology-ai/collaboration/${profileId}`
    );

    return response.data;

};