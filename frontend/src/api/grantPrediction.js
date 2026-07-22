import api from "./axios";

export async function getGrantPrediction(fundingId) {

    const response = await api.get(
        `/grant-prediction/${fundingId}`
    );

    return response.data;

}