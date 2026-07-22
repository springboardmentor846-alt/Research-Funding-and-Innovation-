import api from "./axios";


export async function getPatentLandscape(query) {

  const response = await api.get(

    "/patent-landscape",

    {
      params: {
        query: query,
      },
    }

  );


  return response.data;

}