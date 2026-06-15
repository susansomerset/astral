import { useCallback, useEffect, useRef, useState } from "react"
import { useCandidate } from "../contexts/CandidateContext"
import { sortCandidatesForSelect } from "../lib/candidateLabel"

export type AdminCandidateFilterValue = "" | string

type UrlBacked = {
  value: AdminCandidateFilterValue
  setValue: (next: AdminCandidateFilterValue) => void
}

type Options = {
  urlBacked?: UrlBacked
  /** When true on first mount, existing URL value disables nav sync (explicit bookmark). */
  urlPresentDisablesSync?: boolean
}

export function navDefaultCandidateFilter(selectedId: string | null): AdminCandidateFilterValue {
  return selectedId ?? ""
}

export function useAdminCandidateFilter(options?: Options) {
  const { candidates, selectedId } = useCandidate()
  const urlBacked = options?.urlBacked

  const [syncWithNav, setSyncWithNav] = useState(() => {
    if (urlBacked && options?.urlPresentDisablesSync && urlBacked.value) return false
    return true
  })
  const manualPinRef = useRef(false)

  const [localFilter, setLocalFilter] = useState<AdminCandidateFilterValue>(() =>
    navDefaultCandidateFilter(selectedId),
  )

  const candidateFilter = urlBacked ? urlBacked.value : localFilter

  const applyFilter = useCallback(
    (next: AdminCandidateFilterValue) => {
      if (urlBacked) urlBacked.setValue(next)
      else setLocalFilter(next)
    },
    [urlBacked],
  )

  const setCandidateFilter = useCallback(
    (next: AdminCandidateFilterValue) => {
      manualPinRef.current = true
      setSyncWithNav(false)
      applyFilter(next)
    },
    [applyFilter],
  )

  useEffect(() => {
    if (!syncWithNav || manualPinRef.current) return
    applyFilter(navDefaultCandidateFilter(selectedId))
  }, [selectedId, syncWithNav, applyFilter])

  return {
    candidateFilter,
    setCandidateFilter,
    syncWithNav,
    candidates: sortCandidatesForSelect(candidates),
  }
}
