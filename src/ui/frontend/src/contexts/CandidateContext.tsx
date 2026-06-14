import { createContext, useContext, useEffect, useState, type ReactNode } from "react"
import api from "../lib/api"
import { setFmtTimezone } from "../lib/fmt"
import { useAuth } from "./AuthContext"

interface CandidateInfo {
  astral_candidate_id: string
  state: string
  candidate_data: Record<string, unknown>
}

interface CandidateCtx {
  candidates: CandidateInfo[]
  selectedId: string | null
  setSelectedId: (id: string) => void
  refresh: () => void
}

const CandidateContext = createContext<CandidateCtx>({
  candidates: [], selectedId: null,
  setSelectedId: () => {}, refresh: () => {},
})

const STORAGE_KEY = "astral_selected_candidate"

export function CandidateProvider({ children }: { children: ReactNode }) {
  const { isAdmin, loading: authLoading } = useAuth()
  const [candidates, setCandidates] = useState<CandidateInfo[]>([])
  const [selectedId, _setSelectedId] = useState<string | null>(
    () => localStorage.getItem(STORAGE_KEY)
  )

  function setSelectedId(id: string) {
    if (!isAdmin) return
    _setSelectedId(id)
    localStorage.setItem(STORAGE_KEY, id)
  }

  function load() {
    api("/api/candidates").then(r => r.json()).then(data => {
      const list: CandidateInfo[] = Array.isArray(data) ? data : []
      setCandidates(list)
      if (list.length > 0) {
        _setSelectedId(prev => {
          const kept = prev && list.some(c => c.astral_candidate_id === prev)
          const next = kept ? prev : list[0].astral_candidate_id
          localStorage.setItem(STORAGE_KEY, next!)
          return next
        })
      }
    }).catch(() => setCandidates([]))
  }

  // Wait until AuthContext has wired the bearer token (and finished /api/me).
  useEffect(() => {
    if (authLoading) return
    load()
  }, [authLoading])

  // Keep fmtTime's timezone in sync with the selected candidate
  useEffect(() => {
    const c = candidates.find(x => x.astral_candidate_id === selectedId)
    const profile = c?.candidate_data?.profile as Record<string, string> | undefined
    setFmtTimezone(profile?.timezone || "UTC")
  }, [selectedId, candidates])

  return (
    <CandidateContext.Provider value={{ candidates, selectedId, setSelectedId, refresh: load }}>
      {children}
    </CandidateContext.Provider>
  )
}

// eslint-disable-next-line react-refresh/only-export-components
export function useCandidate(): CandidateCtx {
  return useContext(CandidateContext)
}
