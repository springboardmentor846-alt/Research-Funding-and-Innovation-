import { useEffect, useState } from "react";
import api from "../api/axios";
import ListModulePage from "../components/ListModulePage";

function TechnologyAreas() {
  const [areas, setAreas] = useState([]);
  const [areaName, setAreaName] = useState("");
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(true);

  const fetchAreas = async () => {
    try {
      const response = await api.get(
        "/research-profiles/me/technology-areas"
      );

      setAreas(
        response.data.technology_areas || []
      );
    } catch (error) {
      setMessage(
        error.response?.data?.detail ||
          "Failed to load technology areas."
      );
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAreas();
  }, []);

  const handleSubmit = async (event) => {
    event.preventDefault();

    try {
      setMessage("");

      await api.post(
        "/research-profiles/me/technology-areas",
        {
          name: areaName,
        }
      );

      setAreaName("");
      setMessage(
        "Technology area added successfully."
      );

      await fetchAreas();
    } catch (error) {
      setMessage(
        error.response?.data?.detail ||
          "Failed to add technology area."
      );
    }
  };

  return (
    <ListModulePage
      eyebrow="TECHNOLOGY EXPERTISE"
      title="Technology Areas"
      description="Maintain the technologies, platforms, frameworks, and technical capabilities relevant to your work."
      inputLabel="Technology Area"
      placeholder="Example: FastAPI"
      value={areaName}
      onChange={setAreaName}
      onSubmit={handleSubmit}
      items={areas}
      loading={loading}
      message={message}
      emptyMessage="Add your first technology area to represent your technical expertise."
      successHint="Examples include FastAPI, TensorFlow, Cloud Computing, or Robotics."
    />
  );
}

export default TechnologyAreas;