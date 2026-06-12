import { useState } from "react"
import Modal from "./Modal"
import type { CandidateActionKey } from "../lib/candidateJobActions"

const LABELS: Record<CandidateActionKey, string> = {
  applied: "Applied",
  interview: "Interview",
  rejected: "Rejected",
  ghosted: "Ghosted",
  review: "Return to review",
}

interface Props {
  open: boolean
  action: CandidateActionKey | null
  busy?: boolean
  onClose: () => void
  onConfirm: (notes: string) => void
}

/** AST-312: optional notes before candidate_action POST. */
export default function CandidateActionNotesModal({ open, action, busy, onClose, onConfirm }: Props) {
  const [notes, setNotes] = useState("")
  if (!action) return null
  const title = LABELS[action]

  function handleClose() {
    setNotes("")
    onClose()
  }

  function handleSave() {
    onConfirm(notes)
    setNotes("")
  }

  return (
    <Modal open={open} onClose={handleClose} title={title} onSave={handleSave} stacked>
      <p style={{ fontSize: 13, color: "var(--text-secondary)", marginBottom: 8 }}>
        Optional notes (saved with this action):
      </p>
      <textarea
        className="dep-input"
        rows={4}
        value={notes}
        onChange={e => setNotes(e.target.value)}
        disabled={busy}
        placeholder="Notes…"
      />
      {busy && <p className="entity-loading" style={{ marginTop: 8 }}>Saving…</p>}
    </Modal>
  )
}
