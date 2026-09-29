import { useEffect, useState } from "react"
import Modal from "./Modal"
import { BatchAgentDataPanes } from "./BatchAgentDataModal"
import BatchLogViewer, { type LogEntry } from "./BatchLogViewer"
import api from "../lib/api"

interface Props {
  runId: string | null
  onClose: () => void
}

/** One run's agent prompt panes + log table, as Execution History shows them (AST-1865). Stacks over the job modal. */
export default function BatchExecutionModal({ runId, onClose }: Props) {
  // Logs keyed by the run they were fetched for: loading is derived (no sync setState in the effect),
  // and a late response for a previous run never shows under the current one.
  const [fetched, setFetched] = useState<{ runId: string; logs: LogEntry[] } | null>(null)
  const loading = fetched?.runId !== runId
  const logs = !loading && fetched ? fetched.logs : []

  useEffect(() => {
    // Closed modal makes no admin requests (AST-1865 AC5)
    if (!runId) return
    api(`/api/admin/dispatch_ledger/${encodeURIComponent(runId)}/logs`)
      .then(r => r.json())
      .then(data => setFetched({ runId, logs: Array.isArray(data) ? data : [] }))
      .catch(() => setFetched({ runId, logs: [] }))
  }, [runId])

  return (
    <Modal open={!!runId} onClose={onClose} title={runId ?? ""} size="wide" stacked showFooter={false}>
      {runId ? (
        <>
          <BatchAgentDataPanes batchId={runId} />
          <BatchLogViewer logs={logs} loading={loading} />
        </>
      ) : null}
    </Modal>
  )
}
