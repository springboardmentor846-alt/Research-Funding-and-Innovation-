import { useEffect, useState } from "react";
import api from "../api/axios";
import ListModulePage from "../components/ListModulePage";

function ResearchDomains() {
  const [domains, setDomains] = useState([]);
  const [domainName, setDomainName] = useState("");
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(true);

  const fetchDomains = async () => {
    try {
      const response = await api.get(
        "/research-profiles/me/domains"
      );

      setDomains(response.data.domains || []);
    } catch (error) {
      setMessage(
        error.response?.data?.detail ||
          "Failed to load research domains."
      );
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDomains();
  }, []);

  const handleSubmit = async (event) => {
    event.preventDefault();

    try {
      setMessage("");

      await api.post(
        "/research-profiles/me/domains",
        {
          name: domainName,
        }
      );

      setDomainName("");
      setMessage(
        "Research domain added successfully."
      );

      await fetchDomains();
    } catch (error) {
      setMessage(
        error.response?.data?.detail ||
          "Failed to add research domain."
      );
    }
  };

  const handleDelete = async (domainId) => {
    try {
      setMessage("");

      await api.delete(
        `/research-profiles/me/domains/${domainId}`
      );

      setMessage(
        "Research domain deleted successfully."
      );

      await fetchDomains();
    } catch (error) {
      setMessage(
        error.response?.data?.detail ||
          "Failed to delete research domain."
      );
    }
  };

  return (
    <ListModulePage
      eyebrow="RESEARCH CLASSIFICATION"
      title="Research Domains"
      description="Define the broad academic and scientific fields associated with your work."
      inputLabel="Domain Name"
      placeholder="Example: Artificial Intelligence"
      value={domainName}
      onChange={setDomainName}
      onSubmit={handleSubmit}
      items={domains}
      loading={loading}
      message={message}
      emptyMessage="Add your first research domain to begin structuring your profile."
      successHint="Use broad fields such as Artificial Intelligence, Biotechnology, or Renewable Energy."
      onDelete={handleDelete}
    />
  );
}

export default ResearchDomains;