import { useEffect, useState } from "react";
import axios from "axios";

const API_BASE = "http://127.0.0.1:8000/api/v1/profile";

function ResearchProfileForm({ token, onProfileSaved }) {
  const authHeaders = { headers: { Authorization: `Bearer ${token}` } };

  // ---- Profile fields ----
  const [profileExists, setProfileExists] = useState(false);
  const [researchDomains, setResearchDomains] = useState("");
  const [keywords, setKeywords] = useState("");
  const [technologyAreas, setTechnologyAreas] = useState("");
  const [organizationName, setOrganizationName] = useState("");
  const [orcidId, setOrcidId] = useState("");
  const [profileMessage, setProfileMessage] = useState("");
  const [savingProfile, setSavingProfile] = useState(false);

  // ---- Publication fields ----
  const [pubTitle, setPubTitle] = useState("");
  const [pubAuthors, setPubAuthors] = useState("");
  const [pubYear, setPubYear] = useState("");
  const [pubSource, setPubSource] = useState("");
  const [publications, setPublications] = useState([]);
  const [pubMessage, setPubMessage] = useState("");
  const [uploadingPubId, setUploadingPubId] = useState(null);

  // ---- Patent fields ----
  const [patentTitle, setPatentTitle] = useState("");
  const [patentAssignee, setPatentAssignee] = useState("");
  const [patentFilingDate, setPatentFilingDate] = useState("");
  const [patentNumber, setPatentNumber] = useState("");
  const [patents, setPatents] = useState([]);
  const [patentMessage, setPatentMessage] = useState("");

  // ---- OpenAlex import ----
  const [authorSearchName, setAuthorSearchName] = useState("");
  const [authorResults, setAuthorResults] = useState([]);
  const [openAlexMessage, setOpenAlexMessage] = useState("");
  const [openAlexLoading, setOpenAlexLoading] = useState(false);
  const [importingAuthorId, setImportingAuthorId] = useState("");

  // ---- ORCID import ----
  const [orcidSearchName, setOrcidSearchName] = useState("");
  const [orcidResults, setOrcidResults] = useState([]);
  const [orcidMessage, setOrcidMessage] = useState("");
  const [orcidLoading, setOrcidLoading] = useState(false);
  const [importingOrcidId, setImportingOrcidId] = useState("");

  const loadExistingProfile = async () => {
    try {
      const res = await axios.get(`${API_BASE}/`, authHeaders);
      setProfileExists(true);
      setResearchDomains(res.data.research_domains || "");
      setKeywords(res.data.keywords || "");
      setTechnologyAreas(res.data.technology_areas || "");
      setOrganizationName(res.data.organization_name || "");
      setOrcidId(res.data.orcid_id || "");
    } catch (err) {
      setProfileExists(false);
    }
  };

  const loadPublications = async () => {
    try {
      const res = await axios.get(`${API_BASE}/publications`, authHeaders);
      setPublications(res.data);
    } catch (err) {
      setPublications([]);
    }
  };

  const loadPatents = async () => {
    try {
      const res = await axios.get(`${API_BASE}/patents`, authHeaders);
      setPatents(res.data);
    } catch (err) {
      setPatents([]);
    }
  };

  const handleSearchAuthor = async (e) => {
    e.preventDefault();
    setOpenAlexMessage("");
    setAuthorResults([]);
    if (!authorSearchName.trim()) {
      setOpenAlexMessage("Enter an author name to search.");
      return;
    }
    setOpenAlexLoading(true);
    try {
      const res = await axios.get(`${API_BASE}/openalex/search-author`, {
        ...authHeaders,
        params: { name: authorSearchName },
      });
      setAuthorResults(res.data.authors || []);
      if (!res.data.authors || res.data.authors.length === 0) {
        setOpenAlexMessage("No authors found on OpenAlex for that name.");
      }
    } catch (err) {
      setOpenAlexMessage(
        err.response?.data?.detail || "Could not reach OpenAlex. Check your internet connection."
      );
    } finally {
      setOpenAlexLoading(false);
    }
  };

  const handleImportPublications = async (authorId) => {
    setOpenAlexMessage("");
    setImportingAuthorId(authorId);
    try {
      const res = await axios.post(
        `${API_BASE}/openalex/import-publications`,
        null,
        { ...authHeaders, params: { author_id: authorId } }
      );
      setOpenAlexMessage(
        `Imported ${res.data.imported} of ${res.data.total} publications from OpenAlex.`
      );
      loadPublications();
      if (onProfileSaved) onProfileSaved();
    } catch (err) {
      setOpenAlexMessage(
        err.response?.data?.detail || "Could not import publications."
      );
    } finally {
      setImportingAuthorId("");
    }
  };

  const handleSearchOrcid = async (e) => {
    e.preventDefault();
    setOrcidMessage("");
    setOrcidResults([]);
    if (!orcidSearchName.trim()) {
      setOrcidMessage("Enter a name to search.");
      return;
    }
    setOrcidLoading(true);
    try {
      const res = await axios.get(`${API_BASE}/orcid/search`, {
        ...authHeaders,
        params: { name: orcidSearchName },
      });
      setOrcidResults(res.data || []);
      if (!res.data || res.data.length === 0) {
        setOrcidMessage("No researchers found on ORCID for that name.");
      }
    } catch (err) {
      setOrcidMessage(
        err.response?.data?.detail || "Could not reach ORCID. Check your internet connection."
      );
    } finally {
      setOrcidLoading(false);
    }
  };

  const handleImportFromOrcid = async (candidateOrcidId) => {
    setOrcidMessage("");
    setImportingOrcidId(candidateOrcidId);
    try {
      const res = await axios.post(
        `${API_BASE}/orcid/import`,
        null,
        { ...authHeaders, params: { orcid_id: candidateOrcidId } }
      );
      setOrcidMessage(
        `Imported ${res.data.imported} of ${res.data.total} works from ORCID.`
      );
      setOrcidId(candidateOrcidId);
      if (onProfileSaved) onProfileSaved();
    } catch (err) {
      setOrcidMessage(
        err.response?.data?.detail || "Could not import from ORCID."
      );
    } finally {
      setImportingOrcidId("");
    }
  };

  useEffect(() => {
    loadExistingProfile();
    loadPublications();
    loadPatents();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token]);

  const handleSaveProfile = async (e) => {
    e.preventDefault();
    setSavingProfile(true);
    setProfileMessage("");
    try {
      await axios.post(
        `${API_BASE}/`,
        {
          research_domains: researchDomains,
          keywords: keywords,
          technology_areas: technologyAreas,
          organization_name: organizationName,
          orcid_id: orcidId,
        },
        authHeaders
      );
      setProfileExists(true);
      setProfileMessage("Profile saved successfully.");
      if (onProfileSaved) onProfileSaved();
    } catch (err) {
      setProfileMessage(
        err.response?.data?.detail || "Could not save profile. Please try again."
      );
    } finally {
      setSavingProfile(false);
    }
  };

  const handleAddPublication = async (e) => {
    e.preventDefault();
    setPubMessage("");
    if (!pubTitle.trim()) {
      setPubMessage("Title is required.");
      return;
    }
    try {
      await axios.post(
        `${API_BASE}/publications`,
        {
          title: pubTitle,
          authors: pubAuthors,
          year: pubYear,
          source: pubSource,
        },
        authHeaders
      );
      setPubTitle("");
      setPubAuthors("");
      setPubYear("");
      setPubSource("");
      setPubMessage("Publication added.");
      loadPublications();
      if (onProfileSaved) onProfileSaved();
    } catch (err) {
      setPubMessage(
        err.response?.data?.detail || "Could not add publication."
      );
    }
  };

  const handleUploadPdf = async (publicationId, file) => {
    if (!file) return;
    setUploadingPubId(publicationId);
    setPubMessage("");

    const formData = new FormData();
    formData.append("file", file);

    try {
      await axios.post(
        `${API_BASE}/publications/${publicationId}/upload-pdf`,
        formData,
        {
          headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "multipart/form-data",
          },
        }
      );
      setPubMessage("PDF uploaded.");
      loadPublications();
    } catch (err) {
      setPubMessage(err.response?.data?.detail || "Could not upload PDF.");
    }
    setUploadingPubId(null);
  };

  const handleAddPatent = async (e) => {
    e.preventDefault();
    setPatentMessage("");
    if (!patentTitle.trim()) {
      setPatentMessage("Title is required.");
      return;
    }
    try {
      await axios.post(
        `${API_BASE}/patents`,
        {
          title: patentTitle,
          assignee: patentAssignee,
          filing_date: patentFilingDate,
          patent_number: patentNumber,
        },
        authHeaders
      );
      setPatentTitle("");
      setPatentAssignee("");
      setPatentFilingDate("");
      setPatentNumber("");
      setPatentMessage("Patent added.");
      loadPatents();
      if (onProfileSaved) onProfileSaved();
    } catch (err) {
      setPatentMessage(
        err.response?.data?.detail || "Could not add patent."
      );
    }
  };

  const inputStyle = {
    width: "100%",
    padding: "8px 10px",
    marginTop: "4px",
    marginBottom: "10px",
    border: "1px solid #d7dce3",
    borderRadius: "6px",
    fontSize: "13px",
    boxSizing: "border-box",
  };
  const labelStyle = { fontSize: "12.5px", fontWeight: 600, color: "#3b4252" };
  const sectionStyle = { marginBottom: "18px" };
  const btnStyle = {
    background: "#1C8C7A",
    color: "#fff",
    border: "none",
    padding: "9px 18px",
    borderRadius: "6px",
    fontSize: "13.5px",
    fontWeight: 600,
    cursor: "pointer",
  };
    const listItemStyle = {
    padding: "12px 14px",
    background: "#fff",
    border: "1px solid #E1E5EC",
    borderLeft: "3px solid #1F9E8E",
    borderRadius: "8px",
    marginBottom: "10px",
    fontSize: "13px",
    lineHeight: "1.5",
    transition: "box-shadow 0.15s ease",
  };
  return (
    <div className="dash-card">
      <h3>{profileExists ? "Your Research Profile" : "Create Your Research Profile"}</h3>
      <p className="dash-card-subtitle">
        Add your research domains, publications, and patents so funding
        recommendations and your innovation score can be generated.
      </p>

      {/* PROFILE FORM */}
      <form onSubmit={handleSaveProfile} style={sectionStyle}>
        <label style={labelStyle}>Research Domains (comma separated)</label>
        <input
          style={inputStyle}
          type="text"
          placeholder="e.g. Machine Learning, Blockchain, Cryptography"
          value={researchDomains}
          onChange={(e) => setResearchDomains(e.target.value)}
        />

        <label style={labelStyle}>Keywords (comma separated)</label>
        <input
          style={inputStyle}
          type="text"
          placeholder="e.g. deep learning, security, quantum computing"
          value={keywords}
          onChange={(e) => setKeywords(e.target.value)}
        />

        <label style={labelStyle}>Technology Areas (comma separated)</label>
        <input
          style={inputStyle}
          type="text"
          placeholder="e.g. AI, IoT, Cloud Computing"
          value={technologyAreas}
          onChange={(e) => setTechnologyAreas(e.target.value)}
        />

        <label style={labelStyle}>Organization Name</label>
        <input
          style={inputStyle}
          type="text"
          placeholder="e.g. IIT Delhi"
          value={organizationName}
          onChange={(e) => setOrganizationName(e.target.value)}
        />

        <label style={labelStyle}>ORCID iD (optional)</label>
        <input
          style={inputStyle}
          type="text"
          placeholder="e.g. 0000-0002-1825-0097"
          value={orcidId}
          onChange={(e) => setOrcidId(e.target.value)}
        />

        <button style={btnStyle} type="submit" disabled={savingProfile}>
          {savingProfile ? "Saving..." : profileExists ? "Update Profile" : "Create Profile"}
        </button>
        {profileMessage && (
          <p style={{ fontSize: "12.5px", marginTop: "8px", color: "#1C8C7A" }}>
            {profileMessage}
          </p>
        )}
      </form>

      {/* PUBLICATION FORM — only once profile exists */}
      {profileExists && (
        <>
          <hr style={{ margin: "18px 0", border: "none", borderTop: "1px solid #e5e9ef" }} />
          <h4 style={{ marginBottom: "6px" }}>Add Publication</h4>
          <form onSubmit={handleAddPublication} style={sectionStyle}>
            <label style={labelStyle}>Title</label>
            <input
              style={inputStyle}
              type="text"
              placeholder="Publication title"
              value={pubTitle}
              onChange={(e) => setPubTitle(e.target.value)}
            />
            <label style={labelStyle}>Authors</label>
            <input
              style={inputStyle}
              type="text"
              placeholder="e.g. R. Kumar, A. Sharma"
              value={pubAuthors}
              onChange={(e) => setPubAuthors(e.target.value)}
            />
            <label style={labelStyle}>Year</label>
            <input
              style={inputStyle}
              type="text"
              placeholder="e.g. 2026"
              value={pubYear}
              onChange={(e) => setPubYear(e.target.value)}
            />
            <label style={labelStyle}>Source</label>
            <input
              style={inputStyle}
              type="text"
              placeholder="e.g. IEEE, arXiv"
              value={pubSource}
              onChange={(e) => setPubSource(e.target.value)}
            />
            <button style={btnStyle} type="submit">Add Publication</button>
            {pubMessage && (
              <p style={{ fontSize: "12.5px", marginTop: "8px", color: "#1C8C7A" }}>
                {pubMessage}
              </p>
            )}
          </form>

          {publications.length > 0 && (
            <div style={{ marginBottom: "18px", maxHeight: "420px", overflowY: "auto", paddingRight: "6px" }}>
              {publications.map((p) => (
                <div key={p.id} style={listItemStyle}>
                  <strong>{p.title}</strong>
                  {p.year ? ` (${p.year})` : ""} {p.authors ? `— ${p.authors}` : ""}
                  <div style={{ marginTop: "6px", display: "flex", alignItems: "center", gap: "10px" }}>
                    {p.pdf_path ? (
                      <a
                        href={`http://127.0.0.1:8000/${p.pdf_path}`}
                        target="_blank"
                        rel="noreferrer"
                        style={{ fontSize: "12.5px", color: "#1C8C7A", fontWeight: 600 }}
                      >
                        View PDF
                      </a>
                    ) : (
                      <label style={{ fontSize: "12.5px", cursor: "pointer", color: "#2E5EAA", fontWeight: 600 }}>
                        {uploadingPubId === p.id ? "Uploading..." : "Upload PDF"}
                        <input
                          type="file"
                          accept="application/pdf"
                          style={{ display: "none" }}
                          disabled={uploadingPubId === p.id}
                          onChange={(e) => handleUploadPdf(p.id, e.target.files[0])}
                        />
                      </label>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}

          <hr style={{ margin: "18px 0", border: "none", borderTop: "1px solid #e5e9ef" }} />
          <h4 style={{ marginBottom: "6px" }}>Import Publications from OpenAlex</h4>
          <p className="dash-card-subtitle" style={{ marginBottom: "10px" }}>
            Search your name on OpenAlex (a free, open research database) and import your real publications automatically.
          </p>
          <form onSubmit={handleSearchAuthor} style={{ display: "flex", gap: "8px", marginBottom: "12px" }}>
            <input
              style={{ ...inputStyle, marginBottom: 0, flex: 1 }}
              type="text"
              placeholder="Search author name, e.g. Andrew Ng"
              value={authorSearchName}
              onChange={(e) => setAuthorSearchName(e.target.value)}
            />
            <button style={btnStyle} type="submit" disabled={openAlexLoading}>
              {openAlexLoading ? "Searching..." : "Search"}
            </button>
          </form>

          {openAlexMessage && (
            <p style={{ fontSize: "12.5px", marginBottom: "10px", color: "#3b4252" }}>
              {openAlexMessage}
            </p>
          )}

          {authorResults.length > 0 && (
            <div style={{ marginBottom: "18px" }}>
              {authorResults.map((author) => (
                <div
                  key={author.id}
                  style={{
                    ...listItemStyle,
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "center",
                  }}
                >
                  <span>
                    <strong>{author.name}</strong>
                    {" — "}
                    {author.works_count} works, {author.cited_by_count} citations
                  </span>
                  <button
                    style={{ ...btnStyle, padding: "6px 12px", fontSize: "12px" }}
                    onClick={() => handleImportPublications(author.id)}
                    disabled={importingAuthorId === author.id}
                  >
                    {importingAuthorId === author.id ? "Importing..." : "Import Publications"}
                  </button>
                </div>
              ))}
            </div>
          )}

          <hr style={{ margin: "18px 0", border: "none", borderTop: "1px solid #e5e9ef" }} />
          <h4 style={{ marginBottom: "6px" }}>Import Works from ORCID</h4>
          <p className="dash-card-subtitle" style={{ marginBottom: "10px" }}>
            Search your name on ORCID (the researcher identifier registry) and import the works listed on your public ORCID record.
          </p>
          <form onSubmit={handleSearchOrcid} style={{ display: "flex", gap: "8px", marginBottom: "12px" }}>
            <input
              style={{ ...inputStyle, marginBottom: 0, flex: 1 }}
              type="text"
              placeholder="Search researcher name, e.g. Jane Smith"
              value={orcidSearchName}
              onChange={(e) => setOrcidSearchName(e.target.value)}
            />
            <button style={btnStyle} type="submit" disabled={orcidLoading}>
              {orcidLoading ? "Searching..." : "Search"}
            </button>
          </form>

          {orcidMessage && (
            <p style={{ fontSize: "12.5px", marginBottom: "10px", color: "#3b4252" }}>
              {orcidMessage}
            </p>
          )}

          {orcidResults.length > 0 && (
            <div style={{ marginBottom: "18px" }}>
              {orcidResults.map((candidate) => (
                <div
                  key={candidate.orcid_id}
                  style={{
                    ...listItemStyle,
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "center",
                  }}
                >
                  <span>
                    <strong>{candidate.name}</strong>
                    {" — "}
                    {candidate.orcid_id}
                  </span>
                  <button
                    style={{ ...btnStyle, padding: "6px 12px", fontSize: "12px" }}
                    onClick={() => handleImportFromOrcid(candidate.orcid_id)}
                    disabled={importingOrcidId === candidate.orcid_id}
                  >
                    {importingOrcidId === candidate.orcid_id ? "Importing..." : "Import Works"}
                  </button>
                </div>
              ))}
            </div>
          )}

          <hr style={{ margin: "18px 0", border: "none", borderTop: "1px solid #e5e9ef" }} />
          <h4 style={{ marginBottom: "6px" }}>Add Patent</h4>
          <form onSubmit={handleAddPatent} style={sectionStyle}>
            <label style={labelStyle}>Title</label>
            <input
              style={inputStyle}
              type="text"
              placeholder="Patent title"
              value={patentTitle}
              onChange={(e) => setPatentTitle(e.target.value)}
            />
            <label style={labelStyle}>Assignee</label>
            <input
              style={inputStyle}
              type="text"
              placeholder="e.g. Google LLC"
              value={patentAssignee}
              onChange={(e) => setPatentAssignee(e.target.value)}
            />
            <label style={labelStyle}>Filing Date</label>
            <input
              style={inputStyle}
              type="text"
              placeholder="e.g. 2025-06-01"
              value={patentFilingDate}
              onChange={(e) => setPatentFilingDate(e.target.value)}
            />
            <label style={labelStyle}>Patent Number</label>
            <input
              style={inputStyle}
              type="text"
              placeholder="e.g. US1234567"
              value={patentNumber}
              onChange={(e) => setPatentNumber(e.target.value)}
            />
            <button style={btnStyle} type="submit">Add Patent</button>
            {patentMessage && (
              <p style={{ fontSize: "12.5px", marginTop: "8px", color: "#1C8C7A" }}>
                {patentMessage}
              </p>
            )}
          </form>

          {patents.length > 0 && (
            <div>
              {patents.map((p) => (
                <div key={p.id} style={listItemStyle}>
                  <strong>{p.title}</strong>
                  {p.assignee ? ` — ${p.assignee}` : ""} {p.filing_date ? `(${p.filing_date})` : ""}
                </div>
              ))}
            </div>
          )}
        </>
      )}
    </div>
  );
}

export default ResearchProfileForm;