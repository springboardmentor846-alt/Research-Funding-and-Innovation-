import axios from "axios";

const API = "http://127.0.0.1:8000";

export async function getPublicationAnalysis() {

    const token = localStorage.getItem("token");

    const response = await axios.get(

        `${API}/publication-analysis`,

        {

            headers: {

                Authorization: `Bearer ${token}`

            }

        }

    );

    return response.data;

}