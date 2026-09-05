import { useEffect, useState, useCallback } from "react";
import axios from "axios";
import PublicationSearch from "./PublicationSearch";
import CrossrefSearch from "./CrossrefSearch";

function ResearchLibrary({ token }) {
  const [library, setLibrary] = useState([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  const [searchSource, setSearchSource] = useState("openalex");

  const loadLibrary = useCallback(async () => {
    setLoading(true);
    try {
      const response = await axios.get(
        "http://127.0.0.1:8000/api/v1/profile/library",
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setLibrary(response.data);
      setError("");
    } catch (err) {
      setError("Could not load your research library.");
    }
    setLoading(false);
  }, [token]);

  useEffect(() => {
    loadLibrary();
  }, [loadLibrary]);

  return (
    <>
      <div className="dash-card">
        <h3>Research Library</h3>
        <p className="dash-card-subtitle">
          Papers you've found and saved for reference — separate from your own
          publications. Search below to find and save papers.
        </p>

        <div style={{ display: "flex", gap: "10px", marginBottom: "14px" }}>
          <button
            type="button"
            onClick={() => setSearchSource("openalex")}
            style={{
              padding: "6px 14px",
              borderRadius: "6px",
              border: "1px solid #1C8C7A",
              background: searchSource === "openalex" ? "#1C8C7A" : "transparent",
              color: searchSource === "openalex" ? "#fff" : "#1C8C7A",
              fontWeight: 600,
              fontSize: "13px",
              cursor: "pointer",
            }}
          >
            OpenAlex
          </button>
          <button
            type="button"
            onClick={() => setSearchSource("crossref")}
            style={{
              padding: "6px 14px",
              borderRadius: "6px",
              border: "1px solid #1C8C7A",
              background: searchSource === "crossref" ? "#1C8C7A" : "transparent",
              color: searchSource === "crossref" ? "#fff" : "#1C8C7A",
              fontWeight: 600,
              fontSize: "13px",
              cursor: "pointer",
            }}
          >
            Crossref
          </button>
        </div>

        {searchSource === "openalex" ? (
          <PublicationSearch token={token} onAdded={loadLibrary} />
        ) : (
          <CrossrefSearch token={token} onAdded={loadLibrary} />
        )}
      </div>

      <div className="dash-card">
        <h3>Saved Papers</h3>
        <p className="dash-card-subtitle">{library.length} paper(s) saved</p>

        {loading && <p className="dash-empty">Loading...</p>}
        {error && <p className="dash-error">{error}</p>}

        {!loading && !error && library.length === 0 && (
          <p className="dash-empty">
            Your research library is empty. Search above to save papers for reference.
          </p>
        )}

        {library.map((pub) => (
          <div key={pub.id} className="dash-card" style={{ marginTop: "10px" }}>
            <p style={{ fontWeight: 600 }}>{pub.title}</p>
            <p className="dash-card-subtitle">
              {pub.authors || "Unknown author"} · {pub.year || "n/a"} · {pub.source || "Unknown source"}
            </p>
            {pub.link && (
              <a href={pub.link} target="_blank" rel="noreferrer">
                View source
              </a>
            )}
          </div>
        ))}
      </div>
    </>
  );
}

export default ResearchLibrary;