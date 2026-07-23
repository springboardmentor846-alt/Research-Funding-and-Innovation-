import { useEffect, useState } from "react";
import api from "../api/api";
import { toast } from "react-toastify";

const blank = {
  title: "",
  authors: "",
  journal: "",
  publication_year: new Date().getFullYear(),
  doi: "",
};

export default function Publications() {
  const [items, setItems] = useState([]);
  const [form, setForm] = useState(blank);
  const [editing, setEditing] = useState(null);

  const load = async () => {
    try {
      const res = await api.get("/publications/");
      setItems(res.data);
    } catch (e) {
      toast.error(
        e.response?.data?.detail ||
          "Create a profile before adding publications"
      );
    }
  };

  useEffect(() => {
    load();
  }, []);

  const submit = async (e) => {
    e.preventDefault();

    try {
      if (editing) {
        await api.put(`/publications/${editing}`, form);
      } else {
        await api.post("/publications/", form);
      }

      toast.success(
        editing
          ? "Publication updated successfully"
          : "Publication added successfully"
      );

      setForm(blank);
      setEditing(null);
      load();
    } catch (e) {
      toast.error(
        e.response?.data?.detail ||
          "Could not save publication"
      );
    }
  };

  const remove = async (id) => {
    if (!window.confirm("Delete this publication?")) return;

    try {
      await api.delete(`/publications/${id}`);
      toast.success("Publication deleted");
      load();
    } catch (e) {
      toast.error(
        e.response?.data?.detail ||
          "Could not delete publication"
      );
    }
  };

  const editPublication = (item) => {
    setEditing(item.id);

    setForm({
      title: item.title || "",
      authors: item.authors || "",
      journal: item.journal || "",
      publication_year:
        item.publication_year || new Date().getFullYear(),
      doi: item.doi || "",
    });
  };

  return (
    <section>
      <div className="page-heading">
        <div>
          <p className="eyebrow">SCHOLARLY OUTPUT</p>
          <h1>Publications</h1>
          <p>
            Keep your publication record current for
            stronger grant applications.
          </p>
        </div>
      </div>

      <form
        className="panel compact-form"
        onSubmit={submit}
      >
        <label>
          Title
          <input
            type="text"
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
          Authors
          <input
            type="text"
            required
            value={form.authors}
            onChange={(e) =>
              setForm({
                ...form,
                authors: e.target.value,
              })
            }
          />
        </label>

        <label>
          Journal
          <input
            type="text"
            required
            value={form.journal}
            onChange={(e) =>
              setForm({
                ...form,
                journal: e.target.value,
              })
            }
          />
        </label>

        <label>
          Publication Year
          <input
            type="number"
            required
            value={form.publication_year}
            onChange={(e) =>
              setForm({
                ...form,
                publication_year: Number(e.target.value),
              })
            }
          />
        </label>

        <label>
          DOI
          <input
            type="text"
            value={form.doi}
            onChange={(e) =>
              setForm({
                ...form,
                doi: e.target.value,
              })
            }
          />
        </label>

        <button className="btn-primary">
          {editing
            ? "Update Publication"
            : "Add Publication"}
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
          <p className="empty">
            No publications found.
          </p>
        ) : (
          items.map((item) => (
            <article
              className="record"
              key={item.id}
            >
              <div>
                <h3>{item.title}</h3>

                <p>
                  {item.authors}
                  <br />
                  {item.journal} •{" "}
                  {item.publication_year}
                </p>

                {item.doi && (
                  <small>DOI: {item.doi}</small>
                )}
              </div>

              <div className="record-actions">
                <button
                  onClick={() =>
                    editPublication(item)
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
              </div>
            </article>
          ))
        )}
      </div>
    </section>
  );
}