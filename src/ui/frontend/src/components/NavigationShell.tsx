import { useEffect, useState } from "react"
import { NavLink, Outlet } from "react-router-dom"
import { UserPromptProvider } from "./UserPrompt"
import { useAuth } from "../contexts/AuthContext"
import { useCandidate } from "../contexts/CandidateContext"
import api from "../lib/api"
import astralLogo from "../assets/astral_logo.png"

interface NavItem { label: string; path: string; enabled: boolean; count?: number }
interface NavGroup { label: string; items: NavItem[] }

const NAV_STORAGE_KEY = "nav:expanded"

function loadExpanded(): Set<string> {
  try {
    const raw = localStorage.getItem(NAV_STORAGE_KEY)
    return raw ? new Set(JSON.parse(raw)) : new Set()
  } catch { return new Set() }
}

function saveExpanded(expanded: Set<string>) {
  try {
    localStorage.setItem(NAV_STORAGE_KEY, JSON.stringify([...expanded]))
  } catch { /* quota */ }
}

export default function NavigationShell() {
  const [navGroups, setNavGroups] = useState<NavGroup[]>([])
  // Store which groups are EXPANDED (default: all collapsed)
  const [expanded, setExpanded] = useState<Set<string>>(loadExpanded)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(false)
  const { isAdmin } = useAuth()
  const { candidates, selectedId, setSelectedId } = useCandidate()

  useEffect(() => {
    const params = selectedId ? `?candidate_id=${encodeURIComponent(selectedId)}` : ""
    const fetchNav = () =>
      api(`/api/nav_config${params}`)
        .then(r => {
          if (!r.ok) throw new Error(`${r.status}`)
          return r.json()
        })
        .then(data => {
          setNavGroups(data)
          setLoading(false)
          setError(false)
        })
        .catch(() => {
          setLoading(false)
          setError(true)
        })
    fetchNav()
    const interval = setInterval(fetchNav, 30_000)
    return () => clearInterval(interval)
  }, [selectedId])

  function toggleGroup(label: string) {
    setExpanded(prev => {
      const next = new Set(prev)
      if (next.has(label)) next.delete(label)
      else next.add(label)
      saveExpanded(next)
      return next
    })
  }

  return (
    <UserPromptProvider>
    <div className="shell">
      <nav className="sidebar">
        <div className="sidebar-logo">
          <img src={astralLogo} alt="Astral" />
        </div>
        {candidates.length > 0 && (
          <div className="sidebar-candidate-select">
            <select
              value={selectedId ?? ""}
              disabled={!isAdmin}
              onChange={e => isAdmin && setSelectedId(e.target.value)}
            >
              {candidates.map(c => {
                const cd = c.candidate_data || {}
                const label = [cd.first, cd.last].filter(Boolean).join(" ") || c.astral_candidate_id
                return <option key={c.astral_candidate_id} value={c.astral_candidate_id}>{label}</option>
              })}
            </select>
          </div>
        )}
        {loading ? (
          <p className="sidebar-loading">Loading...</p>
        ) : error ? (
          <p className="sidebar-error">Failed to load navigation. Check server connection.</p>
        ) : (
          navGroups.map(group => {
            const isExpanded = expanded.has(group.label)
            return (
              <div key={group.label} className="nav-group">
                <h3
                  className="nav-group-label"
                  onClick={() => toggleGroup(group.label)}
                >
                  <span className={`nav-group-chevron${isExpanded ? "" : " collapsed"}`}>▾</span>
                  {group.label}
                </h3>
                {isExpanded && group.items.map(item => {
                  const badge = item.count != null
                    ? <span style={{ marginLeft: 6, fontSize: 11, color: "#888", fontWeight: 400 }}>[{item.count}]</span>
                    : null
                  return item.enabled ? (
                    <NavLink
                      key={item.path}
                      to={item.path}
                      className={({ isActive }) => "nav-link" + (isActive ? " active" : "")}
                    >
                      {item.label}{badge}
                    </NavLink>
                  ) : (
                    <span key={item.path} className="nav-link disabled">
                      {item.label}{badge}
                    </span>
                  )
                })}
              </div>
            )
          })
        )}
        <span className="nav-footer-spacer" />
      </nav>
      <main className="content">
        <Outlet />
      </main>
    </div>
    </UserPromptProvider>
  )
}
