import { useEffect, useState } from "react"
import { Navigate } from "react-router-dom"
import { useCandidate } from "../contexts/CandidateContext"
import api from "../lib/api"

interface NavItem { path: string; count?: number }
interface NavGroup { label: string; items: NavItem[] }

// NAV_CONFIG group label in src/utils/config.py — the Jobs items, in nav order.
const JOBS_NAV_GROUP_LABEL = "Jobs"

/**
 * AST-1975: the only place the landing page is chosen. First Jobs nav item with
 * count > 0, else the first Jobs item. Serves `/`, the catch-all, and every former
 * `/jobs/recommended` target (they navigate to `/`).
 */
export default function JobsHomeRedirect() {
  const { selectedId, candidatesHydrated } = useCandidate()
  const [target, setTarget] = useState<string | null>(null)
  const [failed, setFailed] = useState(false)

  useEffect(() => {
    // Wait for the candidate bind — counts before it would be for the wrong (or no) candidate.
    if (!candidatesHydrated) return
    let cancelled = false
    const params = selectedId ? `?candidate_id=${encodeURIComponent(selectedId)}` : ""
    api(`/api/nav_config${params}`)
      .then(r => { if (!r.ok) throw new Error(String(r.status)); return r.json() })
      .then((groups: NavGroup[]) => {
        if (cancelled) return
        const items = groups.find(g => g.label === JOBS_NAV_GROUP_LABEL)?.items ?? []
        const pick = items.find(i => (i.count ?? 0) > 0) ?? items[0]
        if (pick) setTarget(pick.path)
        else setFailed(true)
      })
      .catch(() => { if (!cancelled) setFailed(true) })
    return () => { cancelled = true }
  }, [candidatesHydrated, selectedId])

  if (target) return <Navigate to={target} replace />
  return (
    <div className="page-container">
      <p className="list-page-status">{failed ? "Navigation unavailable." : "Loading…"}</p>
    </div>
  )
}
