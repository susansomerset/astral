import { useCallback, useState } from "react"
import {
  postCandidateAction,
  postSkipJob,
  type CandidateActionKey,
} from "../lib/candidateJobActions"

/** AST-312: shared skip / candidate_action flow for job list pages. */
export function useCandidateJobActions(onRefresh: () => void) {
  const [pending, setPending] = useState<{ jobId: string; action: CandidateActionKey } | null>(null)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const clearError = useCallback(() => setError(null), [])

  const skipJob = useCallback(async (jobId: string) => {
    setBusy(true)
    setError(null)
    try {
      await postSkipJob(jobId)
      onRefresh()
    } catch (e) {
      setError(e instanceof Error ? e.message : "Skip failed")
    } finally {
      setBusy(false)
    }
  }, [onRefresh])

  const requestAction = useCallback((jobId: string, action: CandidateActionKey) => {
    setPending({ jobId, action })
  }, [])

  const confirmPending = useCallback(async (notes: string) => {
    if (!pending || busy) return
    setBusy(true)
    setError(null)
    try {
      await postCandidateAction(pending.jobId, pending.action, notes)
      setPending(null)
      onRefresh()
    } catch (e) {
      setError(e instanceof Error ? e.message : "Action failed")
    } finally {
      setBusy(false)
    }
  }, [pending, busy, onRefresh])

  return {
    pending,
    busy,
    error,
    clearError,
    skipJob,
    requestAction,
    confirmPending,
    closePending: () => setPending(null),
  }
}
