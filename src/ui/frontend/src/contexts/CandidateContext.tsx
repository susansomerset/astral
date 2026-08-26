import { createContext, useCallback, useContext, useEffect, useRef, useState, type ReactNode } from "react"
import api from "../lib/api"
import { setFmtTimezone } from "../lib/fmt"
import { browserTabTitle } from "../lib/documentTitle"
import { useAuth } from "./AuthContext"

export interface CandidateInfo {
  astral_candidate_id: string
  state: string
  candidate_data: Record<string, unknown>
  first?: string
  last?: string
  full?: string
  pronouns?: string
}

interface CandidateCtx {
  candidates: CandidateInfo[]
  selectedId: string | null
  setSelectedId: (id: string) => void
  refresh: () => void
  candidatesHydrated: boolean
  alignSelectedCandidateForJobCompany: (companyShortName: string) => Promise<void>
}

const CandidateContext = createContext<CandidateCtx>({
  candidates: [], selectedId: null,
  setSelectedId: () => {}, refresh: () => {},
  candidatesHydrated: false,
  alignSelectedCandidateForJobCompany: async () => {},
})

const STORAGE_KEY = "astral_selected_candidate"

export function CandidateProvider({ children }: { children: ReactNode }) {
  const { isAdmin, loading: authLoading } = useAuth()
  const [candidates, setCandidates] = useState<CandidateInfo[]>([])
  const [candidatesHydrated, setCandidatesHydrated] = useState(false)
  const [selectedId, _setSelectedId] = useState<string | null>(
    () => localStorage.getItem(STORAGE_KEY)
  )
  const candidatesRef = useRef(candidates)
  candidatesRef.current = candidates
  const selectedIdRef = useRef(selectedId)
  selectedIdRef.current = selectedId

  const setSelectedId = useCallback((id: string) => {
    if (!isAdmin) return
    _setSelectedId(id)
    localStorage.setItem(STORAGE_KEY, id)
  }, [isAdmin])

  const alignSelectedCandidateForJobCompany = useCallback(async (companyShortName: string) => {
    if (!isAdmin) return
    const sn = companyShortName.trim()
    if (!sn) return
    const res = await api(`/api/companies/${encodeURIComponent(sn)}`)
    if (!res.ok) return
    const data = (await res.json()) as { candidate_id?: unknown }
    const cid = typeof data.candidate_id === "string" ? data.candidate_id.trim() : ""
    if (!cid || cid === selectedIdRef.current) return
    if (!candidatesRef.current.some(c => c.astral_candidate_id === cid)) return
    setSelectedId(cid)
  }, [isAdmin, setSelectedId])

  function load() {
    setCandidatesHydrated(false)
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
      .finally(() => setCandidatesHydrated(true))
  }

  // Wait until AuthContext has wired the bearer token (and finished /api/me).
  useEffect(() => {
    if (authLoading) return
    load()
  }, [authLoading])

  // Keep fmtTime's timezone in sync with the selected candidate
  useEffect(() => {
    const c = candidates.find(x => x.astral_candidate_id === selectedId)
    const contact = c?.candidate_data?.contact as Record<string, string> | undefined
    setFmtTimezone(contact?.timezone || "UTC")
  }, [selectedId, candidates])

  useEffect(() => {
    const selected = candidates.find(c => c.astral_candidate_id === selectedId)
    document.title = browserTabTitle(selected?.full)
  }, [selectedId, candidates])

  useEffect(() => {
    return () => {
      document.title = browserTabTitle(undefined)
    }
  }, [])

  return (
    <CandidateContext.Provider value={{
      candidates, selectedId, setSelectedId, refresh: load,
      candidatesHydrated, alignSelectedCandidateForJobCompany,
    }}>
      {children}
    </CandidateContext.Provider>
  )
}

// eslint-disable-next-line react-refresh/only-export-components
export function useCandidate(): CandidateCtx {
  return useContext(CandidateContext)
}
