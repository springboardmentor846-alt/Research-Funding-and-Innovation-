import { useEffect, useState } from "react";
import api from "../api/api";
import { toast } from "react-toastify";

const blank = {
  title: "",
  funding_agency: "",
  research_domain: "",
  technology_area: "",
  keywords: "",
  amount: "",
  deadline: "",
  eligibility: "",
  description: "",
  link: "",
};

export default function Funding() {
  const [items, setItems] = useState([]);
  const [form, setForm] = useState(blank);
  const [editing, setEditing] = useState(null);
  const [show, setShow] = useState(false);

  const load = async () => {
    try {
      const res = await api.get("/funding/");
      setItems(res.data);
    } catch (err) {
      toast.error(
        err.response?.data?.detail ||
          "Could not load funding opportunities."
      );
    }
  };

  useEffect(() => {
    load();
  }, []);

  const update = (key, value) => {
    setForm((prev) => ({
      ...prev,
      [key]: value,
    }));
  };

  const submit = async (e) => {
    e.preventDefault();

    try {
      if (editing) {
        await api.put(`/funding/${editing}`, form);
      } else {
        await api.post("/funding/", form);
      }

      toast.success(
        editing
          ? "Funding opportunity updated successfully."
          : "Funding opportunity added successfully."
      );

      setForm(blank);
      setEditing(null);
      setShow(false);

      load();
    } catch (err) {
      toast.error(
        err.response?.data?.detail ||
          "Could not save funding opportunity."
      );
    }
  };

  const remove = async (id) => {
    if (!window.confirm("Delete this funding opportunity?")) return;

    try {
      await api.delete(`/funding/${id}`);
      toast.success("Funding opportunity deleted.");
      load();
    } catch (err) {
      toast.error(
        err.response?.data?.detail ||
          "Could not delete funding opportunity."
      );
    }
  };

  const editOpportunity = (item) => {
    setEditing(item.id);

    setForm({
      title: item.title || "",
      funding_agency: item.funding_agency || "",
      research_domain: item.research_domain || "",
      technology_area: item.technology_area || "",
      keywords: item.keywords || "",
      amount: item.amount || "",
      deadline: item.deadline || "",
      eligibility: item.eligibility || "",
      description: item.description || "",
      link: item.link || "",
    });

    setShow(true);
  };

  return (
    <section>
      <div className="page-heading heading-row">
        <div>
          <p className="eyebrow">FUNDING MARKETPLACE</p>

          <h1>Funding Opportunities</h1>

          <p>
            Manage funding opportunities used by the
            recommendation and grant matching engine.
          </p>
        </div>

        <button
          className="btn-primary"
          onClick={() => {
            if (show) {
              setShow(false);
              setEditing(null);
              setForm(blank);
            } else {
              setShow(true);
            }
          }}
        >
          {show ? "Close Form" : "Add Opportunity"}
        </button>
      </div>

      {show && (
        <form
          className="panel compact-form funding-form"
          onSubmit={submit}
        >
          <label>
            Title
            <input
              required
              value={form.title}
              onChange={(e) =>
                update("title", e.target.value)
              }
            />
          </label>

          <label>
            Funding Agency
            <input
              required
              value={form.funding_agency}
              onChange={(e) =>
                update("funding_agency", e.target.value)
              }
            />
          </label>

          <label>
            Research Domain
            <input
              required
              value={form.research_domain}
              onChange={(e) =>
                update("research_domain", e.target.value)
              }
            />
          </label>

          <label>
            Technology Area
            <input
              required
              value={form.technology_area}
              onChange={(e) =>
                update("technology_area", e.target.value)
              }
            />
          </label>

          <label>
            Keywords
            <input
              required
              value={form.keywords}
              onChange={(e) =>
                update("keywords", e.target.value)
              }
            />
          </label>

          <label>
            Amount
            <input
              required
              value={form.amount}
              onChange={(e) =>
                update("amount", e.target.value)
              }
            />
          </label>

          <label>
            Deadline
            <input
              required
              type="date"
              value={form.deadline}
              onChange={(e) =>
                update("deadline", e.target.value)
              }
            />
          </label>

          <label>
            Eligibility
            <input
              required
              value={form.eligibility}
              onChange={(e) =>
                update("eligibility", e.target.value)
              }
            />
          </label>

          <label>
            Description
            <input
              value={form.description}
              onChange={(e) =>
                update("description", e.target.value)
              }
            />
          </label>

          <label>
            Application Link
            <input
              value={form.link}
              onChange={(e) =>
                update("link", e.target.value)
              }
            />
          </label>

          <button className="btn-primary">
            {editing
              ? "Update Opportunity"
              : "Save Opportunity"}
          </button>

          {editing && (
            <button
              type="button"
              className="btn-plain"
              onClick={() => {
                setEditing(null);
                setForm(blank);
                setShow(false);
              }}
            >
              Cancel
            </button>
          )}
        </form>
      )}

      <div className="opportunity-grid">
        {items.length === 0 ? (
          <div className="panel empty">
            <h3>No Funding Opportunities</h3>

            <p>
              Add funding opportunities to enable
              recommendations and grant matching.
            </p>
          </div>
        ) : (
          items.map((item) => (
            <article
              className="opportunity"
              key={item.id}
            >
              <span className="tag">
                {item.research_domain}
              </span>

              <h3>{item.title}</h3>

              <p>{item.funding_agency}</p>

              <div className="opportunity-meta">
                <span>{item.amount}</span>

                <span>Due {item.deadline}</span>
              </div>

              <small>{item.technology_area}</small>

              <br />

              <small>{item.keywords}</small>

              {item.description && (
                <p className="description">
                  {item.description}
                </p>
              )}

              <div className="record-actions">
                <button
                  onClick={() =>
                    editOpportunity(item)
                  }
                >
                  Edit
                </button>

                <button
                  className="danger"
                  onClick={() =>
                    remove(item.id)
                  }
                >
                  Delete
                </button>

                {item.link && (
                  <a
                    href={item.link}
                    target="_blank"
                    rel="noreferrer"
                  >
                    Apply ↗
                  </a>
                )}
              </div>
            </article>
          ))
        )}
      </div>
    </section>
  );
}