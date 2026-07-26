import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { BookOpen, Plus, Edit2, Trash2, ExternalLink } from "lucide-react";
import Layout from "@/components/Layout";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { CardGridSkeleton } from "@/components/LoadingSkeleton";
import api from "@/services/api";

export default function MyPublications() {
  const navigate = useNavigate();
  const [publications, setPublications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [deleting, setDeleting] = useState(null);

  useEffect(() => {
    fetchPublications();
  }, []);

  const fetchPublications = async () => {
    setLoading(true);
    try {
      const res = await api.get("/my-publications/");
      setPublications(res.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm("Are you sure you want to delete this publication?")) {
      return;
    }

    setDeleting(id);
    try {
      await api.delete(`/my-publications/${id}`);
      setPublications((prev) => prev.filter((p) => p.id !== id));
    } catch (err) {
      alert(err.response?.data?.detail || "Failed to delete publication");
    } finally {
      setDeleting(null);
    }
  };

  return (
    <Layout>
      <div className="space-y-5">
        {/* Header */}
        <div className="flex items-center justify-between flex-wrap gap-3">
          <div>
            <h2 className="text-xl font-bold text-slate-800 flex items-center gap-2">
              <BookOpen size={20} /> My Publications
            </h2>
            <p className="text-sm text-slate-500">{publications.length} publications</p>
          </div>
          <Link to="/add-publication">
            <Button>
              <Plus size={16} /> Add Publication
            </Button>
          </Link>
        </div>

        {/* Publications List */}
        {loading ? (
          <CardGridSkeleton count={3} />
        ) : publications.length === 0 ? (
          <Card>
            <CardContent className="p-10 text-center">
              <BookOpen size={40} className="mx-auto text-slate-300 mb-3" />
              <p className="text-slate-500 mb-4">No publications yet</p>
              <Link to="/add-publication">
                <Button>Add Your First Publication</Button>
              </Link>
            </CardContent>
          </Card>
        ) : (
          <div className="space-y-3">
            {publications.map((pub) => (
              <Card key={pub.id} className="hover:shadow-md transition-shadow">
                <CardContent className="p-5">
                  <div className="flex items-start justify-between gap-4 mb-3">
                    <div className="flex-1">
                      <h3 className="font-semibold text-slate-800 text-sm leading-snug mb-1">
                        {pub.title}
                      </h3>
                      <p className="text-xs text-slate-500 mb-2">{pub.authors}</p>
                      <div className="flex flex-wrap gap-2 items-center text-xs text-slate-600">
                        <span className="px-2 py-0.5 bg-blue-50 text-blue-700 rounded-full">
                          {pub.publication_type}
                        </span>
                        <span>{pub.journal_or_conference}</span>
                        <span className="text-slate-400">•</span>
                        <span>{pub.publication_year}</span>
                        {pub.doi && (
                          <>
                            <span className="text-slate-400">•</span>
                            <span className="font-mono text-slate-500">{pub.doi}</span>
                          </>
                        )}
                      </div>
                    </div>
                    <div className="flex gap-2 shrink-0">
                      <button
                        onClick={() => navigate(`/edit-publication/${pub.id}`)}
                        className="p-2 hover:bg-slate-100 rounded-lg transition-colors"
                        title="Edit"
                      >
                        <Edit2 size={16} className="text-slate-600" />
                      </button>
                      <button
                        onClick={() => handleDelete(pub.id)}
                        disabled={deleting === pub.id}
                        className="p-2 hover:bg-red-50 rounded-lg transition-colors disabled:opacity-50"
                        title="Delete"
                      >
                        <Trash2 size={16} className="text-red-600" />
                      </button>
                      {pub.pdf_url && (
                        <a
                          href={pub.pdf_url}
                          target="_blank"
                          rel="noreferrer"
                          className="p-2 hover:bg-slate-100 rounded-lg transition-colors"
                          title="View PDF"
                        >
                          <ExternalLink size={16} className="text-slate-600" />
                        </a>
                      )}
                    </div>
                  </div>
                  <p className="text-xs text-slate-600 line-clamp-2 mb-2">
                    {pub.abstract}
                  </p>
                  <div className="flex flex-wrap gap-1">
                    {pub.keywords.split(",").slice(0, 3).map((kw) => (
                      <span
                        key={kw.trim()}
                        className="px-2 py-0.5 bg-slate-100 text-slate-600 rounded text-xs"
                      >
                        {kw.trim()}
                      </span>
                    ))}
                    {pub.keywords.split(",").length > 3 && (
                      <span className="px-2 py-0.5 text-slate-500 text-xs">
                        +{pub.keywords.split(",").length - 3} more
                      </span>
                    )}
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>
    </Layout>
  );
}
