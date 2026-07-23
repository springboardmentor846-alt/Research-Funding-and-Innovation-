import { useEffect, useState } from "react";
import api from "../api/api";
import { toast } from "react-toastify";

const blank = {
  title: "",
  assignee: "",
  filing_date: "",
  patent_number: "",
  technology_domain: "",
};

export default function Patents() {
  const [items, setItems] = useState([]);
  const [form, setForm] = useState(blank);
  const [editing, setEditing] = useState(null);

  const load = () => {
    api
      .get("/patents/")
      .then((res) => setItems(res.data))
      .catch((err) =>
        toast.error(
          err.response?.data?.detail ||
            "Create a research profile before adding patents."
        )
      );
  };

  useEffect(() => {
    load();
  }, []);

  const submit = async (e) => {
    e.preventDefault();

    try {
      if (editing) {
        await api.put(`/patents/${editing}`, form);
      } else {
        await api.post("/patents/", form);
      }

      toast.success(
        editing
          ? "Patent updated successfully"
          : "Patent added successfully"
      );

      setForm(blank);
      setEditing(null);
      load();
    } catch (err) {
      toast.error(
        err.response?.data?.detail ||
          "Could not save patent"
      );
    }
  };

  const remove = async (id) => {
    if (!window.confirm("Delete this patent?")) return;

    try {
      await api.delete(`/patents/${id}`);
      toast.success("Patent deleted");
      load();
    } catch {
      toast.error("Could not delete patent");
    }
  };

  return (
    <section>
      <div className="page-heading">
        <div>
          <p className="eyebrow">INNOVATION ASSETS</p>

          <h1>Patents</h1>

          <p>
            Record your inventions and intellectual
            property for funding and commercialization.
          </p>
        </div>
      </div>

      <form className="panel compact-form" onSubmit={submit}>
        <label>
          Title
          <input
            required
            value={form.title}
            onChange={(e) =>
              setForm({
                ...form,
                title: e.target.value,
              })
            }
          />
        </label>

        <label>
          Assignee
          <input
            required
            value={form.assignee}
            onChange={(e) =>
              setForm({
                ...form,
                assignee: e.target.value,
              })
            }
          />
        </label>

        <label>
          Filing Date
          <input
            required
            type="date"
            value={form.filing_date}
            onChange={(e) =>
              setForm({
                ...form,
                filing_date: e.target.value,
              })
            }
          />
        </label>

        <label>
          Patent Number
          <input
            required
            value={form.patent_number}
            onChange={(e) =>
              setForm({
                ...form,
                patent_number: e.target.value,
              })
            }
          />
        </label>

        <label>
          Technology Domain
          <input
            required
            value={form.technology_domain}
            onChange={(e) =>
              setForm({
                ...form,
                technology_domain: e.target.value,
              })
            }
          />
        </label>

        <button className="btn-primary">
          {editing ? "Update Patent" : "Add Patent"}
        </button>

        {editing && (
          <button
            type="button"
            className="btn-plain"
            onClick={() => {
              setEditing(null);
              setForm(blank);
            }}
          >
            Cancel
          </button>
        )}
      </form>

      <div className="record-list">
        {items.length === 0 ? (
          <div className="panel empty">
            <h3>No Patents Added</h3>
            <p>
              Add your first patent to build your
              innovation portfolio.
            </p>
          </div>
        ) : (
          items.map((item) => (
            <article className="record" key={item.id}>
              <div>
                <h3>{item.title}</h3>

                <p>
                  {item.assignee} •{" "}
                  {item.technology_domain}
                </p>

                <small>
                  Patent No: {item.patent_number}
                </small>

                <br />

                <small>
                  Filing Date: {item.filing_date}
                </small>
              </div>

              <div className="record-actions">
                <button
                  onClick={() => {
                    setEditing(item.id);
                    setForm({
                        title: item.title || "",
                        assignee: item.assignee || "",
                        filing_date: item.filing_date || "",
                        patent_number: item.patent_number || "",
                        technology_domain: item.technology_domain || "",
                    });
                  }}
                >
                  Edit
                </button>

                <button
                  className="danger"
                  onClick={() => remove(item.id)}
                >
                  Delete
                </button>
              </div>
            </article>
          ))
        )}
      </div>
    </section>
  );
}