import { useEffect, useState } from "react";
import api from "../api/api";
import { toast } from "react-toastify";

const empty = {
  organization: "",
  research_domain: "",
  technology_area: "",
  keywords: "",
  publication_count: 0,
  patents: 0,
};

export default function Profile() {
  const [form, setForm] = useState(empty);
  const [exists, setExists] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api
      .get("/profile/")
      .then(({ data }) => {
        setForm(data);
        setExists(true);
      })
      .catch((err) => {
        if (err.response?.status !== 404)
          toast.error("Could not load profile");
      })
      .finally(() => setLoading(false));
  }, []);

  const update = (key, value) =>
    setForm((prev) => ({ ...prev, [key]: value }));

  const submit = async (e) => {
    e.preventDefault();

    try {
      await api[exists ? "put" : "post"]("/profile/", form);

      setExists(true);

      toast.success(
        exists
          ? "Profile updated successfully"
          : "Profile created successfully"
      );
    } catch (err) {
      toast.error(err.response?.data?.detail || "Failed");
    }
  };

  const remove = async () => {
    if (
      !window.confirm(
        "Delete your profile permanently?"
      )
    )
      return;

    try {
      await api.delete("/profile/");

      setForm(empty);
      setExists(false);

      toast.success("Profile deleted");
    } catch (err) {
      toast.error(err.response?.data?.detail || "Delete failed");
    }
  };

  if (loading)
    return (
      <div className="text-center mt-5">
        <div
          className="spinner-border text-primary"
          role="status"
        />
      </div>
    );

  return (
    <div className="container-fluid">

      <div className="mb-4">
        <h2 className="fw-bold">Research Profile</h2>
        <p className="text-muted">
          Manage your research identity used for
          funding recommendations and grant matching.
        </p>
      </div>

      <div className="card shadow-sm border-0">

        <div className="card-body">

          <form onSubmit={submit}>

            <div className="row">

              <div className="col-md-6 mb-3">
                <label className="form-label">
                  Organization
                </label>

                <input
                  className="form-control"
                  required
                  value={form.organization}
                  onChange={(e) =>
                    update("organization", e.target.value)
                  }
                />
              </div>

              <div className="col-md-6 mb-3">
                <label className="form-label">
                  Research Domain
                </label>

                <input
                  className="form-control"
                  required
                  value={form.research_domain}
                  onChange={(e) =>
                    update(
                      "research_domain",
                      e.target.value
                    )
                  }
                />
              </div>

              <div className="col-md-6 mb-3">
                <label className="form-label">
                  Technology Area
                </label>

                <input
                  className="form-control"
                  required
                  value={form.technology_area}
                  onChange={(e) =>
                    update(
                      "technology_area",
                      e.target.value
                    )
                  }
                />
              </div>

              <div className="col-md-6 mb-3">
                <label className="form-label">
                  Keywords
                </label>

                <input
                  className="form-control"
                  placeholder="AI, Machine Learning..."
                  value={form.keywords}
                  onChange={(e) =>
                    update("keywords", e.target.value)
                  }
                />
              </div>

              <div className="col-md-6 mb-3">
                <label className="form-label">
                  Publication Count
                </label>

                <input
                  className="form-control"
                  type="number"
                  min="0"
                  value={form.publication_count}
                  onChange={(e) =>
                    update(
                      "publication_count",
                      Number(e.target.value)
                    )
                  }
                />
              </div>

              <div className="col-md-6 mb-3">
                <label className="form-label">
                  Patent Count
                </label>

                <input
                  className="form-control"
                  type="number"
                  min="0"
                  value={form.patents}
                  onChange={(e) =>
                    update(
                      "patents",
                      Number(e.target.value)
                    )
                  }
                />
              </div>

            </div>

            <div className="mt-4 d-flex gap-3">

              <button
                className="btn btn-primary"
                type="submit"
              >
                {exists
                  ? "Update Profile"
                  : "Create Profile"}
              </button>

              {exists && (
                <button
                  type="button"
                  className="btn btn-outline-danger"
                  onClick={remove}
                >
                  Delete Profile
                </button>
              )}

            </div>

          </form>

        </div>

      </div>

    </div>
  );
}