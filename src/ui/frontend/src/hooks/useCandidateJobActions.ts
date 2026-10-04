import { useCallback, useState } from "react"
import {
  postCandidateAction,
  postGenerateArtifacts,
  postSkipJob,
  type CandidateActionKey,
} from "../lib/candidateJobActions"

/** Bulk outcome reported to the page for its toast (AST-1968). */
export interface BulkActionResult {
  label: string
  succeeded: number
  failed: number
}

// `jobId` stays (= jobIds[0]) because JobsApplied reads pending.jobId directly.
interface PendingAction {
  jobId: string
  jobIds: string[]
  action: CandidateActionKey
  bulk: boolean
  label: string
}

// One POST per job, in order; a failure is counted, never thrown, so the rest still run.
async function runPerJob(jobIds: string[], post: (id: string) => Promise<void>) {
  let succeeded = 0
  for (const id of jobIds) {
    try {
      await post(id)
      succeeded += 1
    } catch {
      // counted as failed below
    }
  }
  return { succeeded, failed: jobIds.length - succeeded }
}

/** AST-312: shared skip / candidate_action flow for job list pages. AST-1968: generate + bulk. */
export function useCandidateJobActions(
  onRefresh: () => void,
  onBulkDone?: (result: BulkActionResult) => void,
) {
  const [pending, setPending] = useState<PendingAction | null>(null)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const clearError = useCallback(() => setError(null), [])

  // Single-job flow: surfaces the server error via `error` (page toasts it).
  const runSingle = useCallback(async (
    jobId: string,
    post: (id: string) => Promise<void>,
    fallback: string,
  ) => {
    setBusy(true)
    setError(null)
    try {
      await post(jobId)
      onRefresh()
    } catch (e) {
      setError(e instanceof Error ? e.message : fallback)
    } finally {
      setBusy(false)
    }
  }, [onRefresh])

  // Bulk flow: never sets `error`; counts go to onBulkDone so the page shows one toast.
  const runBulk = useCallback(async (
    label: string,
    jobIds: string[],
    post: (id: string) => Promise<void>,
  ) => {
    setBusy(true)
    setError(null)
    try {
      const counts = await runPerJob(jobIds, post)
      onRefresh()
      onBulkDone?.({ label, ...counts })
    } finally {
      setBusy(false)
    }
  }, [onRefresh, onBulkDone])

  const skipJob = useCallback(
    (jobId: string) => runSingle(jobId, postSkipJob, "Skip failed"),
    [runSingle],
  )

  const generateJob = useCallback(
    (jobId: string) => runSingle(jobId, postGenerateArtifacts, "Generate failed"),
    [runSingle],
  )

  const skipJobs = useCallback(
    (jobIds: string[]) => runBulk("Skip", jobIds, postSkipJob),
    [runBulk],
  )

  const generateJobs = useCallback(
    (jobIds: string[]) => runBulk("Generate Artifacts", jobIds, postGenerateArtifacts),
    [runBulk],
  )

  const requestAction = useCallback((jobId: string, action: CandidateActionKey) => {
    setPending({ jobId, jobIds: [jobId], action, bulk: false, label: "" })
  }, [])

  // One notes modal for many jobs; confirm applies the same note to each.
  const requestBulkAction = useCallback((jobIds: string[], action: CandidateActionKey, label: string) => {
    if (!jobIds.length) return
    setPending({ jobId: jobIds[0], jobIds, action, bulk: true, label })
  }, [])

  const confirmPending = useCallback(async (notes: string) => {
    if (!pending || busy) return
    if (pending.bulk) {
      const { action, jobIds, label } = pending
      await runBulk(label, jobIds, id => postCandidateAction(id, action, notes))
      setPending(null)
      return
    }
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
  }, [pending, busy, onRefresh, runBulk])

  return {
    pending,
    busy,
    error,
    clearError,
    skipJob,
    generateJob,
    skipJobs,
    generateJobs,
    requestAction,
    requestBulkAction,
    confirmPending,
    closePending: () => setPending(null),
  }
}
