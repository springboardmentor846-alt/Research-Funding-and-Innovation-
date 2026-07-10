import { useEffect, useState } from "react";
import api from "../api/axios";
import ListModulePage from "../components/ListModulePage";

function ResearchKeywords() {
  const [keywords, setKeywords] = useState([]);
  const [keywordName, setKeywordName] = useState("");
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(true);

  const fetchKeywords = async () => {
    try {
      const response = await api.get(
        "/research-profiles/me/keywords"
      );

      setKeywords(response.data.keywords || []);
    } catch (error) {
      setMessage(
        error.response?.data?.detail ||
          "Failed to load research keywords."
      );
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchKeywords();
  }, []);

  const handleSubmit = async (event) => {
    event.preventDefault();

    try {
      setMessage("");

      await api.post(
        "/research-profiles/me/keywords",
        {
          name: keywordName,
        }
      );

      setKeywordName("");
      setMessage(
        "Research keyword added successfully."
      );

      await fetchKeywords();
    } catch (error) {
      setMessage(
        error.response?.data?.detail ||
          "Failed to add research keyword."
      );
    }
  };

  const handleDelete = async (keywordId) => {
    try {
      setMessage("");

      await api.delete(
        `/research-profiles/me/keywords/${keywordId}`
      );

      setMessage(
        "Research keyword deleted successfully."
      );

      await fetchKeywords();
    } catch (error) {
      setMessage(
        error.response?.data?.detail ||
          "Failed to delete research keyword."
      );
    }
  };

  return (
    <ListModulePage
      eyebrow="RESEARCH DISCOVERY"
      title="Research Keywords"
      description="Add focused terms that describe the specific topics, methods, and problems in your research."
      inputLabel="Keyword"
      placeholder="Example: Deep Learning"
      value={keywordName}
      onChange={setKeywordName}
      onSubmit={handleSubmit}
      items={keywords}
      loading={loading}
      message={message}
      emptyMessage="Add your first keyword to improve research classification and future matching."
      successHint="Use focused terms such as Deep Learning, Computer Vision, or Drug Discovery."
      onDelete={handleDelete}
    />
  );
}

export default ResearchKeywords;