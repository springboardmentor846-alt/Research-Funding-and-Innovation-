import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { Bookmark, Building, DollarSign, Calendar, Trash2, ArrowRight } from 'lucide-react'
import toast from 'react-hot-toast'
import { fundingService } from '@/services/fundingService'

export default function MyBookmarksPage() {
  const [bookmarks, setBookmarks] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadBookmarks()
  }, [])

  const loadBookmarks = async () => {
    try {
      setLoading(true)
      const res = await fundingService.getMyBookmarks()
      setBookmarks(res)
    } catch (err) {
      toast.error('Failed to load saved bookmarks')
    } finally {
      setLoading(false)
    }
  }

  const handleRemoveBookmark = async (oppId) => {
    try {
      await fundingService.toggleBookmark(oppId)
      toast.success('Bookmark removed')
      setBookmarks((prev) => prev.filter((b) => b.id !== oppId))
    } catch (err) {
      toast.error('Failed to remove bookmark')
    }
  }

  return (
    <div className="max-w-7xl mx-auto space-y-8">
      <div>
        <h1 className="text-2xl md:text-3xl font-extrabold text-white">
          My Saved Grants & Bookmarks
        </h1>
        <p className="text-surface-400 text-sm mt-1">
          Your personal library of bookmarked funding opportunities and research awards.
        </p>
      </div>

      {loading ? (
        <div className="flex items-center justify-center min-h-[300px]">
          <div className="w-10 h-10 border-4 border-brand-500 border-t-transparent rounded-full animate-spin" />
        </div>
      ) : bookmarks.length === 0 ? (
        <div className="glass p-12 text-center space-y-4 max-w-lg mx-auto">
          <Bookmark className="w-12 h-12 text-surface-500 mx-auto" />
          <h3 className="text-lg font-bold text-white">No saved grants yet</h3>
          <p className="text-surface-400 text-sm">
            Save funding opportunities while searching to track application deadlines and funder criteria.
          </p>
          <Link to="/funding/search" className="btn-primary inline-flex text-xs">
            Explore Funding Opportunities <ArrowRight className="w-3.5 h-3.5 ml-1" />
          </Link>
        </div>
      ) : (
        <div className="grid md:grid-cols-3 gap-5">
          {bookmarks.map((opp) => (
            <div key={opp.id} className="glass p-5 flex flex-col justify-between hover:border-brand-500/40 transition-all">
              <div className="space-y-3">
                <div className="flex items-start justify-between gap-3">
                  <span className="badge badge-brand text-xs">{opp.funding_type}</span>
                  <button
                    onClick={() => handleRemoveBookmark(opp.id)}
                    className="p-2 rounded-lg bg-red-500/10 text-red-400 hover:bg-red-500/20 transition-colors"
                    title="Remove Bookmark"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>

                <Link to={`/funding/${opp.id}`} className="block group">
                  <h3 className="text-base font-bold text-white group-hover:text-brand-300 transition-colors line-clamp-2">
                    {opp.title}
                  </h3>
                </Link>

                <div className="flex items-center gap-3 text-xs text-surface-400">
                  <span className="flex items-center gap-1">
                    <Building className="w-3.5 h-3.5 text-surface-500" /> {opp.funder_name}
                  </span>
                </div>

                <div className="flex items-center gap-3 text-xs font-semibold text-accent-400">
                  <DollarSign className="w-4 h-4" />
                  {opp.amount_max ? `$${(opp.amount_max / 1000).toFixed(0)}K ${opp.currency}` : 'Varies'}
                </div>

                <p className="text-xs text-surface-300 line-clamp-2">{opp.description}</p>
              </div>

              <div className="mt-4 pt-3 border-t border-white/5 flex items-center justify-between text-xs text-surface-400">
                <span className="flex items-center gap-1">
                  <Calendar className="w-3.5 h-3.5" />
                  {opp.deadline ? new Date(opp.deadline).toLocaleDateString() : 'Rolling'}
                </span>
                <Link to={`/funding/${opp.id}`} className="text-brand-400 font-semibold hover:underline">
                  View Details →
                </Link>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
