import { useState, useEffect } from 'react'
import {
  UserCheck, Building2, GraduationCap, Award, BookOpen, FileCode, History,
  Plus, Trash2, Edit3, Upload, X, ExternalLink, Tag, Search, CheckCircle2,
  AlertCircle, DollarSign, Calendar
} from 'lucide-react'
import toast from 'react-hot-toast'
import { clsx } from 'clsx'
import { researchProfileService } from '@/services/researchProfileService'

const ORG_TYPES = [
  { value: 'university', label: 'University / Academia' },
  { value: 'research_institute', label: 'Research Institute' },
  { value: 'corporate_rd', label: 'Corporate R&D' },
  { value: 'startup', label: 'Tech Startup' },
  { value: 'government', label: 'Government Agency' },
  { value: 'other', label: 'Other' },
]

const PATENT_STATUSES = [
  { value: 'granted', label: 'Granted' },
  { value: 'pending', label: 'Pending' },
  { value: 'filed', label: 'Filed' },
  { value: 'expired', label: 'Expired' },
]

const PROJECT_STATUSES = [
  { value: 'ongoing', label: 'Ongoing' },
  { value: 'completed', label: 'Completed' },
  { value: 'proposed', label: 'Proposed' },
]

export default function ResearchProfilePage() {
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [uploadingAvatar, setUploadingAvatar] = useState(false)
  const [activeTab, setActiveTab] = useState('overview')

  const [profile, setProfile] = useState({
    organization_name: '',
    department: '',
    organization_type: 'university',
    position: '',
    academic_degree: '',
    field_of_study: '',
    institution_name: '',
    graduation_year: '',
    h_index: 0,
    i10_index: 0,
    total_citations: 0,
    orcid_id: '',
    google_scholar_url: '',
    scopus_id: '',
    research_domains: [],
    keywords: [],
    technology_interests: [],
    summary_bio: '',
    avatar_url: '',
    publications: [],
    patents: [],
    projects: [],
  })

  // Tag inputs state
  const [domainInput, setDomainInput] = useState('')
  const [keywordInput, setKeywordInput] = useState('')
  const [techInput, setTechInput] = useState('')

  // Modals state
  const [pubModalOpen, setPubModalOpen] = useState(false)
  const [editingPub, setEditingPub] = useState(null)
  const [pubForm, setPubForm] = useState({
    title: '', venue: '', year: '', doi: '', url: '', citations_count: 0, authors: '', abstract: ''
  })

  const [patentModalOpen, setPatentModalOpen] = useState(false)
  const [editingPatent, setEditingPatent] = useState(null)
  const [patentForm, setPatentForm] = useState({
    title: '', patent_number: '', status: 'pending', filing_date: '', issue_date: '', url: '', abstract: ''
  })

  const [projectModalOpen, setProjectModalOpen] = useState(false)
  const [editingProject, setEditingProject] = useState(null)
  const [projectForm, setProjectForm] = useState({
    title: '', role: '', sponsor_organization: '', funding_amount: '', start_date: '', end_date: '', status: 'ongoing', summary: ''
  })

  useEffect(() => {
    fetchProfile()
  }, [])

  const fetchProfile = async () => {
    try {
      setLoading(true)
      const data = await researchProfileService.getMyProfile()
      setProfile({
        ...data,
        graduation_year: data.graduation_year || '',
        research_domains: data.research_domains || [],
        keywords: data.keywords || [],
        technology_interests: data.technology_interests || [],
        publications: data.publications || [],
        patents: data.patents || [],
        projects: data.projects || [],
      })
    } catch (err) {
      toast.error('Failed to load research profile.')
    } finally {
      setLoading(false)
    }
  }

  // ── Profile Submit ──────────────────────────────────────────────────────────
  const handleSaveProfile = async (e) => {
    e.preventDefault()
    try {
      setSaving(true)
      const updated = await researchProfileService.updateMyProfile({
        organization_name: profile.organization_name,
        department: profile.department,
        organization_type: profile.organization_type,
        position: profile.position,
        academic_degree: profile.academic_degree,
        field_of_study: profile.field_of_study,
        institution_name: profile.institution_name,
        graduation_year: profile.graduation_year ? parseInt(profile.graduation_year, 10) : null,
        h_index: parseInt(profile.h_index || 0, 10),
        i10_index: parseInt(profile.i10_index || 0, 10),
        total_citations: parseInt(profile.total_citations || 0, 10),
        orcid_id: profile.orcid_id,
        google_scholar_url: profile.google_scholar_url,
        scopus_id: profile.scopus_id,
        research_domains: profile.research_domains,
        keywords: profile.keywords,
        technology_interests: profile.technology_interests,
        summary_bio: profile.summary_bio,
      })
      setProfile((prev) => ({ ...prev, ...updated }))
      toast.success('Research profile saved successfully!')
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to save profile.')
    } finally {
      setSaving(false)
    }
  }

  // ── Avatar Upload Handler ──────────────────────────────────────────────────
  const handleAvatarChange = async (e) => {
    const file = e.target.files[0]
    if (!file) return

    // Client-side validation
    if (!['image/jpeg', 'image/png', 'image/webp'].includes(file.type)) {
      toast.error('Invalid image type. Please select JPG, PNG, or WEBP.')
      return
    }
    if (file.size > 5 * 1024 * 1024) {
      toast.error('Image size must be under 5MB.')
      return
    }

    try {
      setUploadingAvatar(true)
      const res = await researchProfileService.uploadAvatar(file)
      setProfile((prev) => ({ ...prev, avatar_url: res.avatar_url }))
      toast.success('Profile picture updated!')
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to upload image.')
    } finally {
      setUploadingAvatar(false)
    }
  }

  // ── Tag Handlers ────────────────────────────────────────────────────────────
  const addTag = (type, value, setInput) => {
    const trimmed = value.trim()
    if (!trimmed) return
    if (!profile[type].includes(trimmed)) {
      setProfile((prev) => ({ ...prev, [type]: [...prev[type], trimmed] }))
    }
    setInput('')
  }

  const removeTag = (type, tagToRemove) => {
    setProfile((prev) => ({
      ...prev,
      [type]: prev[type].filter((t) => t !== tagToRemove),
    }))
  }

  // ── Publication CRUD ────────────────────────────────────────────────────────
  const openPubModal = (pub = null) => {
    if (pub) {
      setEditingPub(pub)
      setPubForm({ ...pub, year: pub.year || '', citations_count: pub.citations_count || 0 })
    } else {
      setEditingPub(null)
      setPubForm({ title: '', venue: '', year: '', doi: '', url: '', citations_count: 0, authors: '', abstract: '' })
    }
    setPubModalOpen(true)
  }

  const handleSavePublication = async (e) => {
    e.preventDefault()
    if (!pubForm.title.trim()) {
      toast.error('Publication title is required.')
      return
    }

    const payload = {
      ...pubForm,
      year: pubForm.year ? parseInt(pubForm.year, 10) : null,
      citations_count: parseInt(pubForm.citations_count || 0, 10),
    }

    try {
      if (editingPub) {
        const updated = await researchProfileService.updatePublication(editingPub.id, payload)
        setProfile((prev) => ({
          ...prev,
          publications: prev.publications.map((p) => (p.id === editingPub.id ? updated : p)),
        }))
        toast.success('Publication updated.')
      } else {
        const created = await researchProfileService.addPublication(payload)
        setProfile((prev) => ({
          ...prev,
          publications: [created, ...prev.publications],
        }))
        toast.success('Publication added.')
      }
      setPubModalOpen(false)
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to save publication.')
    }
  }

  const handleDeletePublication = async (id) => {
    if (!confirm('Are you sure you want to delete this publication?')) return
    try {
      await researchProfileService.deletePublication(id)
      setProfile((prev) => ({
        ...prev,
        publications: prev.publications.filter((p) => p.id !== id),
      }))
      toast.success('Publication removed.')
    } catch (err) {
      toast.error('Failed to delete publication.')
    }
  }

  // ── Patent CRUD ─────────────────────────────────────────────────────────────
  const openPatentModal = (pat = null) => {
    if (pat) {
      setEditingPatent(pat)
      setPatentForm({ ...pat })
    } else {
      setEditingPatent(null)
      setPatentForm({ title: '', patent_number: '', status: 'pending', filing_date: '', issue_date: '', url: '', abstract: '' })
    }
    setPatentModalOpen(true)
  }

  const handleSavePatent = async (e) => {
    e.preventDefault()
    if (!patentForm.title.trim()) {
      toast.error('Patent title is required.')
      return
    }

    try {
      if (editingPatent) {
        const updated = await researchProfileService.updatePatent(editingPatent.id, patentForm)
        setProfile((prev) => ({
          ...prev,
          patents: prev.patents.map((p) => (p.id === editingPatent.id ? updated : p)),
        }))
        toast.success('Patent updated.')
      } else {
        const created = await researchProfileService.addPatent(patentForm)
        setProfile((prev) => ({
          ...prev,
          patents: [created, ...prev.patents],
        }))
        toast.success('Patent added.')
      }
      setPatentModalOpen(false)
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to save patent.')
    }
  }

  const handleDeletePatent = async (id) => {
    if (!confirm('Are you sure you want to delete this patent?')) return
    try {
      await researchProfileService.deletePatent(id)
      setProfile((prev) => ({
        ...prev,
        patents: prev.patents.filter((p) => p.id !== id),
      }))
      toast.success('Patent removed.')
    } catch (err) {
      toast.error('Failed to delete patent.')
    }
  }

  // ── Project CRUD ────────────────────────────────────────────────────────────
  const openProjectModal = (proj = null) => {
    if (proj) {
      setEditingProject(proj)
      setProjectForm({ ...proj, funding_amount: proj.funding_amount || '' })
    } else {
      setEditingProject(null)
      setProjectForm({ title: '', role: '', sponsor_organization: '', funding_amount: '', start_date: '', end_date: '', status: 'ongoing', summary: '' })
    }
    setProjectModalOpen(true)
  }

  const handleSaveProject = async (e) => {
    e.preventDefault()
    if (!projectForm.title.trim()) {
      toast.error('Project title is required.')
      return
    }

    const payload = {
      ...projectForm,
      funding_amount: projectForm.funding_amount ? parseFloat(projectForm.funding_amount) : null,
    }

    try {
      if (editingProject) {
        const updated = await researchProfileService.updateProject(editingProject.id, payload)
        setProfile((prev) => ({
          ...prev,
          projects: prev.projects.map((p) => (p.id === editingProject.id ? updated : p)),
        }))
        toast.success('Research project updated.')
      } else {
        const created = await researchProfileService.addProject(payload)
        setProfile((prev) => ({
          ...prev,
          projects: [created, ...prev.projects],
        }))
        toast.success('Research project added.')
      }
      setProjectModalOpen(false)
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to save project.')
    }
  }

  const handleDeleteProject = async (id) => {
    if (!confirm('Are you sure you want to delete this project?')) return
    try {
      await researchProfileService.deleteProject(id)
      setProfile((prev) => ({
        ...prev,
        projects: prev.projects.filter((p) => p.id !== id),
      }))
      toast.success('Project removed.')
    } catch (err) {
      toast.error('Failed to delete project.')
    }
  }

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] gap-4">
        <div className="w-10 h-10 rounded-full border-4 border-brand-500 border-t-transparent animate-spin" />
        <p className="text-surface-400 text-sm animate-pulse">Loading research profile...</p>
      </div>
    )
  }

  return (
    <div className="max-w-6xl mx-auto space-y-8 animate-fade-in pb-12">
      {/* ── Header banner card ── */}
      <div className="glass-card rounded-2xl p-6 md:p-8 relative overflow-hidden">
        <div className="absolute top-0 right-0 w-96 h-96 bg-brand-500/10 rounded-full blur-3xl -z-10 pointer-events-none" />

        <div className="flex flex-col md:flex-row items-center md:items-start gap-6">
          {/* Avatar with Upload */}
          <div className="relative group flex-shrink-0">
            <div className="w-24 h-24 md:w-28 md:h-28 rounded-2xl bg-gradient-to-br from-brand-600 to-accent-600 p-1 shadow-glow-brand overflow-hidden">
              {profile.avatar_url ? (
                <img
                  src={profile.avatar_url}
                  alt={profile.full_name || 'Avatar'}
                  className="w-full h-full object-cover rounded-[14px]"
                />
              ) : (
                <div className="w-full h-full bg-surface-900 rounded-[14px] flex items-center justify-center text-white font-bold text-3xl">
                  {profile.full_name?.charAt(0).toUpperCase() || 'R'}
                </div>
              )}
            </div>

            <label className="absolute inset-0 bg-black/60 rounded-2xl flex flex-col items-center justify-center text-white opacity-0 group-hover:opacity-100 transition-opacity cursor-pointer text-xs font-medium gap-1">
              <Upload className="w-5 h-5" />
              <span>{uploadingAvatar ? 'Uploading...' : 'Change'}</span>
              <input
                type="file"
                accept="image/png,image/jpeg,image/webp"
                onChange={handleAvatarChange}
                disabled={uploadingAvatar}
                className="hidden"
              />
            </label>
          </div>

          {/* User info & quick stats */}
          <div className="flex-1 text-center md:text-left space-y-2">
            <div className="flex flex-wrap items-center justify-center md:justify-start gap-3">
              <h1 className="text-2xl md:text-3xl font-bold text-white">
                {profile.full_name || 'Research Profile'}
              </h1>
              <span className="badge badge-brand text-xs uppercase tracking-wider">
                {profile.user_role || 'Researcher'}
              </span>
            </div>

            <p className="text-surface-300 text-sm flex items-center justify-center md:justify-start gap-2">
              <Building2 className="w-4 h-4 text-brand-400" />
              <span>{profile.position || 'Researcher'}</span>
              <span>•</span>
              <span>{profile.organization_name || 'Academic / R&D Institution'}</span>
            </p>

            {/* Quick Metrics Bar */}
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
                <span className="text-xs text-surface-400 block">Projects</span>
                <span className="text-lg font-bold text-orange-400">{profile.projects.length}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* ── Tabs Navigation ── */}
      <div className="flex items-center gap-2 border-b border-white/10 overflow-x-auto pb-1">
        {[
          { id: 'overview', label: 'General & Academic Profile', icon: GraduationCap },
          { id: 'publications', label: `Publications (${profile.publications.length})`, icon: BookOpen },
          { id: 'patents', label: `Patents (${profile.patents.length})`, icon: Award },
          { id: 'projects', label: `Research History (${profile.projects.length})`, icon: History },
        ].map(({ id, label, icon: Icon }) => (
          <button
            key={id}
            onClick={() => setActiveTab(id)}
            className={clsx(
              'flex items-center gap-2 px-5 py-3 rounded-xl text-sm font-semibold whitespace-nowrap transition-all duration-200 border',
              activeTab === id
                ? 'bg-brand-600/20 text-brand-300 border-brand-500/40 shadow-glow-brand'
                : 'text-surface-400 border-transparent hover:text-white hover:bg-white/5'
            )}
          >
            <Icon className="w-4 h-4" />
            {label}
          </button>
        ))}
      </div>

      {/* ── TAB 1: General & Academic Profile Form ── */}
      {activeTab === 'overview' && (
        <form onSubmit={handleSaveProfile} className="space-y-6">
          {/* Organization details */}
          <div className="glass-card rounded-2xl p-6 space-y-4">
            <h2 className="text-lg font-bold text-white flex items-center gap-2 border-b border-white/10 pb-3">
              <Building2 className="w-5 h-5 text-brand-400" />
              Organization & Position
            </h2>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="label">Institution / Organization Name</label>
                <input
                  type="text"
                  value={profile.organization_name}
                  onChange={(e) => setProfile({ ...profile, organization_name: e.target.value })}
                  placeholder="e.g. Stanford University / MIT"
                  className="input"
                />
              </div>

              <div>
                <label className="label">Department / Unit</label>
                <input
                  type="text"
                  value={profile.department}
                  onChange={(e) => setProfile({ ...profile, department: e.target.value })}
                  placeholder="e.g. Dept. of Computer Science & AI"
                  className="input"
                />
              </div>

              <div>
                <label className="label">Organization Type</label>
                <select
                  value={profile.organization_type}
                  onChange={(e) => setProfile({ ...profile, organization_type: e.target.value })}
                  className="input bg-surface-900"
                >
                  {ORG_TYPES.map((o) => (
                    <option key={o.value} value={o.value}>
                      {o.label}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="label">Role / Designation</label>
                <input
                  type="text"
                  value={profile.position}
                  onChange={(e) => setProfile({ ...profile, position: e.target.value })}
                  placeholder="e.g. Principal Investigator / Senior Research Scientist"
                  className="input"
                />
              </div>
            </div>
          </div>

          {/* Academic & Metrics */}
          <div className="glass-card rounded-2xl p-6 space-y-4">
            <h2 className="text-lg font-bold text-white flex items-center gap-2 border-b border-white/10 pb-3">
              <GraduationCap className="w-5 h-5 text-accent-400" />
              Academic Credentials & Citation Metrics
            </h2>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="label">Highest Academic Degree</label>
                <input
                  type="text"
                  value={profile.academic_degree}
                  onChange={(e) => setProfile({ ...profile, academic_degree: e.target.value })}
                  placeholder="e.g. Ph.D."
                  className="input"
                />
              </div>

              <div>
                <label className="label">Field of Study</label>
                <input
                  type="text"
                  value={profile.field_of_study}
                  onChange={(e) => setProfile({ ...profile, field_of_study: e.target.value })}
                  placeholder="e.g. Computational Biology & AI"
                  className="input"
                />
              </div>

              <div>
                <label className="label">Degree Institution</label>
                <input
                  type="text"
                  value={profile.institution_name}
                  onChange={(e) => setProfile({ ...profile, institution_name: e.target.value })}
                  placeholder="e.g. Harvard University"
                  className="input"
                />
              </div>

              <div>
                <label className="label">Graduation Year</label>
                <input
                  type="number"
                  value={profile.graduation_year}
                  onChange={(e) => setProfile({ ...profile, graduation_year: e.target.value })}
                  placeholder="2020"
                  className="input"
                />
              </div>

              <div>
                <label className="label">h-index</label>
                <input
                  type="number"
                  min="0"
                  value={profile.h_index}
                  onChange={(e) => setProfile({ ...profile, h_index: e.target.value })}
                  className="input"
                />
              </div>

              <div>
                <label className="label">Total Citations</label>
                <input
                  type="number"
                  min="0"
                  value={profile.total_citations}
                  onChange={(e) => setProfile({ ...profile, total_citations: e.target.value })}
                  className="input"
                />
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-2">
              <div>
                <label className="label">ORCID iD</label>
                <input
                  type="text"
                  value={profile.orcid_id}
                  onChange={(e) => setProfile({ ...profile, orcid_id: e.target.value })}
                  placeholder="0000-0002-1825-0097"
                  className="input"
                />
              </div>

              <div>
                <label className="label">Google Scholar URL</label>
                <input
                  type="url"
                  value={profile.google_scholar_url}
                  onChange={(e) => setProfile({ ...profile, google_scholar_url: e.target.value })}
                  placeholder="https://scholar.google.com/citations?user=..."
                  className="input"
                />
              </div>

              <div>
                <label className="label">Scopus Author ID</label>
                <input
                  type="text"
                  value={profile.scopus_id}
                  onChange={(e) => setProfile({ ...profile, scopus_id: e.target.value })}
                  placeholder="57200000000"
                  className="input"
                />
              </div>
            </div>
          </div>

          {/* Research Domains, Keywords & Technology Interests */}
          <div className="glass-card rounded-2xl p-6 space-y-6">
            <h2 className="text-lg font-bold text-white flex items-center gap-2 border-b border-white/10 pb-3">
              <Tag className="w-5 h-5 text-green-400" />
              Research Domains, Keywords & Technology Focus
            </h2>

            {/* Research Domains Tag Input */}
            <div>
              <label className="label">Research Domains</label>
              <div className="flex gap-2 mb-3">
                <input
                  type="text"
                  value={domainInput}
                  onChange={(e) => setDomainInput(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter') {
                      e.preventDefault()
                      addTag('research_domains', domainInput, setDomainInput)
                    }
                  }}
                  placeholder="Add domain (e.g. Artificial Intelligence, Clean Energy) & press Enter"
                  className="input flex-1"
                />
                <button
                  type="button"
                  onClick={() => addTag('research_domains', domainInput, setDomainInput)}
                  className="btn-secondary px-4"
                >
                  Add
                </button>
              </div>
              <div className="flex flex-wrap gap-2">
                {profile.research_domains.map((domain) => (
                  <span
                    key={domain}
                    className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-brand-500/20 text-brand-300 text-xs font-semibold border border-brand-500/30"
                  >
                    {domain}
                    <button
                      type="button"
                      onClick={() => removeTag('research_domains', domain)}
                      className="hover:text-white"
                    >
                      <X className="w-3.5 h-3.5" />
                    </button>
                  </span>
                ))}
              </div>
            </div>

            {/* Keywords Tag Input */}
            <div>
              <label className="label">Keywords & Methodologies</label>
              <div className="flex gap-2 mb-3">
                <input
                  type="text"
                  value={keywordInput}
                  onChange={(e) => setKeywordInput(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter') {
                      e.preventDefault()
                      addTag('keywords', keywordInput, setKeywordInput)
                    }
                  }}
                  placeholder="Add keyword (e.g. Deep Learning, CRISPR, Microfluidics) & press Enter"
                  className="input flex-1"
                />
                <button
                  type="button"
                  onClick={() => addTag('keywords', keywordInput, setKeywordInput)}
                  className="btn-secondary px-4"
                >
                  Add
                </button>
              </div>
              <div className="flex flex-wrap gap-2">
                {profile.keywords.map((kw) => (
                  <span
                    key={kw}
                    className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-accent-500/20 text-accent-300 text-xs font-semibold border border-accent-500/30"
                  >
                    {kw}
                    <button
                      type="button"
                      onClick={() => removeTag('keywords', kw)}
                      className="hover:text-white"
                    >
                      <X className="w-3.5 h-3.5" />
                    </button>
                  </span>
                ))}
              </div>
            </div>

            {/* Technology Interests Tag Input */}
            <div>
              <label className="label">Technology Interests & TRL Focus</label>
              <div className="flex gap-2 mb-3">
                <input
                  type="text"
                  value={techInput}
                  onChange={(e) => setTechInput(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter') {
                      e.preventDefault()
                      addTag('technology_interests', techInput, setTechInput)
                    }
                  }}
                  placeholder="Add technology interest (e.g. Autonomous Robotics, Solid-state Batteries)"
                  className="input flex-1"
                />
                <button
                  type="button"
                  onClick={() => addTag('technology_interests', techInput, setTechInput)}
                  className="btn-secondary px-4"
                >
                  Add
                </button>
              </div>
              <div className="flex flex-wrap gap-2">
                {profile.technology_interests.map((tech) => (
                  <span
                    key={tech}
                    className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-green-500/20 text-green-300 text-xs font-semibold border border-green-500/30"
                  >
                    {tech}
                    <button
                      type="button"
                      onClick={() => removeTag('technology_interests', tech)}
                      className="hover:text-white"
                    >
                      <X className="w-3.5 h-3.5" />
                    </button>
                  </span>
                ))}
              </div>
            </div>

            {/* Bio Summary */}
            <div>
              <label className="label">Executive Research Summary / Bio</label>
              <textarea
                rows={4}
                value={profile.summary_bio}
                onChange={(e) => setProfile({ ...profile, summary_bio: e.target.value })}
                placeholder="Brief summary of research vision, lab capabilities, and target industry applications..."
                className="input"
              />
            </div>
          </div>

          <div className="flex justify-end">
            <button
              type="submit"
              disabled={saving}
              className="btn-primary px-8 py-3 flex items-center gap-2 text-base shadow-glow-brand"
            >
              {saving ? (
                <>
                  <div className="w-4 h-4 rounded-full border-2 border-white border-t-transparent animate-spin" />
                  Saving Profile...
                </>
              ) : (
                <>
                  <CheckCircle2 className="w-5 h-5" />
                  Save Changes
                </>
              )}
            </button>
          </div>
        </form>
      )}

      {/* ── TAB 2: Publications Manager ── */}
      {activeTab === 'publications' && (
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-xl font-bold text-white">Publications</h2>
              <p className="text-surface-400 text-sm">Manage peer-reviewed articles, conference papers, and book chapters.</p>
            </div>
            <button
              onClick={() => openPubModal()}
              className="btn-primary flex items-center gap-2"
            >
              <Plus className="w-4 h-4" />
              Add Publication
            </button>
          </div>

          {profile.publications.length === 0 ? (
            <div className="glass-card rounded-2xl p-12 text-center space-y-3">
              <BookOpen className="w-12 h-12 text-surface-500 mx-auto" />
              <p className="text-surface-300 font-medium">No publications added yet.</p>
              <button
                onClick={() => openPubModal()}
                className="btn-secondary text-xs px-4 py-2 inline-flex items-center gap-1.5"
              >
                <Plus className="w-4 h-4" /> Add your first publication
              </button>
            </div>
          ) : (
            <div className="grid grid-cols-1 gap-4">
              {profile.publications.map((pub) => (
                <div key={pub.id} className="glass-card rounded-xl p-5 space-y-3 relative group">
                  <div className="flex items-start justify-between gap-4">
                    <div className="space-y-1">
                      <h3 className="text-lg font-semibold text-white leading-snug">{pub.title}</h3>
                      <p className="text-xs text-surface-400">{pub.authors || 'Authors unspecified'}</p>
                    </div>

                    <div className="flex items-center gap-2">
                      <button
                        onClick={() => openPubModal(pub)}
                        className="p-2 rounded-lg hover:bg-white/10 text-surface-400 hover:text-brand-300 transition-colors"
                        title="Edit publication"
                      >
                        <Edit3 className="w-4 h-4" />
                      </button>
                      <button
                        onClick={() => handleDeletePublication(pub.id)}
                        className="p-2 rounded-lg hover:bg-red-500/10 text-surface-400 hover:text-red-400 transition-colors"
                        title="Delete publication"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </div>

                  <div className="flex flex-wrap items-center gap-3 text-xs text-surface-300">
                    {pub.venue && <span className="badge badge-brand">{pub.venue}</span>}
                    {pub.year && <span className="text-surface-400">Year: {pub.year}</span>}
                    {pub.citations_count > 0 && (
                      <span className="text-accent-400 font-semibold">
                        Citations: {pub.citations_count}
                      </span>
                    )}
                    {pub.doi && <span className="text-surface-400">DOI: {pub.doi}</span>}
                    {pub.url && (
                      <a
                        href={pub.url}
                        target="_blank"
                        rel="noreferrer"
                        className="inline-flex items-center gap-1 text-brand-400 hover:underline"
                      >
                        View Link <ExternalLink className="w-3 h-3" />
                      </a>
                    )}
                  </div>

                  {pub.abstract && (
                    <p className="text-xs text-surface-400 line-clamp-2 pt-1 border-t border-white/5">
                      {pub.abstract}
                    </p>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* ── TAB 3: Patents Manager ── */}
      {activeTab === 'patents' && (
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-xl font-bold text-white">Patents & Intellectual Property</h2>
              <p className="text-surface-400 text-sm">Showcase granted patents, patent filings, and utility models.</p>
            </div>
            <button
              onClick={() => openPatentModal()}
              className="btn-primary flex items-center gap-2"
            >
              <Plus className="w-4 h-4" />
              Add Patent
            </button>
          </div>

          {profile.patents.length === 0 ? (
            <div className="glass-card rounded-2xl p-12 text-center space-y-3">
              <Award className="w-12 h-12 text-surface-500 mx-auto" />
              <p className="text-surface-300 font-medium">No patents recorded.</p>
              <button
                onClick={() => openPatentModal()}
                className="btn-secondary text-xs px-4 py-2 inline-flex items-center gap-1.5"
              >
                <Plus className="w-4 h-4" /> Add your first patent
              </button>
            </div>
          ) : (
            <div className="grid grid-cols-1 gap-4">
              {profile.patents.map((pat) => (
                <div key={pat.id} className="glass-card rounded-xl p-5 space-y-3">
                  <div className="flex items-start justify-between gap-4">
                    <div className="space-y-1">
                      <div className="flex items-center gap-2">
                        <h3 className="text-lg font-semibold text-white">{pat.title}</h3>
                        <span className={clsx(
                          'badge text-[10px] uppercase font-bold',
                          pat.status === 'granted' && 'badge-green',
                          pat.status === 'pending' && 'badge-orange',
                          pat.status === 'filed' && 'badge-brand',
                          pat.status === 'expired' && 'bg-surface-800 text-surface-400'
                        )}>
                          {pat.status}
                        </span>
                      </div>
                      {pat.patent_number && (
                        <p className="text-xs text-brand-300 font-mono">Patent #: {pat.patent_number}</p>
                      )}
                    </div>

                    <div className="flex items-center gap-2">
                      <button
                        onClick={() => openPatentModal(pat)}
                        className="p-2 rounded-lg hover:bg-white/10 text-surface-400 hover:text-brand-300 transition-colors"
                      >
                        <Edit3 className="w-4 h-4" />
                      </button>
                      <button
                        onClick={() => handleDeletePatent(pat.id)}
                        className="p-2 rounded-lg hover:bg-red-500/10 text-surface-400 hover:text-red-400 transition-colors"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </div>

                  <div className="flex flex-wrap items-center gap-4 text-xs text-surface-400">
                    {pat.filing_date && <span>Filing Date: {pat.filing_date}</span>}
                    {pat.issue_date && <span>Issue Date: {pat.issue_date}</span>}
                    {pat.url && (
                      <a
                        href={pat.url}
                        target="_blank"
                        rel="noreferrer"
                        className="inline-flex items-center gap-1 text-brand-400 hover:underline"
                      >
                        Official Document <ExternalLink className="w-3 h-3" />
                      </a>
                    )}
                  </div>

                  {pat.abstract && (
                    <p className="text-xs text-surface-400 pt-1 border-t border-white/5">
                      {pat.abstract}
                    </p>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* ── TAB 4: Research History & Projects ── */}
      {activeTab === 'projects' && (
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-xl font-bold text-white">Research History & Funded Projects</h2>
              <p className="text-surface-400 text-sm">Track past and active funded research initiatives and lab projects.</p>
            </div>
            <button
              onClick={() => openProjectModal()}
              className="btn-primary flex items-center gap-2"
            >
              <Plus className="w-4 h-4" />
              Add Project
            </button>
          </div>

          {profile.projects.length === 0 ? (
            <div className="glass-card rounded-2xl p-12 text-center space-y-3">
              <History className="w-12 h-12 text-surface-500 mx-auto" />
              <p className="text-surface-300 font-medium">No research projects listed.</p>
              <button
                onClick={() => openProjectModal()}
                className="btn-secondary text-xs px-4 py-2 inline-flex items-center gap-1.5"
              >
                <Plus className="w-4 h-4" /> Add project history
              </button>
            </div>
          ) : (
            <div className="grid grid-cols-1 gap-4">
              {profile.projects.map((proj) => (
                <div key={proj.id} className="glass-card rounded-xl p-5 space-y-3">
                  <div className="flex items-start justify-between gap-4">
                    <div className="space-y-1">
                      <div className="flex items-center gap-2">
                        <h3 className="text-lg font-semibold text-white">{proj.title}</h3>
                        <span className={clsx(
                          'badge text-[10px] uppercase font-bold',
                          proj.status === 'ongoing' && 'badge-brand',
                          proj.status === 'completed' && 'badge-green',
                          proj.status === 'proposed' && 'badge-orange'
                        )}>
                          {proj.status}
                        </span>
                      </div>
                      <p className="text-xs text-surface-400">
                        {proj.role || 'Investigator'} {proj.sponsor_organization && `• Sponsored by ${proj.sponsor_organization}`}
                      </p>
                    </div>

                    <div className="flex items-center gap-2">
                      <button
                        onClick={() => openProjectModal(proj)}
                        className="p-2 rounded-lg hover:bg-white/10 text-surface-400 hover:text-brand-300 transition-colors"
                      >
                        <Edit3 className="w-4 h-4" />
                      </button>
                      <button
                        onClick={() => handleDeleteProject(proj.id)}
                        className="p-2 rounded-lg hover:bg-red-500/10 text-surface-400 hover:text-red-400 transition-colors"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </div>

                  <div className="flex flex-wrap items-center gap-4 text-xs text-surface-300">
                    {(proj.start_date || proj.end_date) && (
                      <span className="flex items-center gap-1">
                        <Calendar className="w-3.5 h-3.5 text-surface-500" />
                        {proj.start_date || 'N/A'} - {proj.end_date || 'Present'}
                      </span>
                    )}
                    {proj.funding_amount > 0 && (
                      <span className="flex items-center gap-1 text-green-400 font-semibold">
                        <DollarSign className="w-3.5 h-3.5" />
                        {proj.funding_amount.toLocaleString()} USD
                      </span>
                    )}
                  </div>

                  {proj.summary && (
                    <p className="text-xs text-surface-400 pt-1 border-t border-white/5">
                      {proj.summary}
                    </p>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* ── PUBLICATION MODAL ── */}
      {pubModalOpen && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="glass-card rounded-2xl max-w-lg w-full p-6 space-y-4 animate-scale-in">
            <div className="flex items-center justify-between border-b border-white/10 pb-3">
              <h3 className="text-lg font-bold text-white">
                {editingPub ? 'Edit Publication' : 'Add New Publication'}
              </h3>
              <button onClick={() => setPubModalOpen(false)} className="hover:text-white text-surface-400">
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleSavePublication} className="space-y-4">
              <div>
                <label className="label">Title *</label>
                <input
                  type="text"
                  required
                  value={pubForm.title}
                  onChange={(e) => setPubForm({ ...pubForm, title: e.target.value })}
                  className="input"
                  placeholder="Full title of article or paper"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="label">Journal / Venue</label>
                  <input
                    type="text"
                    value={pubForm.venue}
                    onChange={(e) => setPubForm({ ...pubForm, venue: e.target.value })}
                    className="input"
                    placeholder="e.g. Nature Machine Intelligence"
                  />
                </div>
                <div>
                  <label className="label">Publication Year</label>
                  <input
                    type="number"
                    value={pubForm.year}
                    onChange={(e) => setPubForm({ ...pubForm, year: e.target.value })}
                    className="input"
                    placeholder="2024"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="label">DOI</label>
                  <input
                    type="text"
                    value={pubForm.doi}
                    onChange={(e) => setPubForm({ ...pubForm, doi: e.target.value })}
                    className="input"
                    placeholder="10.1038/s41586-..."
                  />
                </div>
                <div>
                  <label className="label">Citations Count</label>
                  <input
                    type="number"
                    min="0"
                    value={pubForm.citations_count}
                    onChange={(e) => setPubForm({ ...pubForm, citations_count: e.target.value })}
                    className="input"
                  />
                </div>
              </div>

              <div>
                <label className="label">Authors List</label>
                <input
                  type="text"
                  value={pubForm.authors}
                  onChange={(e) => setPubForm({ ...pubForm, authors: e.target.value })}
                  className="input"
                  placeholder="e.g. Jane Doe, John Smith, et al."
                />
              </div>

              <div>
                <label className="label">URL</label>
                <input
                  type="url"
                  value={pubForm.url}
                  onChange={(e) => setPubForm({ ...pubForm, url: e.target.value })}
                  className="input"
                  placeholder="https://..."
                />
              </div>

              <div>
                <label className="label">Abstract</label>
                <textarea
                  rows={3}
                  value={pubForm.abstract}
                  onChange={(e) => setPubForm({ ...pubForm, abstract: e.target.value })}
                  className="input"
                  placeholder="Brief summary..."
                />
              </div>

              <div className="flex justify-end gap-3 pt-2">
                <button
                  type="button"
                  onClick={() => setPubModalOpen(false)}
                  className="btn-secondary px-4 py-2"
                >
                  Cancel
                </button>
                <button type="submit" className="btn-primary px-6 py-2">
                  Save Publication
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* ── PATENT MODAL ── */}
      {patentModalOpen && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="glass-card rounded-2xl max-w-lg w-full p-6 space-y-4 animate-scale-in">
            <div className="flex items-center justify-between border-b border-white/10 pb-3">
              <h3 className="text-lg font-bold text-white">
                {editingPatent ? 'Edit Patent' : 'Add New Patent'}
              </h3>
              <button onClick={() => setPatentModalOpen(false)} className="hover:text-white text-surface-400">
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleSavePatent} className="space-y-4">
              <div>
                <label className="label">Patent Title *</label>
                <input
                  type="text"
                  required
                  value={patentForm.title}
                  onChange={(e) => setPatentForm({ ...patentForm, title: e.target.value })}
                  className="input"
                  placeholder="Patent title or innovation name"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="label">Patent Number</label>
                  <input
                    type="text"
                    value={patentForm.patent_number}
                    onChange={(e) => setPatentForm({ ...patentForm, patent_number: e.target.value })}
                    className="input"
                    placeholder="US11234567B2"
                  />
                </div>
                <div>
                  <label className="label">Status</label>
                  <select
                    value={patentForm.status}
                    onChange={(e) => setPatentForm({ ...patentForm, status: e.target.value })}
                    className="input bg-surface-900"
                  >
                    {PATENT_STATUSES.map((s) => (
                      <option key={s.value} value={s.value}>{s.label}</option>
                    ))}
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="label">Filing Date</label>
                  <input
                    type="date"
                    value={patentForm.filing_date}
                    onChange={(e) => setPatentForm({ ...patentForm, filing_date: e.target.value })}
                    className="input"
                  />
                </div>
                <div>
                  <label className="label">Issue Date</label>
                  <input
                    type="date"
                    value={patentForm.issue_date}
                    onChange={(e) => setPatentForm({ ...patentForm, issue_date: e.target.value })}
                    className="input"
                  />
                </div>
              </div>

              <div>
                <label className="label">Document URL</label>
                <input
                  type="url"
                  value={patentForm.url}
                  onChange={(e) => setPatentForm({ ...patentForm, url: e.target.value })}
                  className="input"
                  placeholder="https://patents.google.com/patent/..."
                />
              </div>

              <div>
                <label className="label">Patent Abstract</label>
                <textarea
                  rows={3}
                  value={patentForm.abstract}
                  onChange={(e) => setPatentForm({ ...patentForm, abstract: e.target.value })}
                  className="input"
                  placeholder="Summary of claims..."
                />
              </div>

              <div className="flex justify-end gap-3 pt-2">
                <button
                  type="button"
                  onClick={() => setPatentModalOpen(false)}
                  className="btn-secondary px-4 py-2"
                >
                  Cancel
                </button>
                <button type="submit" className="btn-primary px-6 py-2">
                  Save Patent
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* ── PROJECT MODAL ── */}
      {projectModalOpen && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="glass-card rounded-2xl max-w-lg w-full p-6 space-y-4 animate-scale-in">
            <div className="flex items-center justify-between border-b border-white/10 pb-3">
              <h3 className="text-lg font-bold text-white">
                {editingProject ? 'Edit Research Project' : 'Add Research Project'}
              </h3>
              <button onClick={() => setProjectModalOpen(false)} className="hover:text-white text-surface-400">
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleSaveProject} className="space-y-4">
              <div>
                <label className="label">Project Title *</label>
                <input
                  type="text"
                  required
                  value={projectForm.title}
                  onChange={(e) => setProjectForm({ ...projectForm, title: e.target.value })}
                  className="input"
                  placeholder="Research initiative title"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="label">Your Role</label>
                  <input
                    type="text"
                    value={projectForm.role}
                    onChange={(e) => setProjectForm({ ...projectForm, role: e.target.value })}
                    className="input"
                    placeholder="Principal Investigator / Lead"
                  />
                </div>
                <div>
                  <label className="label">Status</label>
                  <select
                    value={projectForm.status}
                    onChange={(e) => setProjectForm({ ...projectForm, status: e.target.value })}
                    className="input bg-surface-900"
                  >
                    {PROJECT_STATUSES.map((s) => (
                      <option key={s.value} value={s.value}>{s.label}</option>
                    ))}
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="label">Sponsor / Funding Body</label>
                  <input
                    type="text"
                    value={projectForm.sponsor_organization}
                    onChange={(e) => setProjectForm({ ...projectForm, sponsor_organization: e.target.value })}
                    className="input"
                    placeholder="e.g. NSF / Horizon Europe / NIH"
                  />
                </div>
                <div>
                  <label className="label">Funding Amount ($)</label>
                  <input
                    type="number"
                    min="0"
                    step="1000"
                    value={projectForm.funding_amount}
                    onChange={(e) => setProjectForm({ ...projectForm, funding_amount: e.target.value })}
                    className="input"
                    placeholder="500000"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="label">Start Date</label>
                  <input
                    type="date"
                    value={projectForm.start_date}
                    onChange={(e) => setProjectForm({ ...projectForm, start_date: e.target.value })}
                    className="input"
                  />
                </div>
                <div>
                  <label className="label">End Date</label>
                  <input
                    type="date"
                    value={projectForm.end_date}
                    onChange={(e) => setProjectForm({ ...projectForm, end_date: e.target.value })}
                    className="input"
                  />
                </div>
              </div>

              <div>
                <label className="label">Project Summary</label>
                <textarea
                  rows={3}
                  value={projectForm.summary}
                  onChange={(e) => setProjectForm({ ...projectForm, summary: e.target.value })}
                  className="input"
                  placeholder="Summary of research objectives..."
                />
              </div>

              <div className="flex justify-end gap-3 pt-2">
                <button
                  type="button"
                  onClick={() => setProjectModalOpen(false)}
                  className="btn-secondary px-4 py-2"
                >
                  Cancel
                </button>
                <button type="submit" className="btn-primary px-6 py-2">
                  Save Project
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
