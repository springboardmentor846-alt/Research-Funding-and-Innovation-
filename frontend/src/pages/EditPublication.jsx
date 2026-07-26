import { useState, useEffect } from "react";
import { useNavigate, useParams, Link } from "react-router-dom";
import { BookOpen, ArrowLeft } from "lucide-react";
import Layout from "@/components/Layout";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Skeleton } from "@/components/LoadingSkeleton";
import api from "@/services/api";

const PUBLICATION_TYPES = [
  "Journal",
  "Conference",
  "Book Chapter",
  "Thesis",
  "Preprint",
  "Workshop",
];

export default function EditPublication() {
  const navigate = useNavigate();
  const { id } = useParams();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [form, setForm] = useState({
    title: "",
    authors: "",
    publication_type: "Journal",
    journal_or_conference: "",
    publication_year: new Date().getFullYear(),
    doi: "",
    abstract: "",
    keywords: "",
    pdf_url: "",
  });

  useEffect(() => {
    fetchPublication();
  }, [id]);

  const fetchPublication = async () => {
    setLoading(true);
    try {
      const res = await api.get(`/my-publications/${id}`);
      setForm(res.data);
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to load publication");
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setSaving(true);

    try {
      await api.put(`/my-publications/${id}`, form);
      navigate("/my-publications");
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to update publication");
    } finally {
      setSaving(false);
    }
  };

  return (
    <Layout>
      <div className="max-w-2xl mx-auto space-y-5">
        <Link
          to="/my-publications"
          className="flex items-center gap-1.5 text-sm text-slate-500 hover:text-slate-800"
        >
          <ArrowLeft size={15} /> Back to My Publications
        </Link>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <BookOpen size={20} /> Edit Publication
            </CardTitle>
          </CardHeader>
          <CardContent>
            {loading ? (
              <div className="space-y-4">
                <Skeleton className="h-10 w-full" />
                <Skeleton className="h-10 w-full" />
                <Skeleton className="h-10 w-full" />
              </div>
            ) : (
              <>
                {error && (
                  <div className="mb-4 p-3 bg-red-50 border border-red-200 text-red-600 rounded-lg text-sm">
                    {error}
                  </div>
                )}

                <form onSubmit={handleSubmit} className="space-y-5">
                  {/* Title */}
                  <div>
                    <Label htmlFor="title">Publication Title *</Label>
                    <Input
                      id="title"
                      name="title"
                      value={form.title}
                      onChange={handleChange}
                      required
                      className="mt-2"
                    />
                  </div>

                  {/* Authors */}
                  <div>
                    <Label htmlFor="authors">Authors *</Label>
                    <Input
                      id="authors"
                      name="authors"
                      value={form.authors}
                      onChange={handleChange}
                      required
                      className="mt-2"
                    />
                  </div>

                  {/* Publication Type */}
                  <div>
                    <Label htmlFor="publication_type">Publication Type *</Label>
                    <select
                      id="publication_type"
                      name="publication_type"
                      value={form.publication_type}
                      onChange={handleChange}
                      className="w-full mt-2 border border-slate-200 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-400"
                    >
                      {PUBLICATION_TYPES.map((type) => (
                        <option key={type} value={type}>
                          {type}
                        </option>
                      ))}
                    </select>
                  </div>

                  {/* Journal or Conference */}
                  <div>
                    <Label htmlFor="journal_or_conference">
                      Journal or Conference Name *
                    </Label>
                    <Input
                      id="journal_or_conference"
                      name="journal_or_conference"
                      value={form.journal_or_conference}
                      onChange={handleChange}
                      required
                      className="mt-2"
                    />
                  </div>

                  {/* Publication Year */}
                  <div>
                    <Label htmlFor="publication_year">Publication Year *</Label>
                    <Input
                      id="publication_year"
                      name="publication_year"
                      type="number"
                      min="1900"
                      max={new Date().getFullYear()}
                      value={form.publication_year}
                      onChange={handleChange}
                      required
                      className="mt-2"
                    />
                  </div>

                  {/* DOI */}
                  <div>
                    <Label htmlFor="doi">DOI (Optional)</Label>
                    <Input
                      id="doi"
                      name="doi"
                      value={form.doi}
                      onChange={handleChange}
                      className="mt-2"
                    />
                  </div>

                  {/* Abstract */}
                  <div>
                    <Label htmlFor="abstract">Abstract *</Label>
                    <textarea
                      id="abstract"
                      name="abstract"
                      value={form.abstract}
                      onChange={handleChange}
                      required
                      rows="5"
                      className="w-full mt-2 border border-slate-200 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-400"
                    />
                  </div>

                  {/* Keywords */}
                  <div>
                    <Label htmlFor="keywords">Keywords *</Label>
                    <Input
                      id="keywords"
                      name="keywords"
                      value={form.keywords}
                      onChange={handleChange}
                      required
                      className="mt-2"
                    />
                  </div>

                  {/* PDF URL */}
                  <div>
                    <Label htmlFor="pdf_url">PDF URL (Optional)</Label>
                    <Input
                      id="pdf_url"
                      name="pdf_url"
                      type="url"
                      value={form.pdf_url}
                      onChange={handleChange}
                      className="mt-2"
                    />
                  </div>

                  {/* Submit Button */}
                  <div className="flex gap-3 pt-4">
                    <Button
                      type="submit"
                      disabled={saving}
                      className="flex-1"
                    >
                      {saving ? "Saving..." : "Save Changes"}
                    </Button>
                    <Button
                      type="button"
                      variant="outline"
                      onClick={() => navigate("/my-publications")}
                      className="flex-1"
                    >
                      Cancel
                    </Button>
                  </div>
                </form>
              </>
            )}
          </CardContent>
        </Card>
      </div>
    </Layout>
  );
}
