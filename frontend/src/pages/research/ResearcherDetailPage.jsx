import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import {
  Building2, GraduationCap, Award, BookOpen, ExternalLink, History, ArrowLeft,
  Tag, Calendar, DollarSign, UserCheck
} from 'lucide-react'
import toast from 'react-hot-toast'
import { clsx } from 'clsx'
import { researchProfileService } from '@/services/researchProfileService'

export default function ResearcherDetailPage() {
  const { id } = useParams()
  const [loading, setLoading] = useState(true)
  const [profile, setProfile] = useState(null)
  const [activeTab, setActiveTab] = useState('overview')

  useEffect(() => {
    fetchProfile()
  }, [id])

  const fetchProfile = async () => {
    try {
      setLoading(true)
      const data = await researchProfileService.getPublicProfile(id)
      setProfile(data)
    } catch (err) {
      toast.error('Failed to load researcher profile.')
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] gap-4">
        <div className="w-10 h-10 rounded-full border-4 border-brand-500 border-t-transparent animate-spin" />
        <p className="text-surface-400 text-sm animate-pulse">Loading researcher profile...</p>
      </div>
    )
  }

  if (!profile) {
    return (
      <div className="max-w-4xl mx-auto py-12 text-center space-y-4">
        <h2 className="text-xl font-bold text-white">Profile Not Found</h2>
        <Link to="/researchers" className="btn-primary inline-flex items-center gap-2 text-xs">
          <ArrowLeft className="w-4 h-4" /> Back to Directory
        </Link>
      </div>
    )
  }

  return (
    <div className="max-w-6xl mx-auto space-y-8 animate-fade-in pb-12">
      {/* Back button */}
      <div>
        <Link
          to="/researchers"
          className="inline-flex items-center gap-2 text-xs font-semibold text-surface-400 hover:text-brand-300 transition-colors"
        >
          <ArrowLeft className="w-4 h-4" /> Back to Researcher Directory
        </Link>
      </div>

      {/* Header Banner */}
      <div className="glass-card rounded-2xl p-6 md:p-8 relative overflow-hidden">
        <div className="flex flex-col md:flex-row items-center md:items-start gap-6">
          <div className="w-24 h-24 md:w-28 md:h-28 rounded-2xl bg-gradient-to-br from-brand-600 to-accent-600 p-1 shadow-glow-brand overflow-hidden flex-shrink-0">
            {profile.avatar_url ? (
              <img
                src={profile.avatar_url}
                alt={profile.full_name || 'Researcher'}
                className="w-full h-full object-cover rounded-[14px]"
              />
            ) : (
              <div className="w-full h-full bg-surface-900 rounded-[14px] flex items-center justify-center text-white font-bold text-3xl">
                {profile.full_name?.charAt(0).toUpperCase() || 'R'}
              </div>
            )}
          </div>

          <div className="flex-1 text-center md:text-left space-y-2">
            <div className="flex flex-wrap items-center justify-center md:justify-start gap-3">
              <h1 className="text-2xl md:text-3xl font-bold text-white">
                {profile.full_name || 'Researcher Profile'}
              </h1>
              <span className="badge badge-brand text-xs uppercase">
                {profile.user_role || 'Researcher'}
              </span>
            </div>

            <p className="text-surface-300 text-sm flex items-center justify-center md:justify-start gap-2">
              <Building2 className="w-4 h-4 text-brand-400" />
              <span>{profile.position || 'Researcher'}</span>
              <span>•</span>
              <span>{profile.organization_name || 'Academic Institution'}</span>
            </p>

            {/* Metrics */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 pt-3">
              <div className="glass px-4 py-2.5 rounded-xl border border-white/5 text-center">
                <span className="text-xs text-surface-400 block">h-index</span>
                <span className="text-lg font-bold text-brand-400">{profile.h_index || 0}</span>
              </div>
              <div className="glass px-4 py-2.5 rounded-xl border border-white/5 text-center">
                <span className="text-xs text-surface-400 block">Publications</span>
                <span className="text-lg font-bold text-accent-400">{profile.publications.length}</span>
              </div>
              <div className="glass px-4 py-2.5 rounded-xl border border-white/5 text-center">
                <span className="text-xs text-surface-400 block">Patents</span>
                <span className="text-lg font-bold text-green-400">{profile.patents.length}</span>
              </div>
              <div className="glass px-4 py-2.5 rounded-xl border border-white/5 text-center">
                <span className="text-xs text-surface-400 block">Total Citations</span>
                <span className="text-lg font-bold text-orange-400">{profile.total_citations || 0}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex items-center gap-2 border-b border-white/10 overflow-x-auto pb-1">
        {[
          { id: 'overview', label: 'Overview & Bio', icon: GraduationCap },
          { id: 'publications', label: `Publications (${profile.publications.length})`, icon: BookOpen },
          { id: 'patents', label: `Patents (${profile.patents.length})`, icon: Award },
          { id: 'projects', label: `Research History (${profile.projects.length})`, icon: History },
        ].map(({ id: tabId, label, icon: Icon }) => (
          <button
            key={tabId}
            onClick={() => setActiveTab(tabId)}
            className={clsx(
              'flex items-center gap-2 px-5 py-3 rounded-xl text-sm font-semibold whitespace-nowrap transition-all duration-200 border',
              activeTab === tabId
                ? 'bg-brand-600/20 text-brand-300 border-brand-500/40 shadow-glow-brand'
                : 'text-surface-400 border-transparent hover:text-white hover:bg-white/5'
            )}
          >
            <Icon className="w-4 h-4" />
            {label}
          </button>
        ))}
      </div>

      {/* Content */}
      {activeTab === 'overview' && (
        <div className="space-y-6">
          {profile.summary_bio && (
            <div className="glass-card rounded-2xl p-6 space-y-3">
              <h2 className="text-base font-bold text-white">Research Vision & Executive Summary</h2>
              <p className="text-surface-300 text-sm leading-relaxed">{profile.summary_bio}</p>
            </div>
          )}

          {/* Academic & External profiles */}
          <div className="glass-card rounded-2xl p-6 space-y-4">
            <h2 className="text-base font-bold text-white flex items-center gap-2">
              <GraduationCap className="w-5 h-5 text-accent-400" /> Academic & Scholarly Profiles
            </h2>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
              <div>
                <span className="text-surface-400 text-xs block">Highest Degree</span>
                <span className="text-white font-medium">{profile.academic_degree || 'N/A'}</span>
              </div>
              <div>
                <span className="text-surface-400 text-xs block">Field of Study</span>
                <span className="text-white font-medium">{profile.field_of_study || 'N/A'}</span>
              </div>
              <div>
                <span className="text-surface-400 text-xs block">Degree Institution</span>
                <span className="text-white font-medium">{profile.institution_name || 'N/A'}</span>
              </div>
            </div>

            {(profile.orcid_id || profile.google_scholar_url || profile.scopus_id) && (
              <div className="flex flex-wrap gap-4 pt-4 border-t border-white/5 text-xs">
                {profile.orcid_id && (
                  <span className="text-brand-300 font-mono">ORCID: {profile.orcid_id}</span>
                )}
                {profile.google_scholar_url && (
                  <a
                    href={profile.google_scholar_url}
                    target="_blank"
                    rel="noreferrer"
                    className="text-brand-400 hover:underline flex items-center gap-1"
                  >
                    Google Scholar <ExternalLink className="w-3 h-3" />
                  </a>
                )}
              </div>
            )}
          </div>

          {/* Domains & Technology Tags */}
          <div className="glass-card rounded-2xl p-6 space-y-4">
            <h2 className="text-base font-bold text-white flex items-center gap-2">
              <Tag className="w-5 h-5 text-green-400" /> Research Domains & Technology Focus
            </h2>

            {profile.research_domains?.length > 0 && (
              <div>
                <span className="text-xs text-surface-400 block mb-2">Research Domains</span>
                <div className="flex flex-wrap gap-2">
                  {profile.research_domains.map((d) => (
                    <span key={d} className="badge badge-brand text-xs">
                      {d}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {profile.keywords?.length > 0 && (
              <div>
                <span className="text-xs text-surface-400 block mb-2">Keywords & Methodologies</span>
                <div className="flex flex-wrap gap-2">
                  {profile.keywords.map((k) => (
                    <span key={k} className="badge badge-accent text-xs">
                      {k}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {profile.technology_interests?.length > 0 && (
              <div>
                <span className="text-xs text-surface-400 block mb-2">Technology Interests</span>
                <div className="flex flex-wrap gap-2">
                  {profile.technology_interests.map((t) => (
                    <span key={t} className="badge badge-green text-xs">
                      {t}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Publications */}
      {activeTab === 'publications' && (
        <div className="space-y-4">
          {profile.publications.length === 0 ? (
            <p className="text-surface-400 text-sm">No publications listed.</p>
          ) : (
            profile.publications.map((pub) => (
              <div key={pub.id} className="glass-card rounded-xl p-5 space-y-2">
                <h3 className="text-lg font-semibold text-white">{pub.title}</h3>
                <p className="text-xs text-surface-400">{pub.authors}</p>
                <div className="flex flex-wrap items-center gap-3 text-xs text-surface-300">
                  {pub.venue && <span className="badge badge-brand">{pub.venue}</span>}
                  {pub.year && <span>Year: {pub.year}</span>}
                  {pub.url && (
                    <a href={pub.url} target="_blank" rel="noreferrer" className="text-brand-400 hover:underline inline-flex items-center gap-1">
                      Publication Link <ExternalLink className="w-3 h-3" />
                    </a>
                  )}
                </div>
              </div>
            ))
          )}
        </div>
      )}

      {/* Patents */}
      {activeTab === 'patents' && (
        <div className="space-y-4">
          {profile.patents.length === 0 ? (
            <p className="text-surface-400 text-sm">No patents listed.</p>
          ) : (
            profile.patents.map((pat) => (
              <div key={pat.id} className="glass-card rounded-xl p-5 space-y-2">
                <div className="flex items-center justify-between">
                  <h3 className="text-lg font-semibold text-white">{pat.title}</h3>
                  <span className="badge badge-green uppercase text-[10px]">{pat.status}</span>
                </div>
                {pat.patent_number && <p className="text-xs text-brand-300 font-mono">Patent #: {pat.patent_number}</p>}
                {pat.abstract && <p className="text-xs text-surface-400">{pat.abstract}</p>}
              </div>
            ))
          )}
        </div>
      )}

      {/* Research History */}
      {activeTab === 'projects' && (
        <div className="space-y-4">
          {profile.projects.length === 0 ? (
            <p className="text-surface-400 text-sm">No research projects listed.</p>
          ) : (
            profile.projects.map((proj) => (
              <div key={proj.id} className="glass-card rounded-xl p-5 space-y-2">
                <div className="flex items-center justify-between">
                  <h3 className="text-lg font-semibold text-white">{proj.title}</h3>
                  <span className="badge badge-brand uppercase text-[10px]">{proj.status}</span>
                </div>
                <p className="text-xs text-surface-400">{proj.role} {proj.sponsor_organization && `• Sponsored by ${proj.sponsor_organization}`}</p>
                {proj.summary && <p className="text-xs text-surface-400">{proj.summary}</p>}
              </div>
            ))
          )}
        </div>
      )}
    </div>
  )
}
