import api from "../axios";

export const getStartupProfile = async () => {
  const response = await api.get("/startup/profile");
  return response.data;
};

export const createStartupProfile = async (data) => {
  const response = await api.post("/startup/profile", data);
  return response.data;
};

export const updateStartupProfile = async (data) => {
  const response = await api.put("/startup/profile", data);
  return response.data;
};